# System Specification Document

**Project**: Insect Detection Training Project  
**Version**: 1.0  
**Date**: 2025-07-03  
**Author**: Development Team  

---

## 1. Executive Summary

This document provides a comprehensive technical specification for the Insect Detection Training Project, a YOLOv8-based machine learning system designed to train custom models for beetle detection. The system encompasses model training, validation, and deployment workflows optimized for CPU-based inference environments.

---

## 2. System Overview

### 2.1 Purpose
The system is designed to:
- Train custom YOLOv8 models for insect (beetle) detection
- Provide efficient CPU-based inference capabilities
- Support automated training workflows with comprehensive logging
- Enable model deployment in resource-constrained environments

### 2.2 Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Training Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│  Dataset → Preprocessing → Training → Validation → Export  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Inference Pipeline                       │
├─────────────────────────────────────────────────────────────┤
│    Input Images → Detection → Visualization → Output       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. System Components

### 3.1 Core Modules

#### 3.1.1 Training Module (`train_yolo.py`)
**Purpose**: Automated YOLOv8 model training and fine-tuning

**Key Features**:
- Pre-trained model initialization
- Custom dataset integration
- Automated training pipeline
- Real-time progress monitoring
- Model validation and metrics reporting

**Technical Specifications**:
- **Framework**: Ultralytics YOLOv8
- **Supported Models**: YOLOv8n, YOLOv8s, YOLOv8m, YOLOv8l, YOLOv8x
- **Input Format**: YOLO format annotations
- **Output Format**: PyTorch (.pt), ONNX, TorchScript

#### 3.1.2 Detection Module (`detect_insect.py`)
**Purpose**: Batch image processing and insect detection

**Key Features**:
- Multi-format image support (JPEG, PNG)
- Batch processing capabilities
- Bounding box visualization
- Performance metrics logging

---

## 4. Training System Detailed Specification

### 4.1 Training Script Architecture

#### 4.1.1 Function Overview

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `setup_logging()` | Initialize logging system | None | Logger instance |
| `validate_dataset()` | Verify dataset structure | Dataset path | Boolean validation result |
| `check_system_requirements()` | System compatibility check | None | System info logs |
| `train_model()` | Execute model training | Training parameters | Trained model, results |
| `validate_model()` | Model performance evaluation | Model, dataset | Validation metrics |
| `export_model()` | Model format conversion | Model, formats | Exported model files |

#### 4.1.2 Training Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--data` | str | Required | Path to dataset configuration (data.yaml) |
| `--model` | str | yolov8n.pt | Pre-trained model selection |
| `--epochs` | int | 100 | Number of training epochs |
| `--batch` | int | 16 | Training batch size |
| `--imgsz` | int | 640 | Input image size (pixels) |
| `--device` | str | auto | Hardware device (auto/cpu/gpu) |
| `--project` | str | training_results | Output directory name |
| `--name` | str | beetle_detection | Experiment identifier |
| `--export` | bool | False | Enable model export |
| `--validate` | bool | True | Enable post-training validation |

### 4.2 Training Workflow

#### 4.2.1 Initialization Phase
1. **Logging Setup**
   - Create timestamped log files in `logs/` directory
   - Configure dual output (file + console)
   - Set logging level to INFO

2. **System Validation**
   - Python version verification
   - PyTorch installation check
   - CUDA availability detection
   - GPU enumeration and specifications
   - OpenCV version confirmation

3. **Dataset Validation**
   - Verify `data.yaml` existence
   - Check directory structure integrity
   - Count files in train/valid/test splits
   - Validate image-label correspondence

#### 4.2.2 Training Phase
1. **Model Initialization**
   - Load pre-trained YOLOv8 weights
   - Configure model architecture
   - Set training hyperparameters

2. **Training Execution**
   - Batch data loading and augmentation
   - Forward/backward propagation
   - Loss calculation and optimization
   - Checkpoint saving (every 10 epochs)
   - Validation set evaluation

3. **Progress Monitoring**
   - Real-time loss tracking
   - Validation metrics computation
   - Training time measurement
   - Resource utilization logging

#### 4.2.3 Validation Phase
1. **Performance Metrics**
   - mAP@0.5 (Mean Average Precision at IoU 0.5)
   - mAP@0.5:0.95 (Mean Average Precision across IoU thresholds)
   - Precision (True Positives / (True Positives + False Positives))
   - Recall (True Positives / (True Positives + False Negatives))

2. **Output Generation**
   - Confusion matrix visualization
   - Training/validation curves
   - Sample detection visualizations
   - Model performance summary

#### 4.2.4 Export Phase
1. **Format Conversion**
   - ONNX export for cross-platform deployment
   - TorchScript export for production optimization
   - Model weight extraction

2. **File Organization**
   - Best model weights (`best.pt`)
   - Latest checkpoint (`last.pt`)
   - Training configuration backup
   - Results visualization files

---

## 5. Dataset Specifications

