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
    from libcamera import controls
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

def optimize_focus_sweep(picam2, center_value, sweep_range=0.8, step=0.2):
    """
    フォーカス値周辺を自動スイープして最適値を見つける
    有識者推奨のLaplacian分散を使用したシャープネス最適化
    
    Args:
        picam2: Picamera2インスタンス
        center_value: 中心となるフォーカス値（ジオプトリー）
        sweep_range: スイープ範囲（±値）
        step: スイープのステップサイズ
    
    Returns:
        最適なフォーカス値
    """
    import numpy as np
    
    print(f"  Focus sweep optimization: {center_value-sweep_range:.1f} to {center_value+sweep_range:.1f} diopters")
    
    # レンズ制御範囲を取得
    lens_controls = picam2.camera_controls.get("LensPosition")
    if not lens_controls:
        print("  Warning: LensPosition control not available")
        return center_value
    
    lp_min, lp_max, _ = lens_controls
    
    # テスト値を生成（範囲内にクランプ）
    test_values = np.arange(center_value - sweep_range, center_value + sweep_range + step, step)
    test_values = np.clip(test_values, lp_min, lp_max)
    test_values = np.round(test_values, 2)
    
    best_value = center_value
    best_sharpness = 0
    
    print(f"  Testing {len(test_values)} focus positions...")
    
    for i, test_value in enumerate(test_values):
        # レンズ位置を設定
        picam2.set_controls({"LensPosition": float(test_value)})
        time.sleep(0.3)  # レンズ移動を待つ
        
        # フレーム取得
        frame = picam2.capture_array()
        
        # 中央部ROIでシャープネス計算
        h, w = frame.shape[:2]
        roi_x, roi_y = w//4, h//4
        roi_w, roi_h = w//2, h//2
        roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        
        # Laplacian分散でシャープネス計算
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        if sharpness > best_sharpness:
            best_sharpness = sharpness
            best_value = test_value
        
        print(f"    {i+1}/{len(test_values)}: {test_value:.2f} diopters → sharpness {sharpness:.0f}")
    
    print(f"  Optimal focus: {best_value:.2f} diopters (sharpness: {best_sharpness:.0f})")
    
    return best_value

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
    show_display: bool = True,
    focus_mode: str = 'auto',
    focus_value: float = 5.0,
    auto_sweep: bool = False
):
    """
    Picamera2を使用してCamera Module 3 WideでYOLOv8物体検出をテストします。
    
    Args:
        model_path: YOLOv8モデルファイルのパス
        confidence: 検出の信頼度閾値
        width: カメラ解像度の幅
        height: カメラ解像度の高さ
        show_display: 画面表示するかどうか
        focus_mode: フォーカスモード ('auto', 'manual', 'continuous')
        focus_value: マニュアルフォーカス時のレンズ位置（ジオプトリー）
        auto_sweep: フォーカス値周辺を自動最適化するかどうか
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
        
        # フォーカス設定（改良版）
        print(f"\nSetting focus mode: {focus_mode}")
        try:
            if focus_mode == 'manual':
                # マニュアルモードに設定
                picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
                time.sleep(0.5)  # モード切替を待つ
                # レンズ位置を設定
                picam2.set_controls({"LensPosition": focus_value})
                print(f"Manual focus set to: {focus_value:.1f} (0=infinity, 10=closest)")
                
                # 設定確認のため少し待つ
                time.sleep(1.0)
                metadata = picam2.capture_metadata()
                actual_pos = metadata.get('LensPosition', -1)
                if actual_pos != -1:
                    print(f"Confirmed lens position: {actual_pos:.3f}")
                else:
                    print("Warning: Could not confirm lens position")
                
                # Auto-sweep機能：周辺のフォーカス値を試して最適化
                if auto_sweep:
                    print(f"\nAuto-sweep optimization around {focus_value:.1f} diopters...")
                    best_focus_value = optimize_focus_sweep(picam2, focus_value)
                    if abs(best_focus_value - focus_value) > 0.1:
                        focus_value = best_focus_value
                        picam2.set_controls({"LensPosition": float(focus_value)})
                        print(f"Focus optimized: {focus_value:.2f} diopters")
                        time.sleep(1.0)
                    else:
                        print(f"Focus already optimal: {focus_value:.2f} diopters")
                    
            elif focus_mode == 'continuous':
                # 連続オートフォーカス
                picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
                print("Continuous autofocus enabled - camera will continuously adjust focus")
                time.sleep(2.0)  # 連続AFが動作開始するまで待つ
                
            else:  # auto
                # オートフォーカス（一回のみ）
                picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
                time.sleep(0.5)
                # AFをトリガー
                picam2.set_controls({"AfTrigger": controls.AfTriggerEnum.Start})
                print("Auto focus triggered - waiting for AF to complete...")
                
                # AFが完了するまで待つ
                af_timeout = 5.0  # 5秒でタイムアウト
                start_time = time.time()
                while time.time() - start_time < af_timeout:
                    metadata = picam2.capture_metadata()
                    af_state = metadata.get('AfState', -1)
                    
                    if af_state == controls.AfStateEnum.Focused:
                        lens_pos = metadata.get('LensPosition', -1)
                        print(f"Auto focus completed! Lens position: {lens_pos:.3f}")
                        break
                    elif af_state == controls.AfStateEnum.Failed:
                        print("Auto focus failed - will continue with current position")
                        break
                    
                    time.sleep(0.1)
                else:
                    print("Auto focus timeout - continuing with current position")
                    
        except Exception as e:
            print(f"Warning: Could not set focus mode: {e}")
            print("Camera may not support autofocus or focus control")
            print("Continuing with default settings...")
        
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
    
    parser.add_argument(
        '--focus-mode',
        type=str,
        default='auto',
        choices=['auto', 'manual', 'continuous'],
        help='Focus mode: auto, manual, or continuous (default: auto)'
    )
    
    parser.add_argument(
        '--focus-value',
        type=float,
        default=5.0,
        help='Manual focus value in diopters: 5.0=20cm, 10.0=10cm (default: 5.0)'
    )
    
    parser.add_argument(
        '--focus-distance',
        type=float,
        default=None,
        help='Target focus distance in cm (will be converted to diopters)'
    )
    
    parser.add_argument(
        '--auto-sweep',
        action='store_true',
        help='Auto-sweep focus around target value to find optimal sharpness'
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
    
    # 距離からジオプトリーへの変換
    if args.focus_distance is not None:
        args.focus_value = 1.0 / (args.focus_distance / 100.0)
        print(f"\nConverted {args.focus_distance}cm to {args.focus_value:.2f} diopters")
    
    # フォーカス設定の推奨値を表示
    print("\nFocus settings for insect observation (diopter-based):")
    print("  Ultra close (5cm): --focus-distance 5 (20.0 diopters)")
    print("  Very close (10cm): --focus-distance 10 (10.0 diopters)")
    print("  Close (15cm): --focus-distance 15 (6.7 diopters)")
    print("  Macro (20cm): --focus-distance 20 (5.0 diopters) ← Standard")
    print("  Medium (30cm): --focus-distance 30 (3.3 diopters)")
    print("  Normal (50cm): --focus-distance 50 (2.0 diopters)")
    print("\nExpert-recommended approaches:")
    print("  1. Macro AF → Lock: --focus-mode auto")
    print("  2. Manual distance: --focus-mode manual --focus-distance 20")
    print("  3. Auto-optimize: --focus-mode manual --focus-distance 20 --auto-sweep")
    print()
    
    # テストを実行
    success = test_camera_detection_picamera2(
        model_path=args.model,
        confidence=args.conf,
        width=args.width,
        height=args.height,
        show_display=not args.no_display,
        focus_mode=args.focus_mode,
        focus_value=args.focus_value,
        auto_sweep=args.auto_sweep
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()