During this assignment, you must first calibrate a camera, then use the calibrated camera to generate a point cloud of a specific scene/object. You will need a camera for this task (a smartphone camera is perfectly suitable). You are required to develop a single application except for the calibration process.

**Input for the application:**

- Images of a calibration object (e.g., a chessboard) taken with the camera.
- Images of a scene or object taken from multiple different angles using the same camera.
- **At least 5 images must be used** (feel free to use more)**.**

**Example Pipeline**

The application should implement a pipeline consisting of the following components:

- **Camera calibration and image undistortion**.
- **Automatic feature detection** on image pairs captured by the calibrated camera.
- **Computation of the Fundamental Matrix** between image pairs.
- **Triangulation** using the mid-point algorithm and the **decomposition of the essential matrix**.
- **Merging the resulting point clouds** using optimal point cloud registration.
- - *Bonus point opportunity:* Numerical optimization considering reprojection errors in all images.
- The final point cloud should be **colored** based on the images and saved in **PLY format**.

Other reconstruction pipelines may be implemented, but the solution and the associated points must be coordinated with one of the instructors in advance.

**Requirements & Visualizations**

- Each step must be **visualized using OpenCV** (e.g., drawing detected feature points, drawing epipolar lines).
- Test the reconstruction pipeline on at least **three different scenes/objects**.
- *Tip:* It is recommended to place an interesting object relatively close to the camera and "walk around" it to capture it from different viewpoints.

**Tools & Constraints**

- You may use libraries such as **OpenCV, NumPy**, etc. (as used during the practice sessions). The use of ready-made solutions (e.g., **COLMAP**) is **not permitted**.

The presentation of the finished application is part of the assignment. You have to be able to justify every design decision you made. You have to be able to explain every line of code you submit.

Upload the source code(s) and the PLY files in a single zip file.