#!/usr/bin/env python3
"""
マクロオートフォーカス→ロック方式のテスト

有識者推奨の手法：
1. AfRange=Macro で近距離優先のAF実行
2. AF成功後、その位置でManualモードにロック
3. ハンチング防止で安定した近距離観察が可能
"""

import time
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls

def wait_for_af_completion(picam2, timeout=10.0):
    """AF完了を待つ"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        metadata = picam2.capture_metadata()
        af_state = metadata.get('AfState', -1)
        
        if af_state == controls.AfStateEnum.Focused:
            return True, "Focused"
        elif af_state == controls.AfStateEnum.Failed:
            return False, "Failed"
        
        time.sleep(0.1)
    
    return False, "Timeout"

def test_macro_af_lock():
    """マクロAF→ロック方式のテスト"""
    
    print("Macro AutoFocus → Lock Test")
    print("=" * 50)
    print("Testing the expert-recommended approach:")
    print("1. Set AfRange=Macro for close-range priority")
    print("2. Execute autofocus cycle")
    print("3. Lock at successful position with Manual mode")
    print()
    
    # Picamera2初期化
    picam2 = Picamera2()
    
    # 設定
    config = picam2.create_preview_configuration(
        main={"size": (1536, 864), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    
    # 利用可能なコントロールを確認
    controls_available = picam2.camera_controls
    print("Available AF controls:")
    af_controls = ['AfMode', 'AfRange', 'AfSpeed', 'LensPosition', 'AfTrigger']
    for control in af_controls:
        if control in controls_available:
            print(f"  ✓ {control}: {controls_available[control]}")
        else:
            print(f"  ✗ {control}: Not available")
    print()
    
    # ウィンドウ作成
    window_name = "Macro AF Lock Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    print("Starting Macro AF sequence...")
    print("-" * 30)
    
    try:
        # ステップ1: マクロ範囲での高速AFに設定
        print("Step 1: Setting up Macro AF parameters...")
        
        af_controls_to_set = {}
        
        # AfRange が利用可能なら Macro に設定
        if 'AfRange' in controls_available:
            af_controls_to_set['AfRange'] = controls.AfRangeEnum.Macro
            print("  AfRange set to Macro (close-range priority)")
        else:
            print("  Warning: AfRange not available")
        
        # AfSpeed が利用可能なら Fast に設定
        if 'AfSpeed' in controls_available:
            af_controls_to_set['AfSpeed'] = controls.AfSpeedEnum.Fast
            print("  AfSpeed set to Fast")
        else:
            print("  Warning: AfSpeed not available")
        
        # Auto AF モードに設定
        af_controls_to_set['AfMode'] = controls.AfModeEnum.Auto
        
        # 設定を適用
        if af_controls_to_set:
            picam2.set_controls(af_controls_to_set)
            time.sleep(0.5)
            print("  AF parameters applied")
        
        # ステップ2: autofocus_cycle() を使用した同期AF実行
        print("\nStep 2: Executing autofocus cycle...")
        
        # autofocus_cycle() が利用可能かチェック
        if hasattr(picam2, 'autofocus_cycle'):
            print("  Using autofocus_cycle() method...")
            af_success = picam2.autofocus_cycle()
            print(f"  AF Result: {'SUCCESS' if af_success else 'FAILED'}")
        else:
            print("  Using manual AF trigger method...")
            # 手動でAFトリガー
            picam2.set_controls({"AfTrigger": controls.AfTriggerEnum.Start})
            af_success, af_result = wait_for_af_completion(picam2, timeout=5.0)
            print(f"  AF Result: {af_result}")
        
        # ステップ3: AF結果の確認とレンズ位置取得
        time.sleep(0.5)
        metadata = picam2.capture_metadata()
        
        lens_position = metadata.get('LensPosition', None)
        af_state = metadata.get('AfState', 'Unknown')
        
        print(f"\nStep 3: AF Results Analysis")
        print(f"  AF State: {af_state}")
        print(f"  Lens Position: {lens_position}")
        
        if lens_position is not None:
            distance_cm = 100.0 / lens_position if lens_position > 0 else float('inf')
            print(f"  Focused Distance: {distance_cm:.1f}cm")
        
        # ステップ4: 成功した場合、Manual モードでロック
        locked_position = None
        if af_success and lens_position is not None:
            print(f"\nStep 4: Locking focus at current position...")
            picam2.set_controls({
                "AfMode": controls.AfModeEnum.Manual,
                "LensPosition": float(lens_position)
            })
            locked_position = lens_position
            print(f"  Focus LOCKED at {lens_position:.3f} diopters ({distance_cm:.1f}cm)")
            print("  Manual mode engaged - no more hunting!")
        else:
            print(f"\nStep 4: AF failed - using default manual focus")
            # フォールバック: 20cm (5.0 diopters) に設定
            picam2.set_controls({
                "AfMode": controls.AfModeEnum.Manual,
                "LensPosition": 5.0
            })
            locked_position = 5.0
            print("  Fallback: Set to 5.0 diopters (20cm)")
        
        time.sleep(1.0)
        
        # ステップ5: ロック状態での動作確認
        print(f"\nStep 5: Testing locked focus stability...")
        
        frame_count = 0
        stable_test_duration = 10  # 10秒間テスト
        start_time = time.time()
        sharpness_history = []
        
        print(f"Testing focus stability for {stable_test_duration} seconds...")
        print("Watch for focus hunting (should be minimal with locked focus)")
        print("Press 'q' to exit early")
        
        while time.time() - start_time < stable_test_duration:
            # フレーム取得
            frame = picam2.capture_array()
            metadata = picam2.capture_metadata()
            frame_count += 1
            
            # 現在のレンズ位置確認
            current_lens = metadata.get('LensPosition', -1)
            current_af_state = metadata.get('AfState', 'Unknown')
            
            # シャープネス計算
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            sharpness_history.append(sharpness)
            
            # レンズ位置の変動チェック
            lens_drift = abs(current_lens - locked_position) if current_lens != -1 and locked_position else 0
            is_stable = lens_drift < 0.05  # 0.05 diopters以下なら安定
            
            # 情報をフレームに描画
            info_lines = [
                f"MACRO AF LOCK TEST",
                f"Locked Position: {locked_position:.3f} diopters",
                f"Current Position: {current_lens:.3f}" if current_lens != -1 else "Current: N/A",
                f"Drift: {lens_drift:.4f} ({'STABLE' if is_stable else 'UNSTABLE'})",
                f"AF State: {current_af_state}",
                f"Sharpness: {sharpness:.0f}",
                f"Time: {time.time() - start_time:.1f}s / {stable_test_duration}s",
                "",
                "Press 'q' to exit"
            ]
            
            y_offset = 30
            for i, text in enumerate(info_lines):
                color = (0, 255, 0) if is_stable else (0, 255, 255)
                cv2.putText(frame, text, (10, y_offset + i * 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # 安定性インジケーター
            status_color = (0, 255, 0) if is_stable else (0, 0, 255)
            cv2.circle(frame, (frame.shape[1] - 50, 50), 20, status_color, -1)
            cv2.putText(frame, "STABLE" if is_stable else "DRIFT", 
                       (frame.shape[1] - 120, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow(window_name, frame)
            
            # 1秒ごとにコンソールに状況報告
            if frame_count % 30 == 0:  # 約1秒ごと（30fps想定）
                elapsed = time.time() - start_time
                avg_sharpness = np.mean(sharpness_history[-30:]) if len(sharpness_history) >= 30 else np.mean(sharpness_history)
                print(f"  {elapsed:.1f}s: Lens={current_lens:.3f}, Drift={lens_drift:.4f}, Sharpness={avg_sharpness:.0f}")
            
            # キー入力チェック
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        # 結果サマリー
        print(f"\n" + "=" * 50)
        print("MACRO AF LOCK TEST RESULTS")
        print("=" * 50)
        
        if sharpness_history:
            avg_sharpness = np.mean(sharpness_history)
            sharpness_std = np.std(sharpness_history)
            print(f"Average Sharpness: {avg_sharpness:.0f}")
            print(f"Sharpness Stability: ±{sharpness_std:.0f}")
            
            # 安定性評価
            if sharpness_std < avg_sharpness * 0.1:
                stability = "EXCELLENT"
            elif sharpness_std < avg_sharpness * 0.2:
                stability = "GOOD"
            else:
                stability = "POOR"
            
            print(f"Focus Stability: {stability}")
        
        if locked_position:
            distance_cm = 100.0 / locked_position if locked_position > 0 else float('inf')
            print(f"\nRECOMMENDED SETTINGS:")
            print(f"  Focus mode: manual")
            print(f"  Focus value: {locked_position:.1f}")
            print(f"  Target distance: {distance_cm:.0f}cm")
            print(f"\nCommand line:")
            print(f"  python test_camera_detection_picamera2.py --focus-mode manual --focus-value {locked_position:.1f}")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # クリーンアップ
        print("\nCleaning up...")
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()
        print("Test completed.")

if __name__ == "__main__":
    test_macro_af_lock()