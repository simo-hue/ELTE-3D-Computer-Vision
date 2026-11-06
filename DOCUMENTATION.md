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