### 5.1 Dataset Structure
```
datasets/
├── train/
│   ├── images/          # 400 training images
│   └── labels/          # 400 YOLO format labels
├── valid/
│   ├── images/          # 50 validation images
│   └── labels/          # 50 YOLO format labels
├── test/
│   ├── images/          # 50 test images
│   └── labels/          # 50 test labels
└── data.yaml            # Dataset configuration
```

### 5.2 Data Format Requirements

#### 5.2.1 Image Specifications
- **Formats**: JPEG, PNG
- **Resolution**: Minimum 640x640 pixels recommended
- **Color Space**: RGB
- **File Naming**: Consistent with corresponding label files

#### 5.2.2 Label Format (YOLO)
```
class_id x_center y_center width height
```
- **class_id**: Integer (0 for 'beetle')
- **Coordinates**: Normalized (0.0 to 1.0)
- **File Extension**: `.txt`

#### 5.2.3 Configuration File (data.yaml)
```yaml
train: ./train/images
val: ./valid/images
test: ./test/images

nc: 1
names: ['beetle']

roboflow:
  workspace: z-algae-bilby
  project: beetle
  version: 1
  license: CC BY 4.0
  url: https://universe.roboflow.com/z-algae-bilby/beetle/dataset/1
```

---

## 6. System Requirements

### 6.1 Hardware Requirements

#### 6.1.1 Minimum Requirements
- **CPU**: Quad-core processor (Intel i5 or AMD Ryzen 5 equivalent)
- **RAM**: 8GB system memory
- **Storage**: 10GB free space for datasets and models
- **GPU**: Optional (CUDA-compatible for accelerated training)

#### 6.1.2 Recommended Requirements
- **CPU**: 8-core processor (Intel i7 or AMD Ryzen 7)
- **RAM**: 16GB+ system memory
- **Storage**: 50GB+ SSD storage
- **GPU**: NVIDIA GPU with 6GB+ VRAM (RTX 3060 or better)

### 6.2 Software Requirements

#### 6.2.1 Operating System
- **Primary**: Ubuntu 22.04 LTS (WSL2 on Windows 10/11)
- **Alternative**: macOS 12+, Windows 10/11 with WSL2
- **Python**: 3.9+ (tested with 3.10.12)

#### 6.2.2 Dependencies (Verified Versions)
```
# Core ML Frameworks
torch==2.7.1                    # Deep Learning Framework
torchvision==0.22.1             # Computer Vision
ultralytics==8.3.162            # YOLOv8 Implementation

# Computer Vision & Image Processing
opencv-python==4.11.0.86        # Computer Vision Library
numpy==2.2.6                    # Numerical Computing
pandas==2.3.0                   # Data Analysis
matplotlib==3.10.3              # Plotting & Visualization
pillow>=11.3.0                  # Image Processing

# Additional Dependencies
ultralytics-thop==2.0.14        # Model Profiling
pyyaml>=5.3.1                   # Configuration Files
tqdm>=4.65.0                    # Progress Bars
```

#### 6.2.3 Installation Commands
```bash
# Install core dependencies
pip3 install torch torchvision ultralytics opencv-python

# Or install all requirements
pip3 install -r requirements.txt
```

#### 6.2.4 Current Environment Status
- **System**: Linux WSL2 (Ubuntu) x86_64
- **Python**: 3.10.12 (System Level)
- **Package Installation**: User-level (~/.local/lib/python3.10/site-packages/)
- **Last Verified**: 2025-07-04

---

## 7. Performance Specifications

### 7.1 Training Performance

#### 7.1.1 Target Metrics
- **Training Time**: ≤ 2 hours for 100 epochs (GPU environment)
- **Memory Usage**: ≤ 8GB RAM during training
- **Model Convergence**: Loss stabilization within 50-80 epochs
- **Validation mAP@0.5**: ≥ 0.7 for beetle detection

#### 7.1.2 Achieved Performance (2025-07-04)
**🏆 Exceptional Results Achieved:**
- **Final mAP@0.5**: 0.9763 (97.63%) - **39.4% above target**
- **mAP@0.5:0.95**: 0.6550 (65.50%)
- **Precision**: 0.9598 (95.98%)
- **Recall**: 0.9305 (93.05%)
- **Training Platform**: Google Colab (GPU accelerated)
- **Model Size**: YOLOv8 Nano (best.pt: 6.3MB)
- **Training Status**: Production-ready quality

#### 7.1.3 Hardware-Specific Performance
| Configuration | Training Time (100 epochs) | Memory Usage | Batch Size |
|---------------|----------------------------|--------------|------------|
| CPU Only | 8-12 hours | 4-6 GB | 8-16 |
| RTX 3060 | 1-2 hours | 6-8 GB | 32-64 |
| RTX 4080 | 30-60 minutes | 8-12 GB | 64-128 |

### 7.2 Inference Performance

#### 7.2.1 Target Specifications
- **Processing Time**: ≤ 1,000ms per image (CPU inference)
- **Memory Efficiency**: ≤ 2GB RAM during inference
- **Accuracy Targets**:
  - True Positive Rate: ≥ 85%
  - False Positive Rate: ≤ 5%
  - Precision: ≥ 0.8
  - Recall: ≥ 0.8

