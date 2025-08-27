#!/usr/bin/env python3
"""
Camera Module 3のフォーカス調整テストスクリプト

Picamera2を使用してフォーカスモードと値を調整します。
キーボードでインタラクティブにフォーカスを調整可能です。

使用方法:
    python test_camera_focus.py
    
キー操作:
    q/w: フォーカス値を減少/増加（マニュアルモード時）
    a: オートフォーカスモード切り替え
    m: マニュアルフォーカスモード切り替え
    c: 連続オートフォーカス（CAF）モード切り替え
    s: 現在の設定を保存
    ESC/Ctrl+C: 終了
"""

import sys
import time
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls

def test_focus():
    """フォーカステストメイン関数"""
    print("Camera Focus Test - Camera Module 3")
    print("=" * 50)
    
    # Picamera2初期化
    picam2 = Picamera2()
    
    # カメラ設定
    config = picam2.create_preview_configuration(
        main={"size": (1536, 864), "format": "RGB888"}
    )
    picam2.configure(config)
    
    # カメラコントロールの取得
    camera_controls = picam2.camera_controls
    
    # フォーカス関連のコントロールを確認
    print("\nAvailable focus controls:")
    focus_controls = {}
    
    if 'AfMode' in camera_controls:
        print(f"  AfMode: {camera_controls['AfMode']}")
        focus_controls['AfMode'] = camera_controls['AfMode']
    
    if 'LensPosition' in camera_controls:
        print(f"  LensPosition: {camera_controls['LensPosition']}")
        focus_controls['LensPosition'] = camera_controls['LensPosition']
    
    if 'AfRange' in camera_controls:
        print(f"  AfRange: {camera_controls['AfRange']}")
        focus_controls['AfRange'] = camera_controls['AfRange']
        
    if 'AfSpeed' in camera_controls:
        print(f"  AfSpeed: {camera_controls['AfSpeed']}")
        focus_controls['AfSpeed'] = camera_controls['AfSpeed']
    
    if not focus_controls:
        print("  No focus controls found. Camera may not support autofocus.")
        print("  Note: Camera Module 3 Wide NoIR should support autofocus.")
    
    # カメラ開始
    picam2.start()
    time.sleep(2)  # カメラ安定化待ち
    
    # デフォルト設定
    current_focus_mode = "auto"
    manual_focus_value = 5.0  # デフォルトのレンズ位置（0.0=無限遠、10.0=最近接）
    focus_step = 0.5  # フォーカス調整のステップ
    
    print("\nControls:")
    print("  q/w: Decrease/Increase focus value (manual mode)")
    print("  1-9: Set focus to preset distances")
    print("  a: Auto focus mode")
    print("  m: Manual focus mode")
    print("  c: Continuous AF mode")
    print("  t: Trigger autofocus")
    print("  r: Reset to default")
    print("  ESC: Exit")
    print("\nFocus distance presets:")
    print("  1: Infinity (landscape)")
    print("  2: 10m (far)")
    print("  3: 2m (medium)")
    print("  4: 1m (near)")
    print("  5: 50cm (close)")
    print("  6: 30cm (macro)")
    print("  7: 20cm (super macro)")
    print("  8: 15cm (ultra macro)")
    print("  9: 10cm (extreme macro)")
    print("-" * 50)
    
    # ウィンドウ作成
    window_name = "Camera Focus Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    # フォーカス距離とレンズ位置のマッピング（概算値）
    focus_presets = {
        ord('1'): (0.0, "Infinity"),
        ord('2'): (0.1, "10m"),
        ord('3'): (0.5, "2m"),
        ord('4'): (1.0, "1m"),
        ord('5'): (2.0, "50cm"),
        ord('6'): (3.3, "30cm"),
        ord('7'): (5.0, "20cm"),
        ord('8'): (6.7, "15cm"),
        ord('9'): (10.0, "10cm"),
    }
    
    try:
        while True:
            # フレーム取得
            frame = picam2.capture_array()
            
            # 情報オーバーレイ
            info_text = [
                f"Mode: {current_focus_mode.upper()}",
                f"Manual Value: {manual_focus_value:.1f}",
                "Press 'a' for AUTO, 'm' for MANUAL",
                "Press '1-9' for distance presets",
                "Press 'q/w' to adjust (manual mode)",
            ]
            
            # メタデータから実際のフォーカス情報を取得（可能な場合）
            try:
                metadata = picam2.capture_metadata()
                if 'LensPosition' in metadata:
                    actual_lens = metadata['LensPosition']
                    info_text.append(f"Actual Lens Position: {actual_lens:.2f}")
                if 'AfState' in metadata:
                    af_state = metadata['AfState']
                    info_text.append(f"AF State: {af_state}")
            except:
                pass
            
            # テキスト描画
            y_offset = 30
            for i, text in enumerate(info_text):
                cv2.putText(frame, text, (10, y_offset + i * 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # エッジ検出でフォーカス評価（シャープネス）
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            
            # シャープネス表示
            cv2.putText(frame, f"Sharpness: {sharpness:.0f}", (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # シャープネスバー表示
            bar_width = int(min(sharpness / 50, frame.shape[1] - 20))
            cv2.rectangle(frame, (10, frame.shape[0] - 50), 
                         (10 + bar_width, frame.shape[0] - 40),
                         (0, 255, 0) if sharpness > 1000 else (255, 255, 0), -1)
            
            # フレーム表示
            cv2.imshow(window_name, frame)
            
            # キー入力処理
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27 or key == ord('q'):  # ESC or q to quit
                break
            
            elif key == ord('w'):  # Increase focus (closer)
                if current_focus_mode == "manual":
                    manual_focus_value = min(10.0, manual_focus_value + focus_step)
                    try:
                        picam2.set_controls({"AfMode": controls.AfModeEnum.Manual,
                                           "LensPosition": manual_focus_value})
                        print(f"Manual focus set to: {manual_focus_value:.1f}")
                    except Exception as e:
                        print(f"Error setting focus: {e}")
            
            elif key == ord('q'):  # Decrease focus (farther)
                if current_focus_mode == "manual":
                    manual_focus_value = max(0.0, manual_focus_value - focus_step)
                    try:
                        picam2.set_controls({"AfMode": controls.AfModeEnum.Manual,
                                           "LensPosition": manual_focus_value})
                        print(f"Manual focus set to: {manual_focus_value:.1f}")
                    except Exception as e:
                        print(f"Error setting focus: {e}")
            
            elif key == ord('a'):  # Auto focus mode
                current_focus_mode = "auto"
                try:
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
                    print("Switched to AUTO focus mode")
                except Exception as e:
                    print(f"Error setting auto focus: {e}")
            
            elif key == ord('m'):  # Manual focus mode
                current_focus_mode = "manual"
                try:
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual,
                                       "LensPosition": manual_focus_value})
                    print(f"Switched to MANUAL focus mode (value: {manual_focus_value:.1f})")
                except Exception as e:
                    print(f"Error setting manual focus: {e}")
            
            elif key == ord('c'):  # Continuous AF mode
                current_focus_mode = "continuous"
                try:
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
                    print("Switched to CONTINUOUS AF mode")
                except Exception as e:
                    print(f"Error setting continuous AF: {e}")
            
            elif key == ord('t'):  # Trigger autofocus
                try:
                    picam2.set_controls({"AfTrigger": controls.AfTriggerEnum.Start})
                    print("Autofocus triggered")
                except Exception as e:
                    print(f"Error triggering AF: {e}")
            
            elif key == ord('r'):  # Reset to default
                manual_focus_value = 5.0
                current_focus_mode = "auto"
                try:
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
                    print("Reset to default settings")
                except Exception as e:
                    print(f"Error resetting: {e}")
            
            elif key in focus_presets:  # Number key for preset
                preset_value, preset_name = focus_presets[key]
                manual_focus_value = preset_value
                current_focus_mode = "manual"
                try:
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual,
                                       "LensPosition": manual_focus_value})
                    print(f"Focus preset: {preset_name} (lens position: {manual_focus_value:.1f})")
                except Exception as e:
                    print(f"Error setting preset: {e}")
                    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # クリーンアップ
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()
        print("\nCamera closed")

if __name__ == "__main__":
    test_focus()