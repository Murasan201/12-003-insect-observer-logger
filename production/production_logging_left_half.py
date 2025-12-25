#!/usr/bin/env python3
"""
左半分エリア検出専用ロギングスクリプト
Camera Module 3 Wide用の昆虫検出（画面左半分のみ）
"""

import argparse
import sys
import time
import csv
import json
from pathlib import Path
from datetime import datetime
import signal

try:
    from picamera2 import Picamera2
    from libcamera import controls
    import cv2
    import numpy as np
    from ultralytics import YOLO
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    sys.exit(1)

# グローバル変数
picam2 = None
running = True
csv_writer = None
csv_file = None

def signal_handler(sig, frame):
    """Ctrl+Cハンドラ"""
    global running
    print("\nStopping logging test...")
    running = False

def distance_to_lens_position(distance_cm, max_lens=32.0):
    """距離(cm)をCamera Module 3 Wide用のレンズ位置に変換"""
    if distance_cm <= 5:
        return max_lens
    elif distance_cm >= 100:
        return 0.0
    else:
        import math
        log_distance = math.log10(distance_cm / 5)
        lens_pos = max_lens * (1 - log_distance / math.log10(20))
        return max(0.0, min(max_lens, lens_pos))

def setup_logging(output_dir: Path):
    """ログファイルのセットアップ"""
    global csv_writer, csv_file
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # タイムスタンプ付きファイル名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = output_dir / f"left_half_detection_log_{timestamp}.csv"
    metadata_path = output_dir / f"left_half_metadata_{timestamp}.json"
    
    # CSVファイル作成
    csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    
    # ヘッダー行を書き込み（検出エリア情報追加）
    csv_writer.writerow([
        'timestamp', 'observation_number', 'detection_count', 'has_detection',
        'class_names', 'confidence_values', 'bbox_coordinates',
        'center_x', 'center_y', 'bbox_width', 'bbox_height', 'area',
        'detection_area', 'processing_time_ms', 'image_saved', 'image_filename'
    ])
    csv_file.flush()
    
    # メタデータファイル作成
    metadata = {
        'start_time': datetime.now().isoformat(),
        'detection_area': 'left_half',
        'area_description': 'Only left 50% of camera view is monitored',
        'log_file': str(csv_path),
        'system_info': {
            'camera': 'Camera Module 3 Wide NoIR',
            'platform': 'Raspberry Pi'
        }
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return csv_path, metadata_path

def save_detection_to_csv(observation_num, detections, processing_time, image_saved=False, image_filename=None):
    """検出結果をCSVに保存（左半分検出情報付き）"""
    global csv_writer, csv_file
    
    if not csv_writer:
        return
    
    timestamp = datetime.now().isoformat()
    detection_count = len(detections) if detections else 0
    has_detection = detection_count > 0
    
    if has_detection:
        class_names = [d['class'] for d in detections]
        confidence_values = [f"{d['confidence']:.3f}" for d in detections]
        bbox_coords = [f"({d['x1']:.0f},{d['y1']:.0f},{d['x2']:.0f},{d['y2']:.0f})" for d in detections]
        
        centers_x = [f"{d['center_x']:.1f}" for d in detections]
        centers_y = [f"{d['center_y']:.1f}" for d in detections]
        widths = [f"{d['width']:.1f}" for d in detections]
        heights = [f"{d['height']:.1f}" for d in detections]
        areas = [f"{d['area']:.1f}" for d in detections]
        
        class_names_str = ';'.join(class_names)
        confidence_str = ';'.join(confidence_values)
        bbox_str = ';'.join(bbox_coords)
        center_x_str = ';'.join(centers_x)
        center_y_str = ';'.join(centers_y)
        width_str = ';'.join(widths)
        height_str = ';'.join(heights)
        area_str = ';'.join(areas)
    else:
        class_names_str = ''
        confidence_str = ''
        bbox_str = ''
        center_x_str = ''
        center_y_str = ''
        width_str = ''
        height_str = ''
        area_str = ''
    
    row = [
        timestamp,
        observation_num,
        detection_count,
        has_detection,
        class_names_str,
        confidence_str,
        bbox_str,
        center_x_str,
        center_y_str,
        width_str,
        height_str,
        area_str,
        'left_half',  # 検出エリア情報
        f"{processing_time:.1f}",
        image_saved,
        image_filename or ''
    ]
    
    csv_writer.writerow(row)
    csv_file.flush()

def test_logging_left_half(
    model_path: str = '../weights/best.pt',
    confidence: float = 0.3,
    width: int = 2304,
    height: int = 1296,
    focus_distance: float = 20.0,
    interval: int = 10,
    duration: int = 60,
    save_images: bool = False,
    output_dir: str = None,
    show_boundary: bool = False,
    exposure_value: float = -0.5,
    contrast: float = 2.0,
    brightness: float = 0.0
):
    """左半分検出ロギング機能"""
    global picam2, running
    
    # デフォルトの出力ディレクトリ
    if output_dir is None:
        script_dir = Path(__file__).parent
        output_path = script_dir / "insect_detection_logs"
    else:
        output_path = Path(output_dir)
    
    # ログ設定
    csv_path, metadata_path = setup_logging(output_path)
    
    # モデル読み込み
    print(f"\nLoading model: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"Model loaded. Classes: {model.names}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return False
    
    # Picamera2初期化
    print(f"\nInitializing Picamera2...")
    try:
        picam2 = Picamera2()
        
        # カメラ設定
        sensor_resolution = picam2.sensor_resolution
        print(f"Sensor resolution: {sensor_resolution}")
        print(f"Using binned sensor mode: {width}x{height} for full wide-angle coverage")
        print(f"Detection area: LEFT HALF ONLY (0 to {width//2} pixels)")
        
        config = picam2.create_preview_configuration(
            main={"size": (width, height), "format": "RGB888"},
            buffer_count=4
        )
        picam2.configure(config)
        
        # カメラ開始
        print("Starting camera...")
        picam2.start()
        time.sleep(2)
        
        # フォーカス設定
        lens_controls = picam2.camera_controls.get("LensPosition")
        if lens_controls:
            lp_min, lp_max, lp_default = lens_controls
        else:
            lp_min, lp_max, lp_default = 0.0, 32.0, 1.0
        
        if focus_distance == 0:
            print(f"Setting auto focus mode...")
            picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
            print("Auto focus mode enabled")
            time.sleep(2.0)
        else:
            print(f"Setting manual focus for {focus_distance}cm...")
            target_lens_pos = distance_to_lens_position(focus_distance, lp_max)
            print(f"Target lens position: {target_lens_pos:.1f}")
            picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
            time.sleep(0.5)
            picam2.set_controls({"LensPosition": float(target_lens_pos)})
            time.sleep(1.0)
        
        # 露出・コントラスト設定
        if exposure_value != 0.0:
            print(f"Setting exposure compensation: {exposure_value}")
            picam2.set_controls({"ExposureValue": exposure_value})
        
        if contrast != 1.0:
            print(f"Setting contrast: {contrast}")
            picam2.set_controls({"Contrast": contrast})
        
        if brightness != 0.0:
            print(f"Setting brightness: {brightness}")
            picam2.set_controls({"Brightness": brightness})
        
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return False
    
    # メタデータ更新
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    metadata.update({
        'focus_mode': 'auto' if focus_distance == 0 else 'manual',
        'focus_distance_cm': focus_distance if focus_distance > 0 else None,
        'model_path': model_path,
        'confidence_threshold': confidence,
        'resolution': f"{width}x{height}",
        'detection_width': width // 2,
        'interval_seconds': interval,
        'duration_seconds': duration,
        'save_images': save_images
    })
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*50)
    print("Starting LEFT HALF detection logging")
    print(f"Detection area: 0 to {width//2} pixels (left half)")
    print(f"Interval: {interval} seconds")
    print(f"Duration: {duration} seconds")
    print(f"Save images: {save_images}")
    print("="*50 + "\n")
    
    # シグナルハンドラ設定
    signal.signal(signal.SIGINT, signal_handler)
    
    # 画像保存ディレクトリ
    if save_images:
        script_dir = Path(__file__).parent
        images_dir = script_dir / "images"
        images_dir.mkdir(exist_ok=True)
        print(f"Images will be saved to: {images_dir}")
    
    observation_count = 0
    start_time = time.time()
    total_detections = 0
    
    # 左半分の境界線（X座標）
    boundary_x = width // 2
    
    try:
        while running:
            obs_start = time.time()
            
            # フレーム取得
            frame = picam2.capture_array()
            if frame is None:
                print(f"[WARNING] Frame capture failed, skipping...")
                time.sleep(1)
                continue
            
            observation_count += 1
            
            # 左半分のみを切り出して検出
            left_half_frame = frame[:, :boundary_x]
            
            # YOLOv8検出（左半分のみ）
            results = model.predict(
                source=left_half_frame,
                device='cpu',
                conf=confidence,
                verbose=False
            )
            
            # 処理時間
            processing_time = (time.time() - obs_start) * 1000
            
            # 検出結果処理
            detections = []
            if results[0].boxes is not None:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # 左半分での座標なので、そのまま使用
                    # （元の画像での座標は同じ）
                    
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    bbox_width = x2 - x1
                    bbox_height = y2 - y1
                    area = bbox_width * bbox_height
                    
                    detection = {
                        'class': model.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                        'center_x': center_x,
                        'center_y': center_y,
                        'width': bbox_width,
                        'height': bbox_height,
                        'area': area
                    }
                    detections.append(detection)
                    total_detections += 1
            
            # 画像保存（オプション）
            image_saved = False
            image_filename = None
            if save_images and detections:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                image_filename = f"left_half_detection_{timestamp}.jpg"
                image_path = images_dir / image_filename
                
                # 全体画像に検出結果を描画
                annotated_frame = frame.copy()
                
                # 境界線を描画（オプション）
                if show_boundary:
                    cv2.line(annotated_frame, (boundary_x, 0), (boundary_x, height), 
                            (255, 0, 0), 2)
                    cv2.putText(annotated_frame, "Detection Area", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                # 検出結果を描画
                for det in detections:
                    x1, y1, x2, y2 = int(det['x1']), int(det['y1']), int(det['x2']), int(det['y2'])
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{det['class']} {det['confidence']:.2f}"
                    cv2.putText(annotated_frame, label, (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # BGRに変換して保存
                annotated_frame_bgr = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(image_path), annotated_frame_bgr)
                image_saved = True
            
            # CSVに保存
            try:
                save_detection_to_csv(
                    observation_count,
                    detections,
                    processing_time,
                    image_saved,
                    image_filename
                )
            except Exception as csv_error:
                print(f"[ERROR] Failed to save CSV: {csv_error}")
            
            # コンソール出力
            if detections:
                detection_list = []
                for d in detections:
                    pos_info = f"@({d['center_x']:.0f},{d['center_y']:.0f})"
                    detection_list.append(f"{d['class']}({d['confidence']:.2f}){pos_info}")
                detection_str = ', '.join(detection_list)
                print(f"[{observation_count:04d}] LEFT HALF: {len(detections)} detections: {detection_str} | {processing_time:.1f}ms")
            else:
                print(f"[{observation_count:04d}] LEFT HALF: No detections | {processing_time:.1f}ms")
            
            # 終了条件チェック
            elapsed = time.time() - start_time
            if duration > 0 and elapsed >= duration:
                print(f"\nDuration completed ({duration} seconds)")
                break
            
            # 次の観測まで待機
            if running and interval > 0:
                time.sleep(interval)
    
    except Exception as e:
        print(f"\nError during logging: {e}")
        return False
    
    finally:
        # クリーンアップ
        print("\nCleaning up...")
        if picam2:
            picam2.stop()
            picam2.close()
        
        if csv_file:
            csv_file.close()
        
        # 統計表示
        elapsed_time = time.time() - start_time
        print("\n" + "="*50)
        print("Left Half Detection Summary")
        print("="*50)
        print(f"Total observations: {observation_count}")
        print(f"Total detections (left half): {total_detections}")
        print(f"Total time: {elapsed_time:.1f} seconds")
        if observation_count > 0:
            print(f"Average detections per observation: {total_detections/observation_count:.2f}")
        print(f"Log file: {csv_path}")
        print("="*50)
    
    return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Left half detection logging with Picamera2 and YOLOv8"
    )
    
    parser.add_argument('--model', default='../weights/best.pt', help='Model path')
    parser.add_argument('--conf', type=float, default=0.3, help='Confidence threshold')
    parser.add_argument('--width', type=int, default=2304, help='Width (default: 2304)')
    parser.add_argument('--height', type=int, default=1296, help='Height (default: 1296)')
    parser.add_argument('--distance', type=float, default=20.0,
                       help='Focus distance in cm (use 0 for auto focus)')
    parser.add_argument('--auto-focus', action='store_true',
                       help='Enable auto focus mode')
    parser.add_argument('--interval', type=int, default=10,
                       help='Observation interval in seconds')
    parser.add_argument('--duration', type=int, default=60,
                       help='Test duration in seconds (0 for unlimited)')
    parser.add_argument('--save-images', action='store_true',
                       help='Save detection images')
    parser.add_argument('--show-boundary', action='store_true',
                       help='Show boundary line in saved images')
    parser.add_argument('--output-dir', default=None,
                       help='Output directory for logs')
    parser.add_argument('--exposure', type=float, default=-0.5,
                       help='Exposure compensation (-8.0 to 8.0, negative for darker)')
    parser.add_argument('--contrast', type=float, default=2.0,
                       help='Contrast (0.0 to 32.0, default 2.0)')
    parser.add_argument('--brightness', type=float, default=0.0,
                       help='Brightness (-1.0 to 1.0, default 0.0)')
    
    args = parser.parse_args()
    
    print("\nLeft Half Detection Logging Test")
    print("="*50)
    print(f"Model: {args.model}")
    focus_distance = 0 if args.auto_focus else args.distance
    focus_mode = "Auto" if focus_distance == 0 else f"{focus_distance}cm"
    print(f"Focus mode: {focus_mode}")
    print(f"Detection area: LEFT HALF ONLY")
    print(f"Confidence: {args.conf}")
    print(f"Interval: {args.interval}s")
    print(f"Duration: {args.duration}s")
    print()
    
    # テスト実行
    success = test_logging_left_half(
        model_path=args.model,
        confidence=args.conf,
        width=args.width,
        height=args.height,
        focus_distance=focus_distance,
        interval=args.interval,
        duration=args.duration,
        save_images=args.save_images,
        output_dir=args.output_dir,
        show_boundary=args.show_boundary,
        exposure_value=args.exposure,
        contrast=args.contrast,
        brightness=args.brightness
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()