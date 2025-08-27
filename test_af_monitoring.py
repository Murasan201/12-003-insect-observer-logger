#!/usr/bin/env python3
"""
オートフォーカスの動作をモニタリングするスクリプト
連続的にAF状態とレンズ位置を監視します
"""

import time
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls

def monitor_autofocus():
    """オートフォーカスをモニタリング"""
    
    print("Autofocus Monitoring Test")
    print("=" * 50)
    print("Testing different AF modes to find what works...")
    print()
    
    # Picamera2初期化
    picam2 = Picamera2()
    
    # カメラ設定
    config = picam2.create_preview_configuration(
        main={"size": (1536, 864), "format": "RGB888"},
        buffer_count=4
    )
    picam2.configure(config)
    
    # カメラ起動
    picam2.start()
    print("Camera started. Waiting for stabilization...")
    time.sleep(2)
    
    # ウィンドウ作成
    window_name = "AF Monitor"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    print("\nPress keys to test different modes:")
    print("  'c' - Continuous AF (CAF)")
    print("  'a' - Auto AF with trigger")
    print("  'm' - Manual mode with different positions")
    print("  't' - Trigger AF (in current mode)")
    print("  'r' - Reset to default")
    print("  'q' - Quit")
    print("-" * 50)
    
    current_mode = "none"
    frame_count = 0
    last_lens_position = None
    af_state_history = []
    
    # 初期状態を取得
    try:
        metadata = picam2.capture_metadata()
        print(f"\nInitial metadata:")
        if 'AfMode' in metadata:
            print(f"  AfMode: {metadata['AfMode']}")
        if 'AfState' in metadata:
            print(f"  AfState: {metadata['AfState']}")
        if 'LensPosition' in metadata:
            print(f"  LensPosition: {metadata['LensPosition']}")
    except:
        pass
    
    print("\nStarting monitoring...")
    print("-" * 50)
    
    try:
        while True:
            # フレームとメタデータを取得
            frame = picam2.capture_array()
            metadata = picam2.capture_metadata()
            frame_count += 1
            
            # AF関連のメタデータを抽出
            af_mode = metadata.get('AfMode', 'Unknown')
            af_state = metadata.get('AfState', 'Unknown')
            lens_pos = metadata.get('LensPosition', -1)
            af_pause_state = metadata.get('AfPauseState', 'Unknown')
            
            # レンズ位置の変化を検出
            lens_changed = False
            if last_lens_position is not None and lens_pos != -1:
                if abs(lens_pos - last_lens_position) > 0.01:
                    lens_changed = True
                    print(f"\n[Frame {frame_count}] Lens moved: {last_lens_position:.3f} -> {lens_pos:.3f}")
            last_lens_position = lens_pos if lens_pos != -1 else last_lens_position
            
            # AF状態の変化を追跡
            if len(af_state_history) == 0 or af_state != af_state_history[-1]:
                af_state_history.append(af_state)
                if len(af_state_history) > 1:
                    print(f"[Frame {frame_count}] AF State changed: {af_state_history[-2]} -> {af_state}")
            
            # シャープネス計算（フォーカス評価）
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            
            # 情報をフレームに描画
            info_lines = [
                f"Mode: {current_mode.upper()}",
                f"AF Mode: {af_mode}",
                f"AF State: {af_state}",
                f"Lens Position: {lens_pos:.3f}" if lens_pos != -1 else "Lens Position: N/A",
                f"Sharpness: {sharpness:.0f}",
                f"Frame: {frame_count}"
            ]
            
            if lens_changed:
                info_lines.append(">>> LENS MOVING <<<")
            
            y_offset = 30
            for i, text in enumerate(info_lines):
                color = (0, 255, 0) if not lens_changed else (0, 255, 255)
                cv2.putText(frame, text, (10, y_offset + i * 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # シャープネスバー
            bar_width = int(min(sharpness / 50, frame.shape[1] - 20))
            bar_color = (0, 255, 0) if sharpness > 1500 else (255, 255, 0) if sharpness > 500 else (255, 0, 0)
            cv2.rectangle(frame, (10, frame.shape[0] - 50), 
                         (10 + bar_width, frame.shape[0] - 40), bar_color, -1)
            
            # フレーム表示
            cv2.imshow(window_name, frame)
            
            # キー入力処理
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
                
            elif key == ord('c'):  # Continuous AF
                current_mode = "continuous"
                print(f"\n[Frame {frame_count}] Setting CONTINUOUS AF mode...")
                try:
                    # 連続AFモードを設定
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
                    print("  -> Continuous AF enabled")
                except Exception as e:
                    print(f"  -> Error: {e}")
                    
            elif key == ord('a'):  # Auto AF with trigger
                current_mode = "auto"
                print(f"\n[Frame {frame_count}] Setting AUTO AF mode...")
                try:
                    # オートAFモードに設定
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
                    time.sleep(0.1)
                    # AFをトリガー
                    picam2.set_controls({"AfTrigger": controls.AfTriggerEnum.Start})
                    print("  -> Auto AF set and triggered")
                except Exception as e:
                    print(f"  -> Error: {e}")
                    
            elif key == ord('m'):  # Manual positions test
                current_mode = "manual_test"
                print(f"\n[Frame {frame_count}] Testing MANUAL positions...")
                positions = [0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0]
                try:
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
                    for pos in positions:
                        print(f"  Setting lens to {pos}...")
                        picam2.set_controls({"LensPosition": pos})
                        time.sleep(0.5)
                        # 現在の位置を確認
                        meta = picam2.capture_metadata()
                        actual = meta.get('LensPosition', -1)
                        print(f"    -> Actual position: {actual}")
                except Exception as e:
                    print(f"  -> Error: {e}")
                    
            elif key == ord('t'):  # Trigger AF
                print(f"\n[Frame {frame_count}] Triggering AF...")
                try:
                    picam2.set_controls({"AfTrigger": controls.AfTriggerEnum.Start})
                    print("  -> AF triggered")
                except Exception as e:
                    print(f"  -> Error: {e}")
                    
            elif key == ord('r'):  # Reset
                current_mode = "reset"
                print(f"\n[Frame {frame_count}] Resetting to default...")
                try:
                    # デフォルト設定に戻す
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
                    print("  -> Reset to Auto mode")
                except Exception as e:
                    print(f"  -> Error: {e}")
            
            # 定期的な状態レポート（100フレームごと）
            if frame_count % 100 == 0:
                print(f"\n[Status at frame {frame_count}]")
                print(f"  Current mode: {current_mode}")
                print(f"  Lens position: {lens_pos:.3f}" if lens_pos != -1 else "  Lens position: N/A")
                print(f"  AF State: {af_state}")
                print(f"  Sharpness: {sharpness:.0f}")
                
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # クリーンアップ
        print("\nCleaning up...")
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()
        
        # サマリー表示
        print("\n" + "=" * 50)
        print("Summary:")
        print(f"  Total frames: {frame_count}")
        print(f"  AF states observed: {list(set(af_state_history))}")
        print("=" * 50)

if __name__ == "__main__":
    monitor_autofocus()