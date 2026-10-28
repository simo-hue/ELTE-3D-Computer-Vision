[Submit Assignment](#)

**Background**

You are provided with [3D point cloud data (Links to an external site.)](https://ikelte-my.sharepoint.com/:f:/g/personal/kovbando_inf_elte_hu/IgAE3gI3BDMdT5IAVGK2umv5ATG2yDrlbPOPP3DLc0Dwkas?e=LHDPrn) captured by a depth camera, stored in a PCD (Point Cloud Data) file format. The objective of this assignment is to process the raw spatial data, identify specific geometric primitives, and output a color-coded point cloud for visualization.

**Objective**

Develop a fully automated command-line application that reads a PCD file, segments the point cloud to find exactly one sphere and an arbitrary number of planar segments, and exports the reconstructed result into a PLY file as a colored point cloud.

**Critical Constraint:** The segmentation algorithm must be implemented from scratch. The only external third-party library permitted for this project is **OpenCV** and python-related mathematical libraries.

**Requirements**

1. **Strict Library Restrictions & Implementation**
- **Allowed Libraries:** You may ONLY use OpenCV (for matrix operations, data structures, etc.) and standard language libraries (e.g., C++ STL, or Python's standard libraries and NumPy).
- **Forbidden Libraries:** The use of dedicated 3D processing or geometry libraries (such as PCL, Open3D, Trimesh, CGAL, etc.) is **strictly prohibited**.
- **Custom Algorithm:** The core segmentation logic (e.g., RANSAC, Region Growing, Hough Transform, or any other mathematical approach used to find the sphere and planes) **must be implemented entirely by you**.
- **File I/O:** Since standard OpenCV does not natively handle.pcd and.ply point cloud files out-of-the-box, you are expected to write your own lightweight file parser and exporter to read the coordinates and write the final colored point cloud.
2. **Data Processing**
- **Input Parsing:** The software must read a given.pcd file. Even if the input file contains additional data fields (such as intensity, normal vectors, or original colors), your algorithm must **only consider the spatial coordinates (x, y, z)**.
- **Geometric Segmentation:**
- You must detect and reconstruct **exactly one sphere** present in the point cloud.
- You must detect and reconstruct an **arbitrary number of planar segments** (planes) present in the scene.
3. **Output and Coloring Rules**
- The output must be saved as a.ply file containing a **colored point cloud** ([ASCII file preferred (Links to an external site.)](https://paulbourke.net/dataformats/ply/)).
- **Color constraints:**
- The points belonging to the **sphere** must be colored **Yellow** (RGB: 255, 255, 0).
- The points belonging to the **planar segments** must be colored such that **each individual plane has a distinct, arbitrary color** to clearly separate them visually.
- Unclassified points (noise/outliers) can be discarded or colored in a neutral color (e.g., grey/black), depending on your implementation preference.
4. **Execution & Interface**
- The software must be **fully automatic**. No graphical user interface (GUI) or manual user intervention (like manual parameter tuning during runtime) is required.
- It must be runnable from the command line.
- The application must accept exactly two positional arguments: the input PCD file path and the desired output PLY file path.
- **Usage example:**

*./segmentation\_tool <input\_file.pcd> <output\_file.ply>*  
*\# or if using Python:*  
*python main.py <input\_file.pcd> <output\_file.ply>*

**Deliverables**

1. **Source Code:** Clean, well-documented source code containing your custom algorithm.
1. **Instructions (README):** A brief guide on how to build/install dependencies and how to run the software.
1. If you use GenAI tool(s), please create a separate text file with the details (promts, answers,... etc.)
1. **Build System:** If using C++, include a CMakeLists.txt or Makefile. If using Python, include a requirements.txt (which should essentially only contain opencv-python and numpy).

**Evaluation Criteria**

- **Algorithmic Skill:** The mathematical correctness, efficiency, and robustness of your custom, from-scratch segmentation algorithm.
- **Accuracy:** Correct identification of the sphere and the distinct planes despite potential sensor noise.
- **Automation:** The algorithm should robustly handle the segmentation without requiring hard-coded, dataset-specific thresholds if possible.
- **Code Quality:** Readability, modularity, and proper error handling.
- **Adherence to constraints:** Strict adherence to the OpenCV-only rule and exact command-line arguments.

Please compress the files with at least three different resulting PLY files in a zip, and upload it to CANVAS.