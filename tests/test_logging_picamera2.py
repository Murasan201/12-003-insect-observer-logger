#!/usr/bin/env python3
"""
Picamera2対応ロギングテストスクリプト
Camera Module 3 Wide用の昆虫検出とログ記録機能をテスト
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
    """ログファイルの設定"""
    global csv_writer, csv_file
    
    # ディレクトリ作成
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # CSVファイル作成
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = output_dir / f"insect_detection_log_{timestamp}.csv"
    
    csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    
    # ヘッダー書き込み
    headers = [
        'timestamp',
        'observation_number',
        'detection_count',
        'has_detection',
        'class_names',
        'confidence_values',
        'bbox_coordinates',
        'center_x',
        'center_y',
        'bbox_width',
        'bbox_height',
        'area',
        'processing_time_ms',
        'image_saved',
        'image_filename'
    ]
    csv_writer.writerow(headers)
    csv_file.flush()
    
    print(f"CSV log file created: {csv_path}")
    
    # JSONメタデータファイル作成
    metadata_path = output_dir / f"metadata_{timestamp}.json"
    metadata = {
        'start_time': datetime.now().isoformat(),
        'camera_module': 'Camera Module 3 Wide NoIR',
        'focus_distance_cm': None,  # 後で設定
        'model_path': None,  # 後で設定
        'confidence_threshold': None,  # 後で設定
        'resolution': None,  # 後で設定
        'csv_file': csv_path.name
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return csv_path, metadata_path

def save_detection_to_csv(observation_num, detections, processing_time, image_saved=False, image_filename=None):
    """検出結果をCSVに保存"""
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
        
        # 中心座標、幅、高さ、面積を計算
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
        f"{processing_time:.1f}",
        image_saved,
        image_filename or ''
    ]
    
    csv_writer.writerow(row)
    csv_file.flush()

def test_logging_with_detection(
    model_path: str = 'weights/best.pt',
    confidence: float = 0.25,
    width: int = 1536,
    height: int = 864,
    focus_distance: float = 20.0,
    interval: int = 10,
    duration: int = 60,
    save_images: bool = False,
    output_dir: str = None
):
    """ロギング機能テスト"""
    global picam2, running
    
    # デフォルトの出力ディレクトリをtests/insect_detection_logs/に設定
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
            # オートフォーカスモードを使用
            picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
            print("Auto focus mode enabled")
            time.sleep(2.0)  # オートフォーカスの安定化待機
        else:
            print(f"Setting manual focus for {focus_distance}cm...")
            
            # 距離をレンズ位置に変換
            target_lens_pos = distance_to_lens_position(focus_distance, lp_max)
            print(f"Target lens position: {target_lens_pos:.1f} (for {focus_distance}cm)")
            
            # マニュアルモードで設定
            picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
            time.sleep(0.5)
            picam2.set_controls({"LensPosition": float(target_lens_pos)})
            time.sleep(1.0)
        
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
        'interval_seconds': interval,
        'duration_seconds': duration,
        'save_images': save_images
    })
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*50)
    print("Starting logging test")
    print(f"Interval: {interval} seconds")
    print(f"Duration: {duration} seconds")
    print(f"Save images: {save_images}")
    print("="*50 + "\n")
    
    # シグナルハンドラ設定
    signal.signal(signal.SIGINT, signal_handler)
    
    # 画像保存ディレクトリ（tests/images を使用）
    if save_images:
        # スクリプトの位置からの相対パスで tests/images を指定
        script_dir = Path(__file__).parent
        images_dir = script_dir / "images"
        images_dir.mkdir(exist_ok=True)
        print(f"Images will be saved to: {images_dir}")
    
    observation_count = 0
    start_time = time.time()
    total_detections = 0
    
    try:
        while running:
            obs_start = time.time()
            
            # フレーム取得
            frame = picam2.capture_array()
            if frame is None:
                print(f"[WARNING] Frame capture failed, skipping this cycle...")
                # 短時間待機してリトライ
                time.sleep(1)
                continue
            
            # 成功した場合のみ観測番号を増加
            observation_count += 1
            
            # YOLOv8検出
            results = model.predict(
                source=frame,
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
                    
                    # 追加の位置情報を計算
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
                image_filename = f"detection_{timestamp}.jpg"
                image_path = images_dir / image_filename
                
                # 検出結果を描画
                annotated_frame = results[0].plot()
                # BGRに変換してOpenCVで保存
                annotated_frame_bgr = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(image_path), annotated_frame_bgr)
                image_saved = True
            
            # CSVに保存（検出の有無に関わらず必ず実行）
            try:
                save_detection_to_csv(
                    observation_count,
                    detections,
                    processing_time,
                    image_saved,
                    image_filename
                )
            except Exception as csv_error:
                print(f"[ERROR] Failed to save CSV for observation #{observation_count}: {csv_error}")
            
            # コンソール出力
            if detections:
                detection_list = []
                for d in detections:
                    # 簡易位置情報を追加（中心座標とサイズ）
                    pos_info = f"@({d['center_x']:.0f},{d['center_y']:.0f})[{d['width']:.0f}x{d['height']:.0f}]"
                    detection_list.append(f"{d['class']}({d['confidence']:.2f}){pos_info}")
                detection_str = ', '.join(detection_list)
                print(f"[{observation_count:04d}] {len(detections)} detections: {detection_str} | {processing_time:.1f}ms")
            else:
                print(f"[{observation_count:04d}] No detections | {processing_time:.1f}ms")
            
            # 終了条件チェック
            elapsed = time.time() - start_time
            if duration > 0 and elapsed >= duration:
                print(f"\nDuration completed ({duration} seconds)")
                break
            
            # 次の観測まで待機
            if running and interval > 0:
                print(f"[INFO] Waiting {interval} seconds for next observation...")
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
        print("Logging Test Summary")
        print("="*50)
        print(f"Total observations: {observation_count}")
        print(f"Total detections: {total_detections}")
        print(f"Total time: {elapsed_time:.1f} seconds")
        if observation_count > 0:
            print(f"Average detections per observation: {total_detections/observation_count:.2f}")
            print(f"Average time per observation: {elapsed_time/observation_count:.2f} seconds")
        print(f"Log file: {csv_path}")
        print("="*50)
    
    return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Test logging functionality with Picamera2 and YOLOv8"
    )
    
    parser.add_argument('--model', default='weights/best.pt', help='Model path')
    parser.add_argument('--conf', type=float, default=0.25, help='Confidence threshold')
    parser.add_argument('--width', type=int, default=1536, help='Width')
    parser.add_argument('--height', type=int, default=864, help='Height')
    parser.add_argument('--distance', type=float, default=20.0,
                       help='Focus distance in cm (use 0 for auto focus)')
    parser.add_argument('--auto-focus', action='store_true',
                       help='Enable auto focus mode (overrides --distance)')
    parser.add_argument('--interval', type=int, default=10,
                       help='Observation interval in seconds')
    parser.add_argument('--duration', type=int, default=60,
                       help='Test duration in seconds (0 for unlimited)')
    parser.add_argument('--save-images', action='store_true',
                       help='Save detection images')
    parser.add_argument('--output-dir', default=None,
                       help='Output directory for logs (default: tests/insect_detection_logs/)')
    
    args = parser.parse_args()
    
    print("\nInsect Detection Logging Test")
    print("="*50)
    print(f"Model: {args.model}")
    # オートフォーカスフラグの確認
    focus_distance = 0 if args.auto_focus else args.distance
    focus_mode = "Auto" if focus_distance == 0 else f"{focus_distance}cm"
    
    print(f"Focus mode: {focus_mode}")
    print(f"Interval: {args.interval}s")
    print(f"Duration: {args.duration}s")
    output_display = args.output_dir if args.output_dir else "tests/insect_detection_logs/"
    print(f"Output: {output_display}")
    print()
    
    # テスト実行
    success = test_logging_with_detection(
        model_path=args.model,
        confidence=args.conf,
        width=args.width,
        height=args.height,
        focus_distance=focus_distance,
        interval=args.interval,
        duration=args.duration,
        save_images=args.save_images,
        output_dir=args.output_dir
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()