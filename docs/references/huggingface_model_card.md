# Beetle Detection YOLOv8 Model

## Model Description

This is a YOLOv8 Nano model fine-tuned for beetle detection, achieving 97.63% mAP@0.5 accuracy.

## Model Details

- **Architecture**: YOLOv8 Nano
- **Framework**: Ultralytics YOLOv8
- **Model Size**: 6.3MB
- **Performance**: 97.63% mAP@0.5, ~100ms inference time (CPU)
- **Classes**: 1 class (beetle)
- **Training Dataset**: 500 annotated beetle images

## Usage

### Quick Start
```python
from ultralytics import YOLO

# Load model
model = YOLO('best.pt')

# Run inference
results = model('path/to/image.jpg')
results[0].show()
```

### With the complete detection script
```bash
# Clone the companion repository
git clone https://github.com/Murasan201/insect-detection-training

# Download this model to weights/ directory
# Run detection
python detect_insect.py --input input_images/ --output output_images/
```

## Training Details

- **Training Images**: 400 images
- **Validation Images**: 50 images  
- **Test Images**: 50 images
- **Epochs**: 100
- **Precision**: 95.98%
- **Recall**: 93.05%

## Dataset Attribution

This model was trained using the Beetle Dataset by z Algae Bilby.
- **Source**: [Roboflow Beetle Dataset](https://universe.roboflow.com/z-algae-bilby/beetle/dataset/1)
- **License**: CC BY 4.0
- **Creator**: z Algae Bilby

## License

This model is derived from YOLOv8 (Ultralytics) and is licensed under AGPL-3.0.

## Citation

If you use this model in your research or project, please cite:

```bibtex
@misc{beetle-detection-yolov8,
  title={Beetle Detection YOLOv8 Model},
  author={Murasan},
  year={2025},
  url={https://huggingface.co/your-username/beetle-detection-yolov8}
}
```

## Companion Resources

- **Full Code Repository**: https://github.com/Murasan201/insect-detection-training
- **Training Notebook**: Available in the repository
- **Book Chapter**: [Your Book Title] - Chapter X

## Performance Metrics

| Metric | Value |
|--------|-------|
| mAP@0.5 | 97.63% |
| mAP@0.5:0.95 | 65.50% |
| Precision | 95.98% |
| Recall | 93.05% |
| Model Size | 6.3MB |
| Avg. Inference Time (CPU) | ~100ms |

## Intended Use

This model is designed for:
- Educational purposes and learning YOLOv8
- Beetle detection in still images
- CPU-optimized inference applications
- Research and development

## Limitations

- Trained specifically on beetle images
- May not generalize to other insect types
- Optimized for CPU inference (not GPU-optimized)
- Performance may vary with different image qualities

## Model Card Authors

- Murasan

## Model Card Contact

For questions about this model, please open an issue in the [companion repository](https://github.com/Murasan201/insect-detection-training).