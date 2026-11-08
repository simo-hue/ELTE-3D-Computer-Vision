# Sphere + plane segmentation of an organized depth-camera point cloud.
# Usage: python main.py <input.pcd> <output.ply>
# Generated from the notebook; see it for the documentation of the algorithm.
import sys, time
import numpy as np
import open3d as o3d
from scipy import ndimage
from scipy.spatial import cKDTree

def read_pcd(path):
    """Read an ASCII or binary PCD file. Returns (xyz [N,3] float64, header dict)."""
    with open(path, 'rb') as f:
        header, data_mode = {}, None
        while True:
            line = f.readline().decode('ascii', 'ignore').strip()
            if not line or line.startswith('#'):
                continue
            key, *vals = line.split()
            header[key] = vals
            if key == 'DATA':
                data_mode = vals[0]; break
        fields = header['FIELDS']; sizes = list(map(int, header['SIZE']))
        types = header['TYPE']; counts = list(map(int, header.get('COUNT', ['1'] * len(fields))))
        n = int(header['POINTS'][0])
        if data_mode == 'ascii':
            raw = np.loadtxt(f, dtype=np.float64, ndmin=2)
            col, idx = {}, 0
            for name, c in zip(fields, counts):
                col[name] = idx; idx += c
            xyz = raw[:, [col['x'], col['y'], col['z']]]
        elif data_mode == 'binary':
            tmap = {('F', 4): 'f4', ('F', 8): 'f8', ('U', 1): 'u1', ('U', 2): 'u2', ('U', 4): 'u4',
                    ('I', 1): 'i1', ('I', 2): 'i2', ('I', 4): 'i4'}
            dt = np.dtype([(nm, tmap[(t, s)], (c,) if c > 1 else ()) for nm, t, s, c in zip(fields, types, sizes, counts)])
            raw = np.frombuffer(f.read(n * dt.itemsize), dtype=dt, count=n)
            xyz = np.stack([raw['x'], raw['y'], raw['z']], 1).astype(np.float64)
        else:
            raise ValueError(f'Unsupported DATA mode {data_mode}')
    return xyz, header

def write_ply(path, xyz, rgb):
    with open(path, 'w') as f:
        f.write('ply\nformat ascii 1.0\ncomment sphere+plane segmentation\n')
        f.write(f'element vertex {len(xyz)}\nproperty float x\nproperty float y\nproperty float z\n')
        f.write('property uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n')
        np.savetxt(f, np.hstack([xyz, rgb]), fmt='%.3f %.3f %.3f %d %d %d')

def grid_shape_from_header(header, xyz):
    """Determine the organized (rows, cols) layout. The writer used here stores columns contiguously."""
    w, h = int(header['WIDTH'][0]), int(header['HEIGHT'][0])
    if h <= 1 or w * h != len(xyz):
        return None
    best = None
    for shape in [(h, w), (w, h)]:
        g = xyz.reshape(shape + (3,))
        step = np.nanmedian(np.linalg.norm(np.diff(g, axis=1), axis=-1)) + np.nanmedian(np.linalg.norm(np.diff(g, axis=0), axis=-1))
        if best is None or step < best[0]:
            best = (step, shape)
    return best[1]

def estimate_normals_curvature(xyz, k=30):
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(xyz))
    pcd.estimate_normals(o3d.geometry.KDTreeSearchParamKNN(k))
    pcd.orient_normals_towards_camera_location(np.zeros(3))
    pcd.estimate_covariances(o3d.geometry.KDTreeSearchParamKNN(k))
    cov = np.asarray(pcd.covariances)
    ev = np.linalg.eigvalsh(cov)  # ascending
    curvature = ev[:, 0] / np.maximum(ev.sum(1), 1e-12)
    return np.asarray(pcd.normals), curvature

def fit_plane_lsq(P, w=None):
    if w is None:
        c = P.mean(0); Q = P - c
    else:
        c = (P * w[:, None]).sum(0) / w.sum(); Q = (P - c) * np.sqrt(w)[:, None]
    _, _, vt = np.linalg.svd(Q, full_matrices=False)
    n = vt[2]
    return n, -n @ c


def fit_plane_robust(P, iters=5):
    n, d = fit_plane_lsq(P)
    for _ in range(iters):
        r = P @ n + d
        s = max(mad_sigma(r), 1e-6)
        w = 1.0 / (1.0 + (r / (2.5 * s)) ** 2)  # Cauchy weights
        n, d = fit_plane_lsq(P, w)
    return n, d

