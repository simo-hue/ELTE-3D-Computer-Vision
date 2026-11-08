# Project Documentation: ELTE 3D Computer Vision - Assignment 1

## Implementation Log

### [2026-11-01 15:52]: Initial Setup & Step 1: Custom PCD Parser
- *Details*:
  - Initialized `FIRST_ASSIGNMENT/Assignment1_3D_Segmentation.ipynb` containing the project overview, theoretical roadmap, and Step 1 implementation.
  - Implemented from-scratch `read_pcd` function that parses ASCII PCD files, extracting strictly $(x, y, z)$ coordinates and filtering out sensor occlusion zeros/non-positive depth values ($z \le 0$).
  - Executed and validated parsing on `Frame4994.pcd` ($217{,}088$ points declared, $215{,}659$ valid 3D points in range $Z \in [259.44, 1779.51]$ mm).
- *Tech Notes*:
  - Dependencies: Installed `opencv-python` (version 5.0.0.93) to satisfy course requirements alongside `numpy`.
  - Created: `FIRST_ASSIGNMENT/Assignment1_3D_Segmentation.ipynb`.

### [2026-11-01 16:11]: Created requirements.txt
- *Details*:
  - Created `FIRST_ASSIGNMENT/requirements.txt` and root `requirements.txt` specifying `numpy>=1.24.0`, `opencv-python>=4.8.0`, and optional `matplotlib>=3.7.0` for notebook visualization.
  - Verified installation compatibility via `python3 -m pip install -r FIRST_ASSIGNMENT/requirements.txt`.
- *Tech Notes*:
  - Files created: `FIRST_ASSIGNMENT/requirements.txt`, `requirements.txt`.

### [2026-11-01 16:16]: Concise Styling Applied to Notebook
- *Details*:
  - Streamlined `Assignment1_3D_Segmentation.ipynb` text to be minimal and direct.
  - Removed boilerplate descriptions while maintaining key formulas and code clarity.

### [2026-11-08 10:55]: Candidate plane example
- *Details*: Added the three-point plane and perpendicular distance exercise to FIRST_ASSIGNMENT/Assignment.ipynb.
- *Tech Notes*: Verified that Q is 2 mm from the example plane and falls within the 3 mm tolerance using NumPy.

### [2026-11-08 11:13]: Configurable plane detection
- *Details*: Added a Parameters section and sequential RANSAC plane detection to Assignment.ipynb. Plane labels preserve the input point order.
- *Tech Notes*: Verified four-plane and single-plane runs on Frame4994 with python3 and NumPy. The project .venv currently lacks NumPy. Removed unused notebook imports.

### [2026-11-08 11:23]: Plane label visualization
- *Details*: Appended camera and side views to Assignment.ipynb and saved the rendered result for Frame4994.
- *Tech Notes*: Verified both views using existing plane labels and the optional notebook dependency Matplotlib.

### [2026-11-08 11:30]: Batch frame processing and four-point sphere example
- *Details*: The notebook selects all local PCD frames by default or one named input. Each frame has independent plane labels and plots. Added the sphere equation and a known-radius example.
- *Tech Notes*: Verified all 11 frames, single-file mode, the example center and radius, and rejection of a singular sample. Uses existing dependencies.

### [2026-11-08 11:37]: Sphere RANSAC across course frames
- *Details*: Added a four-point local RANSAC detector, full-frame sphere masks, and a camera-view comparison to Assignment.ipynb.
- *Tech Notes*: Verified the notebook on 11 PCDs with NumPy and Matplotlib. The yellow mask overlaps the ball in every preview, with some gaps at the edges and on the visible face. No new dependencies.

### [2026-11-08 11:43]: Combined sphere and plane colors
- *Details*: Section 7 reserves sphere inliers before plane fitting and creates one RGB value per valid XYZ point. Saved the combined Frame4994 preview in the notebook.
- *Tech Notes*: Verified all 11 frames for sphere mask preservation, color uniqueness and point/color alignment. No new dependencies.

### [2026-11-08 11:49]: Plane tolerance comparison
- *Details*: Compared 3 mm and 6 mm on Frame4994 with the same seed and sphere mask. The wider cutoff consolidated the upper-left wall, while the lower surface still received two labels.
- *Tech Notes*: Added an optional tolerance argument and saved the side-by-side plot in Assignment.ipynb. Verified 88,620 and 118,578 plane points respectively, with identical sphere masks.

### [2026-11-08 11:52]: Plane tolerance default across course frames
- *Details*: Compared 3 mm and 6 mm on all 11 frames with fixed sphere masks and four-plane cap. Selected 6 mm based on coverage and camera-view continuity.
- *Tech Notes*: Added a reproducible coverage table and refreshed plane previews. Confirmed 118,578 plane points on Frame4994 using the new default.

### [2026-11-08 11:54]: Uncapped plane stopping test
- *Details*: Compared the four-plane baseline with the existing 3% support stopping rule across all 11 frames. Additional candidates raised coverage but included apparent duplicate wall fits.
- *Tech Notes*: Added an explicit per-call plane cap and a reproducible uncapped notebook comparison. Validated the per-frame counts and the fixed sphere masks.

### [2026-11-08 12:00]: Per-frame noise estimation and automatic command-line segmentation
- *Details*: Added one-step plane refinement, local surface noise estimates, explicit sphere tolerance, and notebook-generated main.py with an ASCII PLY writer. PCD parsing uses field names and skips invalid measurements.
- *Tech Notes*: Verified adaptive segmentation across all 11 frames, compared fixed-tolerance refinement on Frame4994, ran the generated CLI and reloaded its 215,659-row PLY. Runtime requires NumPy and the standard library.
