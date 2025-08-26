#!/usr/bin/env python3
"""
Camera Module 3 Wide用のYOLOv8物体検出テストスクリプト（Picamera2版）

Picamera2を使用してRaspberry Pi Camera Module 3 Wideから映像を取得し、
YOLOv8モデルで物体検出を実行します。

使用方法:
    python test_camera_detection_picamera2.py
    python test_camera_detection_picamera2.py --model weights/best.pt
    python test_camera_detection_picamera2.py --width 1536 --height 864
"""

import argparse
import sys
import time
from pathlib import Path
import signal

try:
    from picamera2 import Picamera2
    import cv2
    import numpy as np
    from ultralytics import YOLO
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Please install: sudo apt install python3-picamera2")
    print("And: pip install ultralytics opencv-python")
    sys.exit(1)

# グローバル変数（シグナルハンドラ用）
picam2 = None
running = True

def signal_handler(sig, frame):
    """Ctrl+Cハンドラ"""
    global running
    print("\nStopping...")
    running = False

def test_camera_detection_picamera2(
    model_path: str = 'yolov8n.pt',
    confidence: float = 0.25,
    width: int = 1536,
    height: int = 864,
    show_display: bool = True
):
    """
    Picamera2を使用してCamera Module 3 WideでYOLOv8物体検出をテストします。
    
    Args:
        model_path: YOLOv8モデルファイルのパス
        confidence: 検出の信頼度閾値
        width: カメラ解像度の幅
        height: カメラ解像度の高さ
        show_display: 画面表示するかどうか
    """
    global picam2, running
    
    # モデルを読み込み
    print(f"Loading model: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"Model loaded successfully. Classes: {len(model.names)}")
        print(f"Detectable classes: {list(model.names.values())[:10]}...")
    except Exception as e:
        print(f"Error: Failed to load model: {e}")
        return False
    
    # Picamera2を初期化
    print(f"\nInitializing Picamera2 with {width}x{height} resolution...")
    try:
        picam2 = Picamera2()
        
        # 利用可能な解像度を表示
        camera_config = picam2.create_preview_configuration()
        sensor_modes = picam2.sensor_modes
        print(f"Available sensor modes: {len(sensor_modes)}")
        for i, mode in enumerate(sensor_modes[:3]):  # 最初の3つを表示
            print(f"  Mode {i}: {mode.get('size', 'N/A')} @ {mode.get('fps', 'N/A')}fps")
        
        # カメラ設定
        config = picam2.create_preview_configuration(
            main={"size": (width, height), "format": "RGB888"},
            buffer_count=4
        )
        
        try:
            picam2.configure(config)
            print(f"Camera configured: {width}x{height}")
        except Exception as e:
            print(f"Warning: Could not configure {width}x{height}, trying default...")
            # デフォルト設定を試す
            config = picam2.create_preview_configuration()
            picam2.configure(config)
            actual_size = config['main']['size']
            width, height = actual_size
            print(f"Using default resolution: {width}x{height}")
        
        # カメラを開始
        print("Starting camera...")
        picam2.start()
        time.sleep(2)  # カメラの安定化を待つ
        
    except Exception as e:
        print(f"Error: Failed to initialize camera: {e}")
        return False
    
    # ウィンドウを作成（表示する場合）
    if show_display:
        window_name = "YOLO Detection - Picamera2"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
    
    print("\nStarting detection. Press Ctrl+C to stop.")
    print("-" * 50)
    
    frame_count = 0
    total_time = 0
    last_print_time = time.time()
    
    # シグナルハンドラを設定
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while running:
            # フレームを取得
            try:
                frame = picam2.capture_array()
                
                if frame is None:
                    print("Warning: Received null frame")
                    continue
                    
            except Exception as e:
                print(f"Warning: Failed to capture frame: {e}")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            start_time = time.time()
            
            # YOLOv8で検出を実行
            results = model.predict(
                source=frame,
                device='cpu',
                conf=confidence,
                verbose=False
            )
            
            # 処理時間を計算
            inference_time = (time.time() - start_time) * 1000  # ミリ秒
            total_time += inference_time
            avg_time = total_time / frame_count if frame_count > 0 else 0
            current_fps = 1000 / inference_time if inference_time > 0 else 0
            
            # 検出結果を描画
            annotated_frame = results[0].plot()
            
            # 1秒ごとにコンソールに状態を表示
            current_time = time.time()
            if current_time - last_print_time >= 1.0:
                if results[0].boxes is not None and len(results[0].boxes) > 0:
                    detections = []
                    for box in results[0].boxes:
                        cls_id = int(box.cls)
                        conf = float(box.conf)
                        class_name = model.names[cls_id]
                        detections.append(f"{class_name}({conf:.2f})")
                    
                    print(f"Frame {frame_count}: Detected {len(detections)} objects - {', '.join(detections[:5])} | "
                          f"Inference: {inference_time:.1f}ms | FPS: {current_fps:.1f}")
                else:
                    print(f"Frame {frame_count}: No detections | "
                          f"Inference: {inference_time:.1f}ms | FPS: {current_fps:.1f}")
                
                last_print_time = current_time
            
            # 情報をフレームに追加
            info_text = [
                f"Frame: {frame_count}",
                f"Inference: {inference_time:.1f}ms",
                f"Avg: {avg_time:.1f}ms",
                f"FPS: {current_fps:.1f}",
                f"Resolution: {width}x{height}"
            ]
            
            y_offset = 30
            for i, text in enumerate(info_text):
                cv2.putText(annotated_frame, text, (10, y_offset + i * 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # フレームを表示
            if show_display:
                cv2.imshow(window_name, annotated_frame)
                
                # 'q'キーで終了
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopped by user")
                    running = False
                    
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # リソースを解放
        print("\nCleaning up...")
        if picam2:
            try:
                picam2.stop()
                picam2.close()
            except:
                pass
        
        if show_display:
            cv2.destroyAllWindows()
        
        # 統計情報を表示
        print("\n" + "=" * 50)
        print("Test Results Summary")
        print("=" * 50)
        print(f"Total frames: {frame_count}")
        if frame_count > 0:
            print(f"Average inference time: {avg_time:.1f}ms")
            print(f"Average FPS: {1000/avg_time:.1f}")
        print("=" * 50)
    
    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="YOLOv8 object detection test with Picamera2 (Camera Module 3 Wide)"
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8n.pt',
        help='YOLOv8 model file path (default: yolov8n.pt)'
    )
    
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='Detection confidence threshold (default: 0.25)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=1536,
        help='Camera resolution width (default: 1536 for Wide)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=864,
        help='Camera resolution height (default: 864 for Wide)'
    )
    
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Run without display window (for SSH/headless mode)'
    )
    
    args = parser.parse_args()
    
    # Camera Module 3 Wide推奨解像度を表示
    print("\nCamera Module 3 Wide recommended resolutions:")
    print("  1536x864  (High FPS, default)")
    print("  2304x1296 (Medium resolution)")
    print("  4608x2592 (Maximum resolution, low FPS)")
    print()
    
    # モデルファイルの存在確認
    if not Path(args.model).exists() and not args.model.endswith('.pt'):
        print(f"Warning: Model file '{args.model}' not found.")
        print("Ultralytics will try to download it automatically.")
    
    # テストを実行
    success = test_camera_detection_picamera2(
        model_path=args.model,
        confidence=args.conf,
        width=args.width,
        height=args.height,
        show_display=not args.no_display
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()