def fit_sphere_lsq(P):
    A = np.hstack([2 * P, np.ones((len(P), 1))])
    sol, *_ = np.linalg.lstsq(A, (P ** 2).sum(1), rcond=None)
    c = sol[:3]; return c, np.sqrt(max(sol[3] + c @ c, 1e-9))


def fit_sphere_geometric(P, c0, r0, iters=30):
    c, r = c0.copy(), r0
    for _ in range(iters):
        d = P - c; dist = np.linalg.norm(d, axis=1)
        J = np.hstack([-d / dist[:, None], -np.ones((len(P), 1))])
        delta, *_ = np.linalg.lstsq(J, -(dist - r), rcond=None)
        c += delta[:3]; r += delta[3]
        if np.linalg.norm(delta) < 1e-6: break
    return c, r

def mad_sigma(x):
    return 1.4826 * np.median(np.abs(x - np.median(x)))

class Grid:
    """Maps valid points to their pixel in the organized image."""
    def __init__(self, shape, grid_idx):
        self.shape = shape; self.grid_idx = grid_idx
        self.img = np.full(shape[0] * shape[1], -1, int); self.img[grid_idx] = np.arange(len(grid_idx))
        self.img = self.img.reshape(shape)

    def mask(self, idx):
        m = np.zeros(self.shape, bool); m.flat[self.grid_idx[idx]] = True; return m

    def components(self, idx, close_iter=1):
        m = self.mask(idx)
        if close_iter: m = ndimage.binary_closing(m, iterations=close_iter) | m
        lab, _ = ndimage.label(m, structure=np.ones((3, 3)))
        return lab.flat[self.grid_idx[idx]]

    def largest_component(self, idx):
        lab = self.components(idx); counts = np.bincount(lab); counts[0] = 0
        return idx[lab == counts.argmax()]

    def neighbour_pairs(self):
        img = self.img; pairs = []
        for a, b in [(img[:-1, :], img[1:, :]), (img[:, :-1], img[:, 1:])]:
            a = a.ravel(); b = b.ravel(); ok = (a >= 0) & (b >= 0)
            pairs.append((a[ok], b[ok]))
        a = np.concatenate([p[0] for p in pairs]); b = np.concatenate([p[1] for p in pairs])
        return a, b

def plane_ransac(P, Nn, dist_thr, cos_tol, iters, rng):
    best_inl, best_cnt = None, 0
    for _ in range(iters):
        i = rng.integers(len(P))
        n, d = Nn[i], -Nn[i] @ P[i]
        inl = (np.abs(P @ n + d) < dist_thr) & (np.abs(Nn @ n) > cos_tol)
        cnt = inl.sum()
        if cnt > best_cnt: best_cnt, best_inl = cnt, inl
    return best_inl

def calibrate_noise(xyz, normals, rng):
    """Dominant plane with a coarse threshold (1% of extent); robust sigma of its residuals."""
    extent = np.ptp(xyz, axis=0).max()
    sub = rng.choice(len(xyz), min(40000, len(xyz)), replace=False)
    P, Nn = xyz[sub], normals[sub]
    inl = plane_ransac(P, Nn, 0.01 * extent, np.cos(np.deg2rad(30)), 200, rng)
    for _ in range(3):
        n, d = fit_plane_lsq(P[inl])
        res = P @ n + d
        s = mad_sigma(res[inl])
        inl = np.abs(res) < 3 * s
    return s, extent

