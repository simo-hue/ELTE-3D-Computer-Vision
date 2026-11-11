import math
from colorsys import hsv_to_rgb

import numpy as np


MAX_PLANES = 4
PLANE_TOLERANCE_MM = 6.0
MIN_PLANE_FRACTION = 0.03
RANSAC_TRIALS = 350
RANDOM_SEED = 42
SPHERE_TRIALS = 800
SPHERE_TOLERANCE_MM = 5.0


def read_pcd(file_path):
    """Read the x, y, z coordinates from an ASCII PCD file."""
    fields = []     # Column names from the FIELDS line, e.g. x y z rgb intensity.
    counts = []     # Number of values per field from the COUNT line (normally 1 each).
    columns = None  # Positions of x, y, z in a data row; set when the header ends.
    rows = []

    with open(file_path, "r") as file:
        for line in file:
            tokens = line.split()

            # Skip empty lines and comment lines.
            if not tokens or tokens[0].startswith("#"):
                continue

            # Data rows: keep only the x, y, z values and ignore every other field.
            if columns is not None:
                rows.append([float(tokens[i]) for i in columns])
                continue

            # Header lines: remember the ones needed to locate x, y and z.
            keyword = tokens[0].upper()

            if keyword == "FIELDS":
                fields = tokens[1:]

            elif keyword == "COUNT":
                counts = [int(value) for value in tokens[1:]]

            elif keyword == "DATA":
                # DATA is the last header line; the points start on the next line.
                if len(tokens) < 2 or tokens[1].lower() != "ascii":
                    raise ValueError("Only ASCII PCD files are supported.")

                if not all(axis in fields for axis in ("x", "y", "z")):
                    raise ValueError("The PCD file must contain the fields x, y and z.")

                if not counts:
                    counts = [1] * len(fields)

                # A field starts after all the values of the fields before it.
                columns = [sum(counts[:fields.index(axis)]) for axis in ("x", "y", "z")]

    if columns is None:
        raise ValueError("No DATA line found: this is not a valid PCD file.")

    points = np.array(rows, dtype=np.float64).reshape(-1, 3)

    # Drop invalid measurements: NaN/inf values and points without depth (z <= 0).
    valid = np.isfinite(points).all(axis=1) & (points[:, 2] > 0)

    return points[valid]


def refit_plane(inliers):
    center = inliers.mean(axis=0)
    centered = inliers - center
    _, axes = np.linalg.eigh(centered.T @ centered)
    normal = axes[:, 0]  # Normal is the least-spread direction.

    return normal, normal @ center


def estimate_surface_noise(points):
    """Estimate a noise scale from small local patches."""
    rng = np.random.default_rng(RANDOM_SEED)
    sample = points[rng.choice(len(points), min(len(points), 10000), replace=False)]

    if len(sample) < 4:
        raise ValueError("At least four valid points are required.")

    scales = []

    for anchor in sample[rng.choice(len(sample), min(64, len(sample)), replace=False)]:
        distances = np.sum((sample - anchor) ** 2, axis=1)
        k = min(40, len(sample))

        patch = sample[np.argpartition(distances, k - 1)[:k]]
        normal, offset = refit_plane(patch)
        residuals = patch @ normal - offset

        # Calculate the Mean Absolute Deviation
        mad = np.median(np.abs(residuals - np.median(residuals)))
        scales.append(1.4826 * mad)

    precision = np.finfo(float).eps * max(1.0, np.max(np.abs(sample))) * 32

    return max(np.median(scales), precision)


def find_plane(cloud, tolerance_mm, trials, rng):
    """Find the sampled plane with the most inliers."""
    best_plane = None
    best_mask = np.zeros(len(cloud), dtype=bool)
    best_count = 0

    for _ in range(trials):

        # Select the 3 points
        a, b, c = cloud[rng.choice(len(cloud), size=3, replace=False)]

        # Calculate the normal 
        normal = np.cross(b - a, c - a)
        length = np.linalg.norm(normal) #

        # Must be non-collinear ( not too close points )
        if length < 1e-10:
            continue

        normal = normal / length
        offset = normal @ a

        # Calculate every point's distance to the plane
        mask = np.abs(cloud @ normal - offset) <= tolerance_mm

        # How many points satify the range?
        count = np.count_nonzero(mask)

        # Save the best found
        if count > best_count:
            best_plane = (normal, offset)
            best_mask = mask
            best_count = count

    return best_plane, best_mask


def segment_planes(points, sphere_mask=None, tolerance_mm=None, max_planes=MAX_PLANES, refine=False):
    if tolerance_mm is None:
        tolerance_mm = PLANE_TOLERANCE_MM

    rng = np.random.default_rng(RANDOM_SEED)
    plane_labels = np.zeros(len(points), dtype=int)

    if sphere_mask is not None:
        plane_labels[sphere_mask] = -1  # Exclude sphere points from the plane search.

    remaining = np.flatnonzero(plane_labels == 0)
    planes = []
    min_points = max(3, math.ceil(MIN_PLANE_FRACTION * len(points)))

    while len(remaining) >= min_points and (max_planes is None or len(planes) < max_planes):
        plane, mask = find_plane(points[remaining], tolerance_mm, RANSAC_TRIALS, rng)
        count = np.count_nonzero(mask)

        if count < min_points:
            break

        if refine:
            cloud = points[remaining]
            normal, offset = refit_plane(cloud[mask])
            refined_mask = np.abs(cloud @ normal - offset) <= tolerance_mm

            if np.count_nonzero(refined_mask) >= min_points:
                plane, mask = (normal, offset), refined_mask

        planes.append(plane)
        plane_labels[remaining[mask]] = len(planes)
        remaining = remaining[~mask]

    return planes, plane_labels


