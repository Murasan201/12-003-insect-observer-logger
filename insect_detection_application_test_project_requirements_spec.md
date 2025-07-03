# Requirements Specification Document

## 1. Project Overview

**Name**: Insect Detection Application Test Project (CPU Version)  
**Purpose**: Train a custom YOLOv8 model using insect datasets to detect beetles (specifically Japanese rhinoceros beetles) in still images through fine-tuning and visualize the results.

---

## 2. Scope

- **Input Images**: JPEG/PNG still images in a user-specified directory  
- **Detection Target**: Custom trained classes focusing on beetles (Japanese rhinoceros beetles)  
- **Training Data**: Insect datasets for YOLOv8 fine-tuning  
- **Output**: Images overlaid with bounding boxes where detections occur, saved to an output directory

---

## 3. Runtime Environment

### 3.1 Test Environment (Current Phase)
- **OS**: WSL2 on Windows 10/11 (Ubuntu 22.04 recommended)  
- **Hardware**: Host PC CPU (minimum quad-core recommended)  
- **Accelerator**: None (CPU-only inference)

### 3.2 Training Environment (Cloud-based)
- **Platform**: Google Colaboratory  
- **GPU**: T4 or V100 (free tier available)  
- **Runtime**: Python 3.10+ with CUDA support  
- **Storage**: Google Drive integration for dataset management  

### 3.3 Future Environment (Reference)
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

### 5.1 Model Training Requirements
1. **Dataset Preparation**  
   - Collect and prepare insect datasets (focusing on beetles)  
   - Convert datasets to YOLO format with proper annotations  
2. **Model Fine-tuning**  
   - Fine-tune YOLOv8 model using custom insect datasets  
   - Train specifically for Japanese rhinoceros beetle detection  
3. **Model Validation**  
   - Validate trained model performance on test datasets  
   - Generate training metrics and loss curves  

### 5.2 Detection Application Requirements
1. **Standalone Execution**  
   - Users run the script via `python detect_insect.py`  
2. **Directory Specification**  
   - Input and output directories specified via command-line arguments  
3. **Batch Inference**  
   - Perform sequential YOLO inference using custom trained model on CPU  
4. **Result Visualization & Saving**  
   - Draw bounding boxes for detected beetles and save images to the output directory with the same filename as PNG  
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

### 8.1 Training Performance
1. **Model Convergence**  
   - Training loss should decrease consistently  
   - Validation mAP@0.5 ≥ 0.7 for beetle detection  
2. **Training Stability**  
   - Complete training without crashes  
   - Generate reproducible results  

### 8.2 Detection Accuracy
1. **Beetle Detection Performance**  
   - True positive rate ≥ 85% for Japanese rhinoceros beetles  
   - False positive rate ≤ 5%  
   - Validation on ≥ 50 sample images including beetles  
2. **Processing Time**  
   - Average processing time ≤ 1 second (CPU on WSL)  
3. **Stability**  
   - No crashes over 50 consecutive image processes

---

## 9. Constraints & Assumptions

### 9.1 Training Phase
- Access to insect datasets (publicly available or collected)  
- Sufficient training time and computational resources  
- Proper dataset annotation and formatting  

### 9.2 Inference Phase
- Custom trained YOLOv8 weights available locally  
- Python environment set up in a virtual environment with required dependencies  
- No network required; fully on-device inference  

---

## 10. Training Data Requirements

### 10.1 Dataset Specifications
- **Primary Target**: Japanese rhinoceros beetles (Trypoxylus dichotomus)  
- **Secondary Targets**: Other beetle species for robust training  
- **Format**: YOLO format with bounding box annotations  
- **Minimum Size**: 500+ annotated images for training  
- **Image Quality**: High resolution (≥ 640x640 pixels recommended)  

### 10.2 Data Split
- **Training Set**: 70% of total dataset  
- **Validation Set**: 20% of total dataset  
- **Test Set**: 10% of total dataset  

### 10.3 Directory Structure
```
insect-detection-training/
├── datasets/
│   ├── raw/                    # Original unprocessed data
│   │   ├── images/            # Collected images
│   │   └── annotations/       # Original annotation files
│   ├── processed/             # YOLO format converted data
│   │   ├── images/
│   │   │   ├── train/         # Training images
│   │   │   ├── val/           # Validation images
│   │   │   └── test/          # Test images
│   │   └── labels/
│   │       ├── train/         # Training labels (.txt)
│   │       ├── val/           # Validation labels (.txt)
│   │       └── test/          # Test labels (.txt)
│   └── dataset.yaml           # YOLOv8 configuration file
├── weights/                   # Trained model weights
└── training_results/          # Training logs and metrics
```

### 10.4 File Format Requirements
- **Images**: JPEG/PNG format, consistent naming convention
- **Labels**: YOLO format (.txt files) with class_id, x_center, y_center, width, height (normalized coordinates)
- **Configuration**: dataset.yaml file specifying paths and class names
- **Naming**: Corresponding image and label files must have identical base names  

---

## 11. Model Training Workflow

### 11.1 Local Environment (Data Preparation)
1. **Data Collection & Preparation**  
   - Collect insect images from public datasets  
   - Annotate images with bounding boxes  
   - Convert to YOLO format  
   - Organize in specified directory structure  

### 11.2 Cloud Environment (Training Phase)
2. **Google Colab Setup**  
   - Upload dataset to Google Drive  
   - Set up Colab notebook with GPU runtime  
   - Install required dependencies (ultralytics, etc.)  
3. **Model Configuration**  
   - Configure YOLOv8 for custom classes  
   - Set up training parameters (epochs, batch size, etc.)  
4. **Training Execution**  
   - Fine-tune YOLOv8 on insect datasets using GPU  
   - Monitor training progress and loss curves  
   - Save training checkpoints  
5. **Model Evaluation**  
   - Validate model performance on test set  
   - Generate metrics and visualizations  
   - Export confusion matrix and performance reports  

### 11.3 Local Environment (Deployment Phase)
6. **Model Deployment**  
   - Download trained weights from Colab  
   - Integrate with local detection application  
   - Test inference performance on local CPU  

### 11.4 Development Workflow Benefits
- **GPU Acceleration**: Faster training (hours vs days)  
- **Cost Efficiency**: Free GPU access with Google Colab  
- **Scalability**: Easy to scale up with Colab Pro if needed  
- **Reproducibility**: Notebook-based training for consistent results  