def detect_sphere(xyz, normals, dist_thr, r_range, tree, rng, iters=3000, normal_tol_deg=35.0):
    """Normal-aided RANSAC: two oriented points define a sphere (centre = closest point of the two
    normal lines). Candidates are scored by distance + normal consistency, refined by LSQ."""
    N = len(xyz); cos_tol = np.cos(np.deg2rad(normal_tol_deg))
    best, best_score = None, 0
    for _ in range(iters):
        i = rng.integers(N)
        nb = tree.query_ball_point(xyz[i], 1.5 * r_range[1])
        if len(nb) < 10: continue
        j = nb[rng.integers(len(nb))]
        if i == j: continue
        p1, p2, n1, n2 = xyz[i], xyz[j], normals[i], normals[j]
        w = p1 - p2
        a, b, c = n1 @ n1, n1 @ n2, n2 @ n2
        d, e = n1 @ w, n2 @ w
        den = a * c - b * b
        if den < 1e-4: continue
        t = (b * e - c * d) / den; s = (a * e - b * d) / den
        if t * s < 0: continue
        c1 = p1 + t * n1; c2 = p2 + s * n2
        r = 0.5 * (abs(t) + abs(s))
        if not (r_range[0] <= r <= r_range[1]): continue
        if np.linalg.norm(c1 - c2) > max(2 * dist_thr, 0.1 * r): continue
        center = 0.5 * (c1 + c2)
        cand = np.asarray(tree.query_ball_point(center, r + 2 * dist_thr))
        if len(cand) < 50: continue
        dv = xyz[cand] - center; dn = np.linalg.norm(dv, axis=1)
        good = np.abs(dn - r) < dist_thr
        cosang = np.abs((dv[good] / dn[good, None] * normals[cand][good]).sum(1))
        score = int((cosang > cos_tol).sum())
        if score > best_score:
            best_score, best = score, (center, r, cand[good][cosang > cos_tol])
    if best is None: return None
    center, r, inl = best
    for _ in range(4):
        center, r = fit_sphere_lsq(xyz[inl]); center, r = fit_sphere_geometric(xyz[inl], center, r)
        cand = np.asarray(tree.query_ball_point(center, r + 2 * dist_thr))
        dv = xyz[cand] - center; dn = np.linalg.norm(dv, axis=1)
        good = np.abs(dn - r) < dist_thr
        cosang = np.abs((dv[good] / dn[good, None] * normals[cand][good]).sum(1))
        inl = cand[good][cosang > cos_tol]
    return dict(center=center, radius=r, inliers=inl)

def neighbour_table(grid):
    """[N,4] array of 4-neighbour point indices on the grid (-1 where none)."""
    img = grid.img; N = len(grid.grid_idx)
    nb = np.full((N, 4), -1, int)
    pad = np.pad(img, 1, constant_values=-1)
    valid = img >= 0
    for k, (dy, dx) in enumerate([(-1, 0), (1, 0), (0, -1), (0, 1)]):
        sh = pad[1 + dy: 1 + dy + img.shape[0], 1 + dx: 1 + dx + img.shape[1]]
        nb[img[valid], k] = sh[valid]
    return nb

def region_growing(xyz, normals, curvature, grid, active, dist_thr, min_points,
                   local_deg=15.0, region_deg=20.0, max_seeds=4000):
    """Seeded region growing on the organized grid (vectorised frontier expansion).
    A candidate joins the region if (1) it is on the tangent plane of the labelled neighbour it is
    reached from (|d.n| < dist_thr -> rejects depth discontinuities), (2) its normal is within
    local_deg of that neighbour and (3) within region_deg of the region's running mean normal
    (the non-local test that stops leaking around corners)."""
    nb = neighbour_table(grid)
    cos_loc, cos_reg = np.cos(np.deg2rad(local_deg)), np.cos(np.deg2rad(region_deg))
    labels = np.full(len(xyz), -1)   # -1 unvisited, -2 visited but region too small
    labels[~active] = -3
    order = np.argsort(curvature)  # lowest curvature first = best seeds
    regions, next_label, seeds_used = [], 0, 0
    for seed in order:
        if labels[seed] != -1: continue
        if seeds_used >= max_seeds: break
        seeds_used += 1
        members = [np.array([seed])]; labels[seed] = next_label
        nsum = normals[seed].copy(); frontier = np.array([seed])
        while len(frontier):
            nreg = nsum / np.linalg.norm(nsum)
            cand = nb[frontier]                     # [F,4]
            src = np.repeat(frontier, 4)
            cand = cand.ravel()
            ok = (cand >= 0)
            cand, src = cand[ok], src[ok]
            ok = labels[cand] == -1
            cand, src = cand[ok], src[ok]
            if len(cand) == 0: break
            d = xyz[cand] - xyz[src]
            ok = ((np.abs((d * normals[src]).sum(1)) < dist_thr) &
                  (np.abs((normals[cand] * normals[src]).sum(1)) > cos_loc) &
                  (np.abs(normals[cand] @ nreg) > cos_reg))
            cand = np.unique(cand[ok])
            if len(cand) == 0: break
            labels[cand] = next_label
            # accumulate normals with consistent sign relative to region normal
            nc = normals[cand]; sgn = np.sign(nc @ nreg); sgn[sgn == 0] = 1
            nsum += (nc * sgn[:, None]).sum(0)
            members.append(cand); frontier = cand
        members = np.concatenate(members)
        if len(members) < min_points:
            labels[members] = -2
        else:
            regions.append(members); next_label += 1
    return regions