def sphere_from_four(sample):
    origin = sample[0]
    delta = sample[1:] - origin

    try:
        shift = np.linalg.solve(2 * delta, np.sum(delta ** 2, axis=1))
    except np.linalg.LinAlgError: # If it's not invertible
        return None

    return origin + shift, np.linalg.norm(shift)


def refine_sphere(inliers, center, radius):
    if len(inliers) < 4:
        return center, radius

    # [1, -2x, -2y, -2z] * [x0^2+y0^2+z0^2-R^2, x0, y0, z0] = -(x^2+y^2+z^2)
    A = np.column_stack((np.ones(len(inliers)), -2 * inliers))
    b = -np.sum(inliers ** 2, axis=1)
    solution = np.linalg.pinv(A) @ b

    new_center = solution[1:]
    radius_squared = new_center @ new_center - solution[0]

    if radius_squared <= 0:
        return center, radius

    return new_center, np.sqrt(radius_squared)


def visible_sphere_inliers(points, center, radius, tolerance_mm):
    offsets = points - center
    errors = np.abs(np.linalg.norm(offsets, axis=1) - radius)

    # Assume the camera is at the coordinate origin.
    facing_camera = np.sum(offsets * points, axis=1) <= 0

    return (errors <= tolerance_mm) & facing_camera


def find_sphere(points, tolerance_mm=SPHERE_TOLERANCE_MM):
    rng = np.random.default_rng(RANDOM_SEED)
    sample = points[rng.choice(len(points), min(6000, len(points)), replace=False)]
    scene_width = np.linalg.norm(np.ptp(sample, axis=0))
    best_count = 0
    best = None

    for _ in range(SPHERE_TRIALS):
        # I choose an anchor
        anchor = sample[rng.integers(len(sample))]
        # I look for 4 points near that anchor, but not too far away
        nearby = sample[np.linalg.norm(sample - anchor, axis=1) < scene_width / 10]

        if len(nearby) < 4:
            continue

        sphere = sphere_from_four(nearby[rng.choice(len(nearby), 4, replace=False)])

        if sphere is None:
            continue

        center, radius = sphere

        # Reject excessively large spheres
        if radius > scene_width / 4:
            continue

        count = np.count_nonzero(visible_sphere_inliers(sample, center, radius, tolerance_mm))

        if count > best_count:
            best_count = count
            best = sphere

    if best is None:
        raise ValueError("Could not fit a sphere to this frame.")

    center, radius = best

    # Refit using the full-cloud inliers.
    initial_mask = visible_sphere_inliers(points, center, radius, tolerance_mm)
    center, radius = refine_sphere(points[initial_mask], center, radius)
    final_mask = visible_sphere_inliers(points, center, radius, tolerance_mm)

    return center, radius, final_mask


def label_colors(plane_count):
    # Label 0 is grey; -1 indexes the last palette entry (yellow).
    palette = [[160, 160, 160]]
    for i in range(plane_count):
        hue = (0.6 + i * 0.618) % 1
        palette.append([round(255 * v) for v in hsv_to_rgb(hue, 0.8, 0.85)])
    palette.append([255, 255, 0])
    return np.array(palette, dtype=np.uint8)


def segment_frame(points):
    noise = estimate_surface_noise(points)
    plane_tolerance = 10 * noise
    sphere_tolerance = 3.5 * noise
    _, _, sphere_mask = find_sphere(points, tolerance_mm=sphere_tolerance)
    planes, labels = segment_planes(points, sphere_mask, tolerance_mm=plane_tolerance,
                                   max_planes=None, refine=True)
    colors = label_colors(len(planes))[labels]

    return labels, colors, plane_tolerance, sphere_tolerance


def write_ply(path, points, colors):
    header = ("ply\nformat ascii 1.0\n"
              f"element vertex {len(points)}\n"
              "property double x\nproperty double y\nproperty double z\n"
              "property uchar red\nproperty uchar green\nproperty uchar blue\nend_header")
    np.savetxt(path, np.column_stack((points, colors)), header=header, comments="",
               fmt="%.12g %.12g %.12g %d %d %d")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Color the sphere and planes in an ASCII PCD.")
    parser.add_argument("input_pcd")
    parser.add_argument("output_ply")
    args = parser.parse_args()
    points = read_pcd(args.input_pcd)
    _, colors, plane_tol, sphere_tol = segment_frame(points)
    write_ply(args.output_ply, points, colors)
    print(f"Saved {len(points):,} points. Plane tolerance {plane_tol:.2f} mm, "
          f"sphere tolerance {sphere_tol:.2f} mm.")


if __name__ == "__main__":
    main()
