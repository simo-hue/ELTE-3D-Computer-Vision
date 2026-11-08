# Sphere + plane segmentation (unconstrained, best-quality version)

Finds exactly one sphere and an arbitrary number of planar segments in Kinect-style PCD frames and
writes a coloured ASCII PLY (sphere yellow, each plane its own colour, unassigned grey).

* `sphere_plane_segmentation.ipynb` – the full, executed notebook: data exploration, algorithm
  explanation, implementation, per-frame results, sanity checks, and generation of `main.py`.
* `main.py` – command-line tool generated from the notebook:
  `python main.py <input.pcd> <output.ply>`
* `output/` – coloured PLY for all 11 frames + `all_frames.png` overview.

## Install / run

```
pip install -r requirements.txt
jupyter notebook sphere_plane_segmentation.ipynb   # expects the *.pcd files in ./data
python main.py data/Frame7183.pcd out.ply          # or the CLI
```

## Method in one paragraph

Normals/curvature via Open3D PCA; the sensor noise σ is measured from the dominant plane's residuals
so every metric threshold is a multiple of σ. The sphere is found with a normal-aided 2-point RANSAC
(centre = intersection of two normal lines), refined by algebraic + Gauss-Newton least squares and
re-estimated on well-viewed points to avoid the time-of-flight silhouette bias. Planes come from a
vectorised seeded region growing on the organized depth grid (depth continuity, local smoothness and a
non-local test against the region's mean normal that stops leaks across corners), followed by
coplanar merging, label propagation into the gaps and validation of each region. Plain iterative RANSAC
was rejected because the walls in this data bow by ±3 cm and get sliced into slabs.