def extract_planes(xyz, normals, curvature, grid, active, dist_thr, min_points, planar_deg=15.0):
    regions = region_growing(xyz, normals, curvature, grid, active, dist_thr, min_points)
    planes = []
    for idx in regions:
        n, d = fit_plane_robust(xyz[idx])
        agree = np.median(np.abs(normals[idx] @ n))
        if agree < np.cos(np.deg2rad(planar_deg)):
            continue  # curved region -> not a plane
        planes.append(dict(normal=n, d=d, inliers=idx))
    return planes

def merge_planes(planes, xyz, grid, dist_thr, ang_deg=8.0):
    """Merge adjacent regions whose fitted planes agree (orientation and offset)."""
    changed = True
    while changed:
        changed = False
        for i in range(len(planes)):
            for j in range(i + 1, len(planes)):
                a, b = planes[i], planes[j]
                if abs(a['normal'] @ b['normal']) < np.cos(np.deg2rad(ang_deg)): continue
                # offsets: evaluate each plane at the other's centroid
                ca, cb = xyz[a['inliers']].mean(0), xyz[b['inliers']].mean(0)
                if max(abs(cb @ a['normal'] + a['d']), abs(ca @ b['normal'] + b['d'])) > 4 * dist_thr: continue
                ma = ndimage.binary_dilation(grid.mask(a['inliers']), iterations=4)
                if not ma.flat[grid.grid_idx[b['inliers']]].any(): continue
                inl = np.concatenate([a['inliers'], b['inliers']])
                n, d = fit_plane_robust(xyz[inl])
                planes[i] = dict(normal=n, d=d, inliers=inl); planes.pop(j)
                changed = True; break
            if changed: break
    return planes

def propagate_labels(labels, xyz, normals, grid, planes, dist_thr, passes=12, ang_deg=20.0):
    """Grow plane labels into unlabeled neighbours that are locally consistent with the plane:
    tangent-plane distance to the labelled neighbour < dist_thr, normal within ang_deg of the plane."""
    a, b = grid.neighbour_pairs()
    a2 = np.concatenate([a, b]); b2 = np.concatenate([b, a])  # both directions: a labelled -> b candidate
    plane_n = np.array([p['normal'] for p in planes])
    cos_tol = np.cos(np.deg2rad(ang_deg))
    for _ in range(passes):
        src_lab = labels[a2]
        ok = (src_lab >= 1) & (labels[b2] == -1)
        if not ok.any(): break
        s, t, L = a2[ok], b2[ok], src_lab[ok]
        n_plane = plane_n[L - 1]
        d = xyz[t] - xyz[s]
        good = (np.abs((d * normals[s]).sum(1)) < dist_thr) & (np.abs((normals[t] * n_plane).sum(1)) > cos_tol)
        if not good.any(): break
        # a candidate may receive several proposals; take the first (arbitrary but deterministic)
        labels[t[good]] = L[good]
    return labels

