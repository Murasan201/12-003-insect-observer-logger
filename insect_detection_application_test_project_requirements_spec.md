# Requirements Specification Document

## 1. Project Overview

**Name**: Insect Detection Application Test Project (CPU Version)  
**Purpose**: Evaluate the capability of a YOLO model to detect insects (e.g., beetles) in still images and visualize the results.

---

## 2. Scope

- **Input Images**: JPEG/PNG still images in a user-specified directory  
- **Detection Target**: YOLO categories such as "bug" or "insect"  
- **Output**: Images overlaid with bounding boxes where detections occur, saved to an output directory

---

## 3. Runtime Environment

### 3.1 Test Environment (Current Phase)
- **OS**: WSL2 on Windows 10/11 (Ubuntu 22.04 recommended)  
- **Hardware**: Host PC CPU (minimum quad-core recommended)  
- **Accelerator**: None (CPU-only inference)

### 3.2 Future Environment (Reference)
- **OS**: Raspberry Pi OS (64bit)  
- **Hardware**: Raspberry Pi 5 (8GB RAM)  
> *Not used in this phase*

---

## 4. Software Components

- **Language**: Python 3.9+  
- **Deep Learning Framework**: Ultralytics YOLOv8 (CPU mode)  
- **Key Libraries**:
  - OpenCV (image I/O and drawing)  
  - NumPy  
  - torch, torchvision (CPU builds)

---

## 5. Functional Requirements

1. **Standalone Execution**  
   - Users run the script via `python detect_insect.py`  
2. **Directory Specification**  
   - Input and output directories specified via command-line arguments  
3. **Batch Inference**  
   - Perform sequential YOLO inference on all images in the specified input directory using CPU  
4. **Result Visualization & Saving**  
   - Draw bounding boxes for detected insects and save images to the output directory with the same filename as PNG  
5. **Logging**  
   - Record filename, detection status, count, and processing time (ms) to both terminal and a log file  
6. **Help Display**  
   - Provide usage instructions via `-h, --help` options

---

## 6. Non-Functional Requirements

- **Performance**: Combined inference and drawing time ≤ 1,000 ms per image (CPU environment)  
- **Reliability**: Continue processing remaining files on exceptions  
- **Portability**: Run within a Python virtual environment (venv/conda)  
- **Reproducibility**: Log model version and weight filename

---

## 7. Data Requirements

- **Input**: JPEG/PNG still images (any resolution)  
- **Output**: PNG images of the same resolution with bounding boxes  
- **Log**: CSV format (`filename, detected, count, time_ms`)

---

## 8. Testing & Evaluation Criteria

1. **Detection Accuracy**  
   - True positive rate ≥ 80%  
   - False positive rate ≤ 10%  
   - Validation on ≥ 20 sample images  
2. **Processing Time**  
   - Average processing time ≤ 1 second (CPU on WSL)  
3. **Stability**  
   - No crashes over 50 consecutive image processes

---

## 9. Constraints & Assumptions

- Pre-downloaded YOLOv8 pretrained weights available locally  
- Python environment set up in a virtual environment with required dependencies  
- No network required; fully on-device inference  
