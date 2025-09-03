#!/usr/bin/env python3
"""
Camera Module 3 Wide用の修正版YOLOv8物体検出スクリプト
LensPosition範囲が0-32の特殊なカメラに対応
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
    sys.exit(1)

# グローバル変数
picam2 = None
running = True

def signal_handler(sig, frame):
    """Ctrl+Cハンドラ"""
    global running
    print("\nStopping...")
    running = False

def distance_to_lens_position(distance_cm, max_lens=32.0):
    """
    距離(cm)をCamera Module 3 Wide用のレンズ位置に変換
    注: このカメラはLensPosition 0-32の範囲を持つ
    経験的な変換式を使用
    """
    # 32.0が最近接、0.0が無限遠と仮定
    # 5cmで32.0、無限遠で0.0として線形補間
    if distance_cm <= 5:
        return max_lens
    elif distance_cm >= 100:
        return 0.0
    else:
        # 対数スケールで変換（近距離により敏感）
        # 5cm->32, 10cm->20, 20cm->10, 50cm->4, 100cm->0
        import math
        log_distance = math.log10(distance_cm / 5)
        lens_pos = max_lens * (1 - log_distance / math.log10(20))
        return max(0.0, min(max_lens, lens_pos))

def test_camera_detection_fixed(
    model_path: str = 'yolov8n.pt',
    confidence: float = 0.25,
    width: int = 2304,
    height: int = 1296,
    show_display: bool = True,
    focus_distance: float = 20.0
):
    """
    修正版: Camera Module 3 Wideの特殊なLensPosition範囲に対応
    """
    global picam2, running
    
    # モデルを読み込み
    print(f"Loading model: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"Model loaded successfully. Classes: {len(model.names)}")
    except Exception as e:
        print(f"Error: Failed to load model: {e}")
        return False
    
    # Picamera2を初期化
    print(f"\nInitializing Picamera2...")
    try:
        picam2 = Picamera2()
        
        # カメラコントロール範囲を確認
        lens_controls = picam2.camera_controls.get("LensPosition")
        if lens_controls:
            lp_min, lp_max, lp_default = lens_controls
            print(f"LensPosition range: {lp_min}-{lp_max} (default: {lp_default})")
        else:
            lp_min, lp_max, lp_default = 0.0, 32.0, 1.0
            print("Warning: Using assumed LensPosition range: 0-32")
        
        # カメラ設定
        # Camera Module 3 Wide用: 2304x1296の2x2ビニングモードで最大視野角を確保
        sensor_resolution = picam2.sensor_resolution
        print(f"Sensor resolution: {sensor_resolution}")
        print(f"Using binned sensor mode: {width}x{height} for full wide-angle coverage")
        
        # 2x2ビニングモードを使用して最大視野角を確保
        # 2304x1296は2x2ビニング（4608x2592の半分）で最大FOVを維持
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
            # オートフォーカスモードを使用
            picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
            print("Auto focus mode enabled")
            time.sleep(2.0)  # オートフォーカスの安定化待機
            target_lens_pos = None
        else:
            print(f"\nSetting manual focus for {focus_distance}cm distance...")
            
            # 距離をレンズ位置に変換
            target_lens_pos = distance_to_lens_position(focus_distance, lp_max)
            print(f"Target lens position: {target_lens_pos:.1f} (for {focus_distance}cm)")
            
            # マニュアルモードで設定
            picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
            time.sleep(0.5)
            picam2.set_controls({"LensPosition": float(target_lens_pos)})
            time.sleep(1.0)
        
        # 実際の位置を確認
        metadata = picam2.capture_metadata()
        actual_pos = metadata.get('LensPosition', -1)
        if actual_pos != -1:
            print(f"Actual lens position: {actual_pos:.1f}")
        
        # シャープネス最適化（マニュアルフォーカスの場合のみ）
        if focus_distance > 0 and target_lens_pos is not None:
            print("\nOptimizing focus around target position...")
            best_pos = optimize_focus_simple(picam2, target_lens_pos, lp_max)
            if abs(best_pos - target_lens_pos) > 1.0:
                picam2.set_controls({"LensPosition": float(best_pos)})
                print(f"Optimized lens position: {best_pos:.1f}")
                time.sleep(1.0)
        elif focus_distance == 0:
            print("Auto focus mode - skipping manual optimization")
        
    except Exception as e:
        print(f"Error: Failed to initialize camera: {e}")
        return False
    
    # ウィンドウを作成
    if show_display:
        window_name = "YOLO Detection - Fixed"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
    
    print("\nStarting detection. Press Ctrl+C to stop.")
    print("-" * 50)
    
    frame_count = 0
    total_time = 0
    
    # シグナルハンドラを設定
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while running:
            # フレームを取得
            frame = picam2.capture_array()
            if frame is None:
                continue
            
            frame_count += 1
            start_time = time.time()
            
            # YOLOv8で検出
            results = model.predict(
                source=frame,
                device='cpu',
                conf=confidence,
                verbose=False
            )
            
            # 処理時間を計算
            inference_time = (time.time() - start_time) * 1000
            total_time += inference_time
            avg_time = total_time / frame_count
            current_fps = 1000 / inference_time if inference_time > 0 else 0
            
            # 検出結果を描画
            annotated_frame = results[0].plot()
            
            # 定期的にコンソール出力
            if frame_count % 30 == 0:  # 約1秒ごと
                detections = []
                if results[0].boxes is not None:
                    for box in results[0].boxes:
                        cls_id = int(box.cls)
                        conf = float(box.conf)
                        class_name = model.names[cls_id]
                        detections.append(f"{class_name}({conf:.2f})")
                
                if detections:
                    print(f"Frame {frame_count}: {len(detections)} detections - {', '.join(detections[:3])}")
                else:
                    print(f"Frame {frame_count}: No detections | FPS: {current_fps:.1f}")
            
            # 情報をフレームに追加
            info_text = [
                f"Focus: {focus_distance}cm",
                f"Lens: {actual_pos:.1f}" if 'actual_pos' in locals() else "Lens: N/A",
                f"FPS: {current_fps:.1f}",
                f"Inference: {inference_time:.1f}ms"
            ]
            
            y_offset = 30
            for i, text in enumerate(info_text):
                cv2.putText(annotated_frame, text, (10, y_offset + i * 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # フレーム表示
            if show_display:
                cv2.imshow(window_name, annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopped by user")
                    running = False
                    
    except Exception as e:
        print(f"\nError: {e}")
        return False
    finally:
        # クリーンアップ
        print("\nCleaning up...")
        if picam2:
            picam2.stop()
            picam2.close()
        if show_display:
            cv2.destroyAllWindows()
        
        # 統計表示
        print(f"\nTotal frames: {frame_count}")
        if frame_count > 0:
            print(f"Average inference: {avg_time:.1f}ms")
            print(f"Average FPS: {1000/avg_time:.1f}")
    
    return True

def optimize_focus_simple(picam2, center_pos, max_pos, num_steps=5):
    """
    簡単なフォーカス最適化（シャープネスベース）
    """
    # テスト範囲を設定（center_pos ± 20%）
    test_range = max_pos * 0.2
    test_positions = np.linspace(
        max(0, center_pos - test_range),
        min(max_pos, center_pos + test_range),
        num_steps
    )
    
    best_pos = center_pos
    best_sharpness = 0
    
    for pos in test_positions:
        picam2.set_controls({"LensPosition": float(pos)})
        time.sleep(0.3)
        
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        if sharpness > best_sharpness:
            best_sharpness = sharpness
            best_pos = pos
    
    return best_pos

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Fixed YOLOv8 detection for Camera Module 3 Wide (0-32 LensPosition)"
    )
    
    parser.add_argument('--model', default='yolov8n.pt', help='Model path')
    parser.add_argument('--conf', type=float, default=0.25, help='Confidence threshold')
    parser.add_argument('--width', type=int, default=2304, help='Width (default: 2304 for full wide-angle)')
    parser.add_argument('--height', type=int, default=1296, help='Height (default: 1296 for full wide-angle)')
    parser.add_argument('--no-display', action='store_true', help='Headless mode')
    parser.add_argument('--distance', type=float, default=20.0, 
                       help='Focus distance in cm (5-100), use 0 for auto focus')
    parser.add_argument('--auto-focus', action='store_true',
                       help='Enable auto focus mode (overrides --distance)')
    
    args = parser.parse_args()
    
    print("\nCamera Module 3 Wide - Fixed Focus Control")
    print("=" * 50)
    print(f"Focus distance: {args.distance}cm")
    print("\nDistance to LensPosition mapping:")
    print("  5cm  -> 32.0 (maximum close)")
    print("  10cm -> ~20.0")
    print("  20cm -> ~10.0 (recommended for insects)")
    print("  50cm -> ~4.0")
    print("  100cm -> 0.0 (infinity)")
    print()
    
    # オートフォーカスフラグの確認
    focus_distance = 0 if args.auto_focus else args.distance
    
    # テスト実行
    success = test_camera_detection_fixed(
        model_path=args.model,
        confidence=args.conf,
        width=args.width,
        height=args.height,
        show_display=not args.no_display,
        focus_distance=focus_distance
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()