def segment(xyz_all, header=None, verbose=True, rng_seed=0, min_halfwidth_px=8, max_normal_dev_deg=12.0):
    rng = np.random.default_rng(rng_seed)
    t0 = time.time()
    valid = np.isfinite(xyz_all).all(1) & (np.abs(xyz_all).sum(1) > 0)
    xyz = xyz_all[valid]; grid_idx = np.where(valid)[0]
    shape = grid_shape_from_header(header, xyz_all) if header else None
    if shape is None:
        raise ValueError('This pipeline needs an organized cloud (WIDTH x HEIGHT grid) for the region growing')
    grid = Grid(shape, grid_idx)
    normals, curvature = estimate_normals_curvature(xyz)
    tree = cKDTree(xyz)
    sigma, extent = calibrate_noise(xyz, normals, rng)
    dist_thr = 3.0 * sigma
    r_range = (0.02 * extent, 0.3 * extent)
    min_points = max(300, int(0.005 * len(xyz)))
    if verbose: print(f'sigma={sigma:.2f} mm -> thr={dist_thr:.1f} mm, extent={extent:.0f} mm, r in [{r_range[0]:.0f},{r_range[1]:.0f}]')

    # --- sphere
    sph = detect_sphere(xyz, normals, dist_thr, r_range, tree, rng)
    # final sphere membership: distance only, single connected blob, refit
    for _ in range(2):
        dv = xyz - sph['center']; res = np.abs(np.linalg.norm(dv, axis=1) - sph['radius'])
        cand = np.where(res < dist_thr)[0]
        si = grid.largest_component(cand)
        sph['center'], sph['radius'] = fit_sphere_geometric(xyz[si], *fit_sphere_lsq(xyz[si]))
    sph['inliers'] = si
    # final parameters from well-viewed points only: ToF silhouettes (grazing > 70 deg) are biased outward
    P = xyz[si]; nrm = P - sph['center']; nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    view = -P / np.linalg.norm(P, axis=1)[:, None]
    well = (nrm * view).sum(1) > np.cos(np.deg2rad(70))
    if well.sum() > 100:
        sph['center'], sph['radius'] = fit_sphere_geometric(P[well], *fit_sphere_lsq(P[well]))
    if verbose: print('sphere', sph['center'].round(1), round(sph['radius'], 1), len(si), f'{time.time()-t0:.1f}s')

    # --- planes by smooth region growing on low-curvature, non-sphere points
    active = np.ones(len(xyz), bool); active[si] = False
    planes = extract_planes(xyz, normals, curvature, grid, active, dist_thr, min_points)
    planes = merge_planes(planes, xyz, grid, dist_thr)
    planes.sort(key=lambda p: -len(p['inliers']))

    labels = np.full(len(xyz), -1); labels[si] = 0
    for k, p in enumerate(planes): labels[p['inliers']] = k + 1
    labels = propagate_labels(labels, xyz, normals, grid, planes, dist_thr)
    # --- validate each plane after propagation; drop thin strips (corner smoothing artefacts)
    #     and ragged regions whose normals do not agree with the fitted plane
    kept = []
    for k, p in enumerate(planes):
        idx = np.where(labels == k + 1)[0]
        n, d = fit_plane_robust(xyz[idx])
        m = grid.mask(idx); m = ndimage.binary_closing(m, iterations=1) | m
        halfwidth = np.percentile(ndimage.distance_transform_edt(m).flat[grid.grid_idx[idx]], 90)
        ang_med = np.degrees(np.arccos(np.clip(np.median(np.abs(normals[idx] @ n)), 0, 1)))
        p.update(inliers=idx, normal=n, d=d, halfwidth_px=float(halfwidth), normal_dev_deg=float(ang_med))
        r = xyz[idx] @ n + d; p['rms'] = float(np.sqrt(np.mean(r ** 2)))
        if halfwidth < min_halfwidth_px or ang_med > max_normal_dev_deg or len(idx) < min_points:
            labels[idx] = -1
            if verbose: print(f'  rejected region: {len(idx)} pts, halfwidth {halfwidth:.1f}px, normal dev {ang_med:.1f} deg')
            continue
        kept.append(p)
    planes = kept
    labels = np.where(labels > 0, -1, labels)
    for k, p in enumerate(planes): labels[p['inliers']] = k + 1
    r = np.linalg.norm(xyz[si] - sph['center'], axis=1) - sph['radius']; sph['rms'] = float(np.sqrt(np.mean(r ** 2)))
    if verbose:
        for p in planes: print('plane n=', p['normal'].round(3), 'd=', round(p['d'], 1), 'pts', len(p['inliers']), 'rms %.1f' % p['rms'])
        print(f'sphere pts {len(si)} rms {sph["rms"]:.1f}, unassigned {(labels<0).sum()}  total {time.time()-t0:.1f}s')
    return xyz, labels, sph, planes, dict(sigma=sigma, dist_thr=dist_thr, grid=shape, normals=normals, seconds=time.time() - t0)

PALETTE = np.array([[255, 255, 0], [230, 25, 75], [60, 180, 75], [0, 130, 200], [245, 130, 48], [145, 30, 180],
                    [70, 240, 240], [240, 50, 230], [210, 245, 60], [250, 190, 212], [0, 128, 128], [220, 190, 255],
                    [170, 110, 40], [128, 0, 0], [170, 255, 195], [128, 128, 0]])

def colorize(labels):
    rgb = np.full((len(labels), 3), 80, int)
    m = labels >= 0
    rgb[m] = PALETTE[labels[m] % len(PALETTE)]
    rgb[labels == 0] = PALETTE[0]
    return rgb


def process_file(pcd_path, ply_path, verbose=True):
    """Full run for one file: read -> segment -> write coloured PLY. Returns the segmentation result."""
    xyz_all, header = read_pcd(pcd_path)
    xyz, labels, sph, planes, info = segment(xyz_all, header, verbose=verbose)
    write_ply(ply_path, xyz, colorize(labels))
    return xyz, labels, sph, planes, info

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python main.py <input.pcd> <output.ply>")
    try:
        process_file(sys.argv[1], sys.argv[2])
    except Exception as exc:
        sys.exit(f"error: {exc}")
