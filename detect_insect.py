#!/usr/bin/env python3
"""
Insect Detection Application using YOLOv8

A CPU-based insect detection application that processes images in batch
and outputs visualization results with comprehensive logging.

Author: Generated with Claude Code
License: MIT
"""

import argparse
import csv
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from ultralytics import YOLO


def setup_logging(log_dir: Path) -> Tuple[logging.Logger, str]:
    """
    Setup logging configuration for both console and file output.
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        Tuple of logger instance and CSV log filename
    """
    # Create log directory if it doesn't exist
    log_dir.mkdir(exist_ok=True)
    
    # Setup console logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Create CSV log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"detection_log_{timestamp}.csv"
    csv_path = log_dir / csv_filename
    
    # Create CSV header
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'detected', 'count', 'time_ms'])
    
    logger.info(f"Logging initialized. CSV log: {csv_path}")
    return logger, str(csv_path)


def load_model(model_path: str, logger: logging.Logger) -> YOLO:
    """
    Load YOLOv8 model for inference.
    
    Args:
        model_path: Path to model weights file
        logger: Logger instance
        
    Returns:
        Loaded YOLO model
    """
    try:
        logger.info(f"Loading YOLOv8 model: {model_path}")
        model = YOLO(model_path)
        logger.info(f"Model loaded successfully. Classes: {len(model.names)}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        sys.exit(1)


def get_image_files(input_dir: Path, logger: logging.Logger) -> List[Path]:
    """
    Get all valid image files from input directory.
    
    Args:
        input_dir: Input directory path
        logger: Logger instance
        
    Returns:
        List of image file paths
    """
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    image_files = []
    
    for ext in valid_extensions:
        image_files.extend(input_dir.glob(f"*{ext}"))
        image_files.extend(input_dir.glob(f"*{ext.upper()}"))
    
    image_files.sort()
    logger.info(f"Found {len(image_files)} image files in {input_dir}")
    
    if not image_files:
        logger.warning(f"No image files found in {input_dir}")
    
    return image_files


def detect_objects(
    model: YOLO, 
    image_path: Path, 
    confidence_threshold: float = 0.25
) -> Tuple[np.ndarray, List[dict], bool]:
    """
    Perform object detection on a single image.
    
    Args:
        model: YOLO model instance
        image_path: Path to input image
        confidence_threshold: Minimum confidence for detections
        
    Returns:
        Tuple of (annotated_image, detections_list, has_detections)
    """
    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Perform inference with CPU device explicitly set
    results = model.predict(
        source=image,
        device='cpu',
        conf=confidence_threshold,
        verbose=False
    )
    
    detections = []
    has_detections = False
    
    # Process results
    for result in results:
        # Get the annotated image
        annotated_image = result.plot()
        
        # Extract detection information
        if result.boxes is not None and len(result.boxes) > 0:
            has_detections = True
            
            boxes = result.boxes.xyxy.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            
            for box, cls, conf in zip(boxes, classes, confidences):
                x1, y1, x2, y2 = map(int, box)
                class_name = model.names[int(cls)]
                
                detection = {
                    'class': class_name,
                    'confidence': float(conf),
                    'bbox': [x1, y1, x2, y2]
                }
                detections.append(detection)
        else:
            # No detections found, return original image
            annotated_image = image
    
    return annotated_image, detections, has_detections


def save_result_image(
    annotated_image: np.ndarray, 
    output_path: Path, 
    logger: logging.Logger
) -> bool:
    """
    Save annotated image to output directory.
    
    Args:
        annotated_image: Image with bounding boxes drawn
        output_path: Output file path
        logger: Logger instance
        
    Returns:
        True if save successful, False otherwise
    """
    try:
        cv2.imwrite(str(output_path), annotated_image)
        return True
    except Exception as e:
        logger.error(f"Failed to save image {output_path}: {e}")
        return False


def log_detection_result(
    csv_path: str,
    filename: str,
    detected: bool,
    count: int,
    processing_time: float,
    logger: logging.Logger
) -> None:
    """
    Log detection result to CSV file.
    
    Args:
        csv_path: Path to CSV log file
        filename: Image filename
        detected: Whether any objects were detected
        count: Number of detections
        processing_time: Processing time in milliseconds
        logger: Logger instance
    """
    try:
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([filename, detected, count, f"{processing_time:.1f}"])
    except Exception as e:
        logger.error(f"Failed to write to CSV log: {e}")


def process_images(
    model: YOLO,
    input_dir: Path,
    output_dir: Path,
    csv_log_path: str,
    logger: logging.Logger,
    confidence_threshold: float = 0.25
) -> None:
    """
    Process all images in the input directory.
    
    Args:
        model: YOLO model instance
        input_dir: Input directory path
        output_dir: Output directory path
        csv_log_path: Path to CSV log file
        logger: Logger instance
        confidence_threshold: Minimum confidence for detections
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Get all image files
    image_files = get_image_files(input_dir, logger)
    
    if not image_files:
        logger.warning("No images to process")
        return
    
    total_images = len(image_files)
    successful_processed = 0
    total_detections = 0
    
    logger.info(f"Starting batch processing of {total_images} images...")
    
    for i, image_path in enumerate(image_files, 1):
        try:
            # Record start time
            start_time = time.time()
            
            logger.info(f"Processing [{i}/{total_images}]: {image_path.name}")
            
            # Perform detection
            annotated_image, detections, has_detections = detect_objects(
                model, image_path, confidence_threshold
            )
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Generate output filename (always save as PNG)
            output_filename = image_path.stem + ".png"
            output_path = output_dir / output_filename
            
            # Save result image
            if save_result_image(annotated_image, output_path, logger):
                successful_processed += 1
                detection_count = len(detections)
                total_detections += detection_count
                
                # Log results
                log_detection_result(
                    csv_log_path,
                    image_path.name,
                    has_detections,
                    detection_count,
                    processing_time,
                    logger
                )
                
                # Console output
                if has_detections:
                    classes_detected = [d['class'] for d in detections]
                    logger.info(
                        f"✓ Detected {detection_count} objects: "
                        f"{', '.join(set(classes_detected))} "
                        f"(Time: {processing_time:.1f}ms)"
                    )
                else:
                    logger.info(f"✓ No objects detected (Time: {processing_time:.1f}ms)")
            
        except Exception as e:
            logger.error(f"Failed to process {image_path.name}: {e}")
            # Log failed processing
            log_detection_result(
                csv_log_path,
                image_path.name,
                False,
                0,
                0.0,
                logger
            )
    
    # Summary
    logger.info("=" * 60)
    logger.info("PROCESSING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total images: {total_images}")
    logger.info(f"Successfully processed: {successful_processed}")
    logger.info(f"Failed: {total_images - successful_processed}")
    logger.info(f"Total detections: {total_detections}")
    logger.info(f"CSV log saved to: {csv_log_path}")
    logger.info("=" * 60)


def main():
    """Main function to run the insect detection application."""
    parser = argparse.ArgumentParser(
        description="Insect Detection Application using YOLOv8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python detect_insect.py --input input_images/ --output output_images/
  python detect_insect.py --input input_images/ --output results/ --model yolov8s.pt
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input directory containing images to process'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for processed images'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8n.pt',
        help='Path to YOLOv8 model weights (default: yolov8n.pt)'
    )
    
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='Confidence threshold for detections (default: 0.25)'
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        default='logs',
        help='Directory for log files (default: logs)'
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    log_dir = Path(args.log_dir)
    
    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"Error: '{input_dir}' is not a directory")
        sys.exit(1)
    
    # Setup logging
    logger, csv_log_path = setup_logging(log_dir)
    
    # Load model
    model = load_model(args.model, logger)
    
    # Log model information
    logger.info(f"Model classes: {list(model.names.values())}")
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Confidence threshold: {args.conf}")
    
    # Process images
    try:
        process_images(
            model=model,
            input_dir=input_dir,
            output_dir=output_dir,
            csv_log_path=csv_log_path,
            logger=logger,
            confidence_threshold=args.conf
        )
        logger.info("Processing completed successfully")
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()