#### 7.2.2 Achieved Local Inference Performance (2025-07-04)
**🚀 Outstanding Local Performance:**
- **Average Processing Time**: ~100ms per image (**90% faster than target**)
- **Processing Range**: 63.4ms - 121.2ms per image
- **Test Results**: 5/5 images processed successfully (100% success rate)
- **Total Detections**: 9 beetles detected across 5 images
- **System**: Linux WSL2, Python 3.10.12, CPU-only inference
- **Model**: best.pt (6.3MB YOLOv8 Nano)
- **Memory Usage**: Minimal system impact

---

## 8. Output Specifications

### 8.1 Training Outputs

#### 8.1.1 Model Files
- **best.pt**: Best performing model weights
- **last.pt**: Final epoch weights
- **Model exports**: ONNX, TorchScript formats

#### 8.1.2 Visualization Files
- **results.png**: Training/validation curves
- **confusion_matrix.png**: Classification performance matrix
- **labels.jpg**: Ground truth label distribution
- **predictions.jpg**: Model prediction samples

#### 8.1.3 Log Files
- **Training logs**: Timestamped training progress
- **CSV metrics**: Epoch-by-epoch performance data
- **System logs**: Hardware utilization and errors

### 8.2 File Organization
```
training_results/
└── beetle_detection/
    ├── weights/
    │   ├── best.pt
    │   └── last.pt
    ├── plots/
    │   ├── results.png
    │   ├── confusion_matrix.png
    │   └── predictions.jpg
    └── logs/
        └── training_YYYYMMDD_HHMMSS.log
```

---

## 9. Error Handling and Logging

### 9.1 Error Classification

#### 9.1.1 Critical Errors
- Dataset validation failures
- Model loading errors
- CUDA out-of-memory errors
- File system permission issues

#### 9.1.2 Warning Conditions
- Low available memory
- Slow training convergence
- Missing optional dependencies
- Suboptimal hardware configuration

### 9.2 Logging Specifications

#### 9.2.1 Log Levels
- **INFO**: Normal operation progress
- **WARNING**: Non-critical issues
- **ERROR**: Recoverable failures
- **CRITICAL**: System-stopping errors

#### 9.2.2 Log Format
```
YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE
```

#### 9.2.3 Log Rotation
- New log file per training session
- Timestamp-based naming convention
- Automatic cleanup of old logs (>30 days)

---

## 10. Security Considerations

### 10.1 Data Security
- Dataset files excluded from version control
- No sensitive information in configuration files
- Secure handling of model weights

### 10.2 System Security
- Input validation for all user parameters
- Safe file path handling
- Memory usage monitoring and limits

---

## 11. Deployment Guidelines

### 11.1 Development Environment Setup
1. Clone repository from GitHub
2. Create Python virtual environment
3. Install dependencies from requirements.txt
4. Download and prepare dataset
5. Verify system requirements

### 11.2 Training Execution
```bash
# Basic training command
python train_yolo.py --data datasets/data.yaml --epochs 100

# Production training with custom parameters
python train_yolo.py \
    --data datasets/data.yaml \
    --model yolov8s.pt \
    --epochs 200 \
    --batch 32 \
    --imgsz 640 \
    --device 0 \
    --export
```

### 11.3 Model Deployment
1. Export trained model to ONNX format
2. Optimize for target hardware platform
3. Integrate with inference application
4. Validate performance on test dataset

---

## 12. Maintenance and Updates

### 12.1 Model Retraining
- Recommended frequency: Monthly with new data
- Version control for model weights
- Performance comparison with previous versions

### 12.2 System Updates
- Regular dependency updates
- YOLOv8 framework version monitoring
- Security patch application

---

## 13. Testing and Validation

### 13.1 Unit Testing
- Dataset validation functions
- Model loading/saving operations
- Configuration file parsing
- Error handling mechanisms

### 13.2 Integration Testing
- End-to-end training pipeline
- Model export functionality
- Cross-platform compatibility
- Performance benchmarking

### 13.3 Acceptance Testing
- Model accuracy validation
- Performance requirement verification
- User interface testing
- Documentation completeness

---

## 14. Appendices

### 14.1 Command Reference
```bash
# Display help information
python train_yolo.py --help

# Quick training with minimal parameters
python train_yolo.py --data datasets/data.yaml --epochs 50

# High-quality training with export
python train_yolo.py --data datasets/data.yaml --model yolov8m.pt --epochs 200 --export

# CPU-only training
python train_yolo.py --data datasets/data.yaml --device cpu --batch 8
```

### 14.2 Troubleshooting Guide

#### 14.2.1 Common Issues
- **"Dataset not found"**: Verify dataset directory structure
- **"CUDA out of memory"**: Reduce batch size or use CPU
- **"Permission denied"**: Check file system permissions
- **"Import error"**: Reinstall dependencies

#### 14.2.2 Performance Optimization
- Use SSD storage for faster data loading
- Optimize batch size based on available memory
- Enable mixed precision training for GPU speedup
- Close unnecessary applications during training

---

*Document Version: 1.0*  
*Last Updated: 2025-07-03*  
*Contact: Development Team*