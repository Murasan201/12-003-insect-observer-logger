#!/usr/bin/env python3
"""
左半分検出リアルタイム表示スクリプト
Camera Module 3 Wide用の昆虫検出（画面左半分のみ）をリアルタイム表示
"""

import argparse
import sys
import time
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

def signal_handler(sig, frame):
    """Ctrl+Cハンドラ"""
    global running
    print("\nStopping camera test...")
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

def test_camera_left_half(
    model_path: str = '../weights/best.pt',
    confidence: float = 0.3,
    width: int = 2304,
    height: int = 1296,
    show_display: bool = True,
    focus_distance: float = 20.0,
    display_scale: float = 0.5,
    exposure_value: float = -0.5,
    contrast: float = 2.0,
    brightness: float = 0.0
):
    """左半分検出リアルタイム表示"""
    global picam2, running
    
    # モデル読み込み
    print(f"\nLoading model: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"Model loaded successfully. Classes: {model.names}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return False
    
    # Picamera2初期化
    print(f"\nInitializing Picamera2...")
    try:
        picam2 = Picamera2()
        
        # カメラプロパティ取得
        camera_properties = picam2.camera_properties
        print(f"Camera Model: {camera_properties.get('Model', 'Unknown')}")
        
        # LensPosition範囲確認
        lens_controls = picam2.camera_controls.get("LensPosition")
        if lens_controls:
            lp_min, lp_max, lp_default = lens_controls
            print(f"LensPosition range: {lp_min} - {lp_max} (default: {lp_default})")
        else:
            lp_min, lp_max, lp_default = 0.0, 32.0, 1.0
            print("Warning: Using assumed LensPosition range: 0-32")
        
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
        if focus_distance == 0:
            print(f"\nSetting auto focus mode...")
            picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
            print("Auto focus mode enabled")
            time.sleep(2.0)
        else:
            print(f"\nSetting manual focus for {focus_distance}cm distance...")
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
    
    print("\n" + "="*50)
    print("Starting LEFT HALF detection test")
    print(f"Detection area: Left half only (0-{width//2} pixels)")
    print("Press 'q' to quit, 's' to save image")
    print("="*50 + "\n")
    
    # シグナルハンドラ設定
    signal.signal(signal.SIGINT, signal_handler)
    
    # 画像保存ディレクトリ
    script_dir = Path(__file__).parent
    images_dir = script_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    frame_count = 0
    total_detections = 0
    boundary_x = width // 2  # 左半分の境界
    
    try:
        while running:
            # フレーム取得
            frame = picam2.capture_array()
            if frame is None:
                continue
            
            frame_count += 1
            
            # 左半分のみを切り出して検出
            left_half_frame = frame[:, :boundary_x]
            
            # YOLOv8検出（左半分のみ）
            results = model.predict(
                source=left_half_frame,
                device='cpu',
                conf=confidence,
                verbose=False
            )
            
            # 表示用フレーム（全体）
            display_frame = frame.copy()
            
            # 境界線を描画（青い縦線）
            cv2.line(display_frame, (boundary_x, 0), (boundary_x, height), 
                    (255, 0, 0), 2)
            
            # 左半分の枠線（緑）
            cv2.rectangle(display_frame, (0, 0), (boundary_x-1, height-1), 
                         (0, 255, 0), 2)
            
            # "Detection Area" ラベル
            cv2.putText(display_frame, "Detection Area", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_frame, "Ignored Area", (boundary_x + 10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)
            
            # 検出結果処理
            detections = []
            if results[0].boxes is not None:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    cls = int(box.cls)
                    conf = float(box.conf)
                    
                    # 左半分での座標（そのまま使用）
                    cv2.rectangle(display_frame, (int(x1), int(y1)), (int(x2), int(y2)), 
                                (0, 255, 0), 2)
                    
                    # ラベル
                    label = f"{model.names[cls]} {conf:.2f}"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(display_frame, 
                                (int(x1), int(y1) - label_size[1] - 10),
                                (int(x1) + label_size[0], int(y1)),
                                (0, 255, 0), -1)
                    cv2.putText(display_frame, label, (int(x1), int(y1) - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                    
                    detections.append({
                        'class': model.names[cls],
                        'confidence': conf,
                        'bbox': (x1, y1, x2, y2)
                    })
                    total_detections += 1
            
            # ステータス表示
            status_text = f"Frame: {frame_count} | Detections: {len(detections)}"
            cv2.putText(display_frame, status_text, (10, height - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # コンソール出力
            if len(detections) > 0:
                detection_list = [f"{d['class']}({d['confidence']:.2f})" for d in detections]
                print(f"Frame {frame_count}: {len(detections)} detections in LEFT HALF - {', '.join(detection_list)}")
            
            # 表示
            if show_display:
                # BGRに変換
                display_frame_bgr = cv2.cvtColor(display_frame, cv2.COLOR_RGB2BGR)
                
                # ウィンドウサイズ調整（リサイズ）
                if display_scale != 1.0:
                    display_width = int(width * display_scale)
                    display_height = int(height * display_scale)
                    display_frame_resized = cv2.resize(display_frame_bgr, (display_width, display_height))
                    cv2.imshow('Left Half Detection Test', display_frame_resized)
                else:
                    cv2.imshow('Left Half Detection Test', display_frame_bgr)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quit requested")
                    break
                elif key == ord('s'):
                    # 画像保存
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"left_half_test_{timestamp}.jpg"
                    filepath = images_dir / filename
                    cv2.imwrite(str(filepath), display_frame_bgr)
                    print(f"Image saved: {filepath}")
            
            # CPU使用率を抑える
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error during detection: {e}")
        return False
    finally:
        print("\nCleaning up...")
        if show_display:
            cv2.destroyAllWindows()
        if picam2:
            picam2.stop()
            picam2.close()
        
        print(f"\nTest completed")
        print(f"Total frames: {frame_count}")
        print(f"Total detections (left half): {total_detections}")
        if frame_count > 0:
            print(f"Average detections per frame: {total_detections/frame_count:.2f}")
    
    return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Test left half detection with real-time display"
    )
    
    parser.add_argument('--model', default='../weights/best.pt', help='Model path')
    parser.add_argument('--conf', type=float, default=0.3, help='Confidence threshold')
    parser.add_argument('--width', type=int, default=2304, help='Width (default: 2304)')
    parser.add_argument('--height', type=int, default=1296, help='Height (default: 1296)')
    parser.add_argument('--no-display', action='store_true', help='Headless mode')
    parser.add_argument('--distance', type=float, default=20.0, 
                       help='Focus distance in cm (5-100), use 0 for auto focus')
    parser.add_argument('--auto-focus', action='store_true',
                       help='Enable auto focus mode')
    parser.add_argument('--display-scale', type=float, default=0.5,
                       help='Display window scale (0.5 = half size, 1.0 = full size)')
    parser.add_argument('--exposure', type=float, default=-0.5,
                       help='Exposure compensation (-8.0 to 8.0, negative for darker)')
    parser.add_argument('--contrast', type=float, default=2.0,
                       help='Contrast (0.0 to 32.0, default 2.0)')
    parser.add_argument('--brightness', type=float, default=0.0,
                       help='Brightness (-1.0 to 1.0, default 0.0)')
    
    args = parser.parse_args()
    
    print("\nLeft Half Detection Real-time Test")
    print("="*50)
    print(f"Model: {args.model}")
    print(f"Confidence: {args.conf}")
    print(f"Resolution: {args.width}x{args.height}")
    
    focus_distance = 0 if args.auto_focus else args.distance
    focus_mode = "Auto" if focus_distance == 0 else f"{focus_distance}cm"
    print(f"Focus: {focus_mode}")
    print(f"Display: {'No' if args.no_display else 'Yes'}")
    print()
    
    # テスト実行
    success = test_camera_left_half(
        model_path=args.model,
        confidence=args.conf,
        width=args.width,
        height=args.height,
        show_display=not args.no_display,
        focus_distance=focus_distance,
        display_scale=args.display_scale,
        exposure_value=args.exposure,
        contrast=args.contrast,
        brightness=args.brightness
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()