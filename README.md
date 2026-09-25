# 🎯 ELTE 3D Computer Vision — Course Materials & Study Resources

![University](https://img.shields.io/badge/University-ELTE_Budapest-0065BD?style=for-the-badge&logo=academia&logoColor=white)
![Program](https://img.shields.io/badge/Program-EIT_Digital_MSc_(AUSIR)-blueviolet?style=for-the-badge)
![Semester](https://img.shields.io/badge/Semester-2026%2F2027_Fall-brightgreen?style=for-the-badge)
![Language](https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-In_Progress-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-Educational-lightgrey?style=for-the-badge)

> **The most comprehensive open-source study resource for the 3D Computer Vision course at [Eötvös Loránd University (ELTE)](https://www.elte.hu/en/), Budapest.**
> Labs, quizzes, exercises, lecture notes, and hands-on implementations — all in one place.

---

## 📖 Table of Contents

- [About the Course](#-about-the-course)
- [Topics Covered](#-topics-covered)
- [Course Schedule](#-course-schedule--agenda)
- [Grading & Assessment](#-grading--assessment)
- [Repository Structure](#-repository-structure)
- [Progress Tracker](#-progress-tracker)
- [Tech Stack & Prerequisites](#-tech-stack--prerequisites)
- [External Resources](#-external-resources)
- [Disclaimer](#%EF%B8%8F-disclaimer)

---

## 📚 About the Course

| Detail | Info |
|---|---|
| **Course Name** | 3D Computer Vision |
| **University** | Eötvös Loránd University (ELTE), Budapest, Hungary |
| **Faculty** | Faculty of Informatics |
| **Program** | EIT Digital Master School (AUSIR — Autonomous Systems) |
| **Research Group** | [Geometric Computer Vision Group (GCVG)](https://cv.inf.elte.hu/) |
| **Semester** | 2026/2027 — 1st Semester (Fall) |
| **Lectures** | Thursdays, 14:15–15:45, South Building, Room 0-804 (Lóczy Lajos) |
| **Labs** | Tuesdays 8:30–10:00 & 10:15–11:45 (Room 2-710 PC10) / Wednesdays 12:15–13:45 (Room 0-807 Database Lab) |

This course provides a deep dive into **3D computer vision**, covering the mathematical foundations and practical algorithms used in stereo vision, 3D reconstruction, camera calibration, and autonomous driving perception systems. It is taught by the [Geometric Computer Vision Group (GCVG)](https://cv.inf.elte.hu/) at ELTE's Faculty of Informatics.

---

## 🧠 Topics Covered

- **Estimation Theory** — Solving homogeneous and inhomogeneous linear systems of equations
- **Robust Fitting** — RANSAC algorithm, multi-model fitting (Sequential RANSAC, MultiRANSAC)
- **Constrained Optimization** — Lagrange multipliers
- **Camera Models** — Perspective camera, orthogonal projection, weak-perspective camera
- **Camera Calibration** — Projection matrix estimation & decomposition, chessboard-based calibration, radial & tangential distortion
- **Homography** — Plane-plane homography, panoramic images, data normalization
- **Epipolar Geometry** — Essential & fundamental matrices, rectification, decomposition
- **Triangulation** — Standard and general stereo vision
- **Stereo Vision** — Stereo disparity computation, planar motion
- **3D Reconstruction** — Merging stereo reconstructions, point set registration via similarity transformation
- **Numerical Optimization** — Bundle adjustment, multi-view reconstruction
- **3D Sensing Devices** — Laser scanning, depth cameras, LiDAR

---

## 🗓️ Course Schedule & Agenda

> **Semester**: 2026/2027 Fall (preliminary — subject to changes)

| Week | Lecture | Laboratory |
|------|---------|------------|
| 1 | *Registration week* | — |
| 2 | Introduction | Intro to 3D Computer Vision (Colab) |
| 3 | Estimation theory: inhomogeneous linear systems, Circle estimation | Vehicle & sensor kit demonstration |
| 4 | Constrained optimization: Lagrange multipliers | RANSAC for line fitting (Colab) |
| 5 | TBD | TBD |
| 6 | TBD | TBD |
| 7 | TBD | TBD |
| 8 | TBD | TBD |
| 9 | *Autumn break* | *Autumn break* |
| 10 | TBD | TBD |
| 11 | TBD | TBD |
| 12 | TBD | TBD |
| 13 | TBD | TBD |
| 14 | TBD | TBD |
| 15 | TBD | TBD |

---

## 📊 Grading & Assessment

### Quiz Rules

- **10 quizzes** throughout the semester, taken in-person at the start of labs (online attendance not allowed).
- Each quiz contains **5 questions**:
  - ✅ **+1 point** — 4 or 5 correct answers
  - ➖ **0 points** — 3 correct answers
  - ❌ **-1 point** — fewer than 3 correct answers
- **Minimum requirement**: accumulate **+5 points total** across all quizzes to pass the subject.
- Maximum possible: +10 points.
- Quiz points **do not** affect final grade — they only verify minimum competency.
- **Make-up**: if you miss or fail quizzes, a comprehensive 25-question make-up quiz is available at the start of the exam period (17+ correct answers required to pass).

### Oral Exam Topics

1. Estimation theory (homogeneous/inhomogeneous systems)
2. Robust fitting (RANSAC)
3. Multi-model fitting (Sequential RANSAC, MultiRANSAC)
4. Camera models (perspective, orthogonal, weak-perspective)
5. Camera calibration using spatial objects
6. Chessboard-based calibration, distortion models
7. Plane-plane homography, panoramic images
8. Homography estimation, data normalization
9. Epipolar geometry, essential & fundamental matrices, rectification
10. Estimation of essential/fundamental matrices, decomposition
11. Triangulation (standard & general stereo)
12. Stereo vision for planar motion
13. Reconstruction by merging stereo reconstructions, point set registration
14. Numerical optimization
15. Bundle adjustment
16. 3D sensing: laser scanning, depth cameras, LiDAR

---

## 📂 Repository Structure

```
ELTE-3D-Computer-Vision/
├── README.md
├── LAB/
│   ├── 1/                          # Lab 1 — Stereo Disparity (Jupyter notebooks + datasets)
│   │   ├── 3DCV_Stereo_Disparity_Skeleton_en.ipynb   # Skeleton notebook (exercise)
│   │   ├── 3DCV_Stereo_Disparity_en.ipynb            # Completed solution
│   │   └── Art/                    # Art stereo image pair dataset
│   └── 2/                          # Lab 2 — NumPy Fundamentals
│       ├── numpy_intro.py          # NumPy introduction exercises
│       ├── aritm.py                # Arithmetic operations
│       ├── filtering.py            # Array filtering
│       ├── indexing.py             # Array indexing
│       ├── slicing.py              # Array slicing
│       └── functions_np.py         # NumPy functions practice
└── QUIZ/
    ├── 1/                          # Quiz 1 — PDF question sets (3 PDFs)
    ├── 2/                          # Quiz 2 — (empty, upcoming)
    ├── 3/                          # Quiz 3 — (empty, upcoming)
    ├── 4/                          # Quiz 4 — (empty, upcoming)
    └── 5/                          # Quiz 5 — (empty, upcoming)
```

---

## ✅ Progress Tracker

### Labs
- [x] Lab 1 — Stereo Disparity (completed with solution)
- [x] Lab 2 — NumPy Fundamentals
- [ ] Lab 3
- [ ] Lab 4
- [ ] Lab 5
- [ ] Lab 6

### Quizzes
- [x] Quiz 1 (3 PDFs collected)
- [ ] Quiz 2
- [ ] Quiz 3
- [ ] Quiz 4
- [ ] Quiz 5
- [ ] Quiz 6
- [ ] Quiz 7
- [ ] Quiz 8
- [ ] Quiz 9
- [ ] Quiz 10

### Exams
- [ ] Oral Exam
- [ ] Assignment Presentation

---

## 🛠️ Tech Stack & Prerequisites

| Tool / Library | Purpose |
|---|---|
| **Python 3.12+** | Primary programming language |
| **NumPy** | Numerical computing, matrix operations |
| **Jupyter Notebook / Google Colab** | Interactive lab exercises |
| **OpenCV** | Computer vision operations |
| **Matplotlib** | Visualization of results |

### Getting Started

```bash
# Clone the repository
git clone https://github.com/simo-hue/ELTE-3D-Computer-Vision.git

# Navigate to the project
cd ELTE-3D-Computer-Vision

# Install dependencies
pip install numpy matplotlib opencv-python jupyter
```

---

## 🔗 External Resources

| Resource | Link |
|---|---|
| **Official Course Page** | [3D Computer Vision — GCVG at ELTE](https://cv.inf.elte.hu/index.php/education/3d-computer-vision/) |
| **GCVG YouTube Channel** | [Geometric Computer Vision Group](https://www.youtube.com/@geometriccomputervisiongro6255) |
| **Lab 1 — Colab Notebook** | [Intro to 3D Computer Vision](https://colab.research.google.com/drive/13HN6IMVJA_O7eoTLeXGLdtL2-h8FPS0f) |
| **Lab 3 — RANSAC Colab** | [RANSAC for Line Fitting](https://colab.research.google.com/drive/1773pejXS01vlJpHIlvs_FQEHqnXoOb4C) |
| **Affine/Perspective Transforms** | [Colab Notebook](https://colab.research.google.com/drive/1ve-zjGf3i2wjMFXrtfAoEuQPoFS0GO2r?usp=sharing) |
| **ELTE Faculty of Informatics** | [inf.elte.hu](https://www.inf.elte.hu/en/) |

---

## ⚠️ Disclaimer

> This repository is intended **for educational purposes only**.
> All lecture materials, slides, PDFs, and course content belong to their respective authors and to **Eötvös Loránd University (ELTE)**, Budapest.
> Personal notes, exercise solutions, and code implementations are my own work.
> This repository is not officially affiliated with or endorsed by ELTE or the GCVG research group.

---

## 🌟 Star This Repo

If you find these materials helpful for your studies, please consider giving this repository a ⭐ — it helps other ELTE students discover it!

---

<p align="center">
  Made with 📐 by <a href="https://simo-hue.github.io">Simone Mattioli</a> for 3D Computer Vision students at ELTE Budapest
</p>