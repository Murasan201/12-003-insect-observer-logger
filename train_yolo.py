#!/usr/bin/env python3
"""
YOLOv8 Training Script for Insect Detection

This script performs fine-tuning of YOLOv8 models on custom insect datasets.
Designed for beetle detection using the Roboflow dataset.

Usage:
    python train_yolo.py --data datasets/data.yaml --epochs 100
    python train_yolo.py --data datasets/data.yaml --epochs 50 --batch 16 --imgsz 640

Requirements:
    - ultralytics
    - torch
    - opencv-python
    - numpy
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from ultralytics import YOLO
    import torch
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Error: Required library not installed: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


def setup_logging():
    """Setup logging configuration for training process."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"training_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def validate_dataset(data_path):
    """
    Validate dataset structure and configuration.
    
    Args:
        data_path (str): Path to data.yaml file
        
    Returns:
        bool: True if dataset is valid, False otherwise
    """
    data_file = Path(data_path)
    if not data_file.exists():
        logging.error(f"Dataset configuration not found: {data_path}")
        return False
    
    # Check if dataset directories exist
    dataset_dir = data_file.parent
    required_dirs = ["train/images", "train/labels", "valid/images", "valid/labels"]
    
    for dir_path in required_dirs:
        full_path = dataset_dir / dir_path
        if not full_path.exists():
            logging.error(f"Required directory not found: {full_path}")
            return False
        
        # Count files in directory
        files = list(full_path.glob("*"))
        if not files:
            logging.error(f"No files found in directory: {full_path}")
            return False
        
        logging.info(f"Found {len(files)} files in {dir_path}")
    
    logging.info("Dataset validation successful")
    return True


def check_system_requirements():
    """Check system requirements and log system information."""
    logger = logging.getLogger(__name__)
    
    # Check Python version
    python_version = sys.version
    logger.info(f"Python version: {python_version}")
    
    # Check PyTorch version and CUDA availability
    torch_version = torch.__version__
    cuda_available = torch.cuda.is_available()
    device_count = torch.cuda.device_count() if cuda_available else 0
    
    logger.info(f"PyTorch version: {torch_version}")
    logger.info(f"CUDA available: {cuda_available}")
    logger.info(f"GPU count: {device_count}")
    
    if cuda_available:
        for i in range(device_count):
            gpu_name = torch.cuda.get_device_name(i)
            logger.info(f"GPU {i}: {gpu_name}")
    else:
        logger.info("Training will use CPU only")
    
    # Check OpenCV version
    cv2_version = cv2.__version__
    logger.info(f"OpenCV version: {cv2_version}")


def train_model(data_path, model_name="yolov8n.pt", epochs=100, batch_size=16, 
                img_size=640, device="auto", project="training_results", 
                name="beetle_detection"):
    """
    Train YOLOv8 model with specified parameters.
    
    Args:
        data_path (str): Path to dataset configuration file
        model_name (str): Pre-trained model to use
        epochs (int): Number of training epochs
        batch_size (int): Batch size for training
        img_size (int): Image size for training
        device (str): Device to use for training
        project (str): Project directory name
        name (str): Experiment name
        
    Returns:
        YOLO: Trained model instance
    """
    logger = logging.getLogger(__name__)
    
    logger.info("Starting YOLOv8 training process")
    logger.info(f"Model: {model_name}")
    logger.info(f"Dataset: {data_path}")
    logger.info(f"Epochs: {epochs}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Image size: {img_size}")
    logger.info(f"Device: {device}")
    
    try:
        # Load pre-trained model
        logger.info(f"Loading pre-trained model: {model_name}")
        model = YOLO(model_name)
        
        # Start training
        start_time = time.time()
        logger.info("Training started...")
        
        results = model.train(
            data=data_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=img_size,
            device=device,
            project=project,
            name=name,
            save=True,
            save_period=10,  # Save checkpoint every 10 epochs
            val=True,
            plots=True,
            verbose=True
        )
        
        training_time = time.time() - start_time
        logger.info(f"Training completed in {training_time:.2f} seconds")
        logger.info(f"Results saved to: {project}/{name}")
        
        return model, results
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


def validate_model(model, data_path):
    """
    Validate trained model on test dataset.
    
    Args:
        model (YOLO): Trained model instance
        data_path (str): Path to dataset configuration
        
    Returns:
        dict: Validation results
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting model validation...")
        
        # Run validation
        validation_results = model.val(data=data_path)
        
        # Log key metrics
        if hasattr(validation_results, 'box'):
            box_metrics = validation_results.box
            logger.info(f"mAP@0.5: {box_metrics.map50:.4f}")
            logger.info(f"mAP@0.5:0.95: {box_metrics.map:.4f}")
            logger.info(f"Precision: {box_metrics.mp:.4f}")
            logger.info(f"Recall: {box_metrics.mr:.4f}")
        
        logger.info("Model validation completed")
        return validation_results
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise


def export_model(model, formats=None, project="weights", name="best_model"):
    """
    Export trained model to various formats.
    
    Args:
        model (YOLO): Trained model instance
        formats (list): List of export formats
        project (str): Export directory
        name (str): Export filename prefix
    """
    if formats is None:
        formats = ["onnx", "torchscript"]
    
    logger = logging.getLogger(__name__)
    
    # Create weights directory
    weights_dir = Path(project)
    weights_dir.mkdir(exist_ok=True)
    
    try:
        for format_type in formats:
            logger.info(f"Exporting model to {format_type} format...")
            model.export(format=format_type)
            logger.info(f"Model exported to {format_type} format successfully")
    
    except Exception as e:
        logger.error(f"Model export failed: {str(e)}")


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="YOLOv8 Training for Insect Detection")
    
    # Required arguments
    parser.add_argument("--data", type=str, required=True,
                        help="Path to dataset configuration file (data.yaml)")
    
    # Optional arguments
    parser.add_argument("--model", type=str, default="yolov8n.pt",
                        help="Pre-trained model to use (default: yolov8n.pt)")
    parser.add_argument("--epochs", type=int, default=100,
                        help="Number of training epochs (default: 100)")
    parser.add_argument("--batch", type=int, default=16,
                        help="Batch size for training (default: 16)")
    parser.add_argument("--imgsz", type=int, default=640,
                        help="Image size for training (default: 640)")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device to use (auto, cpu, 0, 1, etc.)")
    parser.add_argument("--project", type=str, default="training_results",
                        help="Project directory name (default: training_results)")
    parser.add_argument("--name", type=str, default="beetle_detection",
                        help="Experiment name (default: beetle_detection)")
    parser.add_argument("--export", action="store_true",
                        help="Export model after training")
    parser.add_argument("--validate", action="store_true", default=True,
                        help="Run validation after training (default: True)")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("YOLOv8 Insect Detection Training Script")
    logger.info("=" * 60)
    
    # Check system requirements
    check_system_requirements()
    
    # Validate dataset
    if not validate_dataset(args.data):
        logger.error("Dataset validation failed. Exiting.")
        sys.exit(1)
    
    try:
        # Train model
        model, train_results = train_model(
            data_path=args.data,
            model_name=args.model,
            epochs=args.epochs,
            batch_size=args.batch,
            img_size=args.imgsz,
            device=args.device,
            project=args.project,
            name=args.name
        )
        
        # Validate model
        if args.validate:
            validation_results = validate_model(model, args.data)
        
        # Export model
        if args.export:
            export_model(model, project="weights", name="beetle_detection_model")
        
        logger.info("Training pipeline completed successfully!")
        logger.info(f"Model weights saved to: {args.project}/{args.name}/weights/")
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()