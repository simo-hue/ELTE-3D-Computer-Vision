import math
import os
from colorsys import hsv_to_rgb

import numpy as np


MAX_PLANES = 4
PLANE_TOLERANCE_MM = 6.0
MIN_PLANE_FRACTION = 0.03
RANSAC_TRIALS = 150
RANDOM_SEED = 42
SPHERE_TRIALS = 800
SPHERE_TOLERANCE_MM = 5.0


def read_pcd(file_path, filter_zeros=True):
    """Read XYZ columns from an ASCII PCD file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    header = {}
    data_started = False
    points_list = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if not data_started:
                tokens = line.split()
                keyword = tokens[0].upper()
                if keyword == 'DATA':
                    header['DATA'] = tokens[1] if len(tokens) > 1 else 'ascii'
                    if header['DATA'].lower() != 'ascii':
                        raise ValueError("Expected an ASCII PCD file.")
                    fields = header.get('FIELDS', [])
                    counts = list(map(int, header.get('COUNT', ['1'] * len(fields))))
                    columns = [sum(counts[:fields.index(axis)]) for axis in ('x', 'y', 'z')]
                    data_started = True
                else:
                    header[keyword] = tokens[1:]
            else:
                parts = line.split()
                points_list.append([float(parts[i]) for i in columns])

    points = np.array(points_list, dtype=np.float64).reshape(-1, 3)
    raw_count = len(points)

    if filter_zeros and len(points) > 0:
        valid_mask = np.isfinite(points).all(axis=1) & (points[:, 2] > 0.0) & (np.linalg.norm(points, axis=1) > 1e-3)
        points = points[valid_mask]

    return points, header, raw_count


def refit_plane(inliers):
    """Fit a plane through the inliers by finding their least-spread direction."""
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
        a, b, c = cloud[rng.choice(len(cloud), size=3, replace=False)]
        normal = np.cross(b - a, c - a)
        length = np.linalg.norm(normal)

        if length < 1e-10:
            continue

        normal = normal / length
        offset = normal @ a
        mask = np.abs(cloud @ normal - offset) <= tolerance_mm
        count = np.count_nonzero(mask)

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
    except np.linalg.LinAlgError:
        return None
    return origin + shift, np.linalg.norm(shift)


def refine_sphere(inliers, center, radius, iterations=10):
    """Use Gauss-Newton to reduce radial errors on the sphere inliers."""
    center = np.asarray(center, dtype=float).copy()
    radius = float(radius)

    if len(inliers) < 4:
        return center, radius

    for _ in range(iterations):
        offsets = inliers - center
        distances = np.linalg.norm(offsets, axis=1)
        valid = distances > 1e-12  # The radial direction is undefined at the center.
        if np.count_nonzero(valid) < 4:
            break

        residuals = distances[valid] - radius
        jacobian = np.column_stack((
            -offsets[valid] / distances[valid, None],
            -np.ones(np.count_nonzero(valid))
        ))

        # Solve for changes in the three center coordinates and the radius.
        step, *_ = np.linalg.lstsq(jacobian, -residuals, rcond=None)
        new_center = center + step[:3]
        new_radius = radius + step[3]

        if not np.all(np.isfinite(new_center)) or not np.isfinite(new_radius) or new_radius <= 0:
            break

        # Shorten the step if it makes the fit worse.
        old_sse = np.sum(residuals ** 2)
        fraction = 1.0
        accepted = False

        for _ in range(10):
            candidate_center = center + fraction * step[:3]
            candidate_radius = radius + fraction * step[3]

            if candidate_radius > 0:
                candidate_residuals = np.linalg.norm(inliers[valid] - candidate_center, axis=1) - candidate_radius

                if np.sum(candidate_residuals ** 2) <= old_sse:
                    center, radius = candidate_center, candidate_radius
                    accepted = True
                    break
            fraction *= 0.5

        if not accepted or np.linalg.norm(fraction * step) < 1e-5:
            break

    return center, radius


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
        anchor = sample[rng.integers(len(sample))]
        nearby = sample[np.linalg.norm(sample - anchor, axis=1) < scene_width / 10]

        if len(nearby) < 4:
            continue
        sphere = sphere_from_four(nearby[rng.choice(len(nearby), 4, replace=False)])

        if sphere is None:
            continue
        center, radius = sphere

        if radius > scene_width / 4:
            continue
        count = np.count_nonzero(visible_sphere_inliers(sample, center, radius, tolerance_mm))

        if count > best_count:
            best_count = count
            best = sphere

    if best is None:
        raise ValueError("Could not fit a sphere to this frame.")

    center, radius = best

    # Refit using the full-cloud inliers, then check membership again.
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
    plane_tolerance = 4 * noise
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
    points, _, _ = read_pcd(args.input_pcd)
    _, colors, plane_tol, sphere_tol = segment_frame(points)
    write_ply(args.output_ply, points, colors)
    print(f"Saved {len(points):,} points. Plane tolerance {plane_tol:.2f} mm, "
          f"sphere tolerance {sphere_tol:.2f} mm.")


if __name__ == "__main__":
    main()
