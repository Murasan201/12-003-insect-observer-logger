#!/usr/bin/env python3
"""
ジオプトリー（屈折度）を使った正確なフォーカス制御テスト

LensPosition = 1/距離[m] の公式に基づいて距離を指定
20cm = 5.0 diopters を基準とした昆虫観察用フォーカステスト
"""

import time
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls

def distance_to_diopters(distance_cm):
    """距離（cm）をジオプトリーに変換"""
    return 1.0 / (distance_cm / 100.0)

def diopters_to_distance(diopters):
    """ジオプトリーを距離（cm）に変換"""
    if diopters <= 0:
        return float('inf')
    return 100.0 / diopters

def calculate_sharpness(frame, roi=None):
    """Laplacian分散でシャープネス計算"""
    if roi:
        x, y, w, h = roi
        frame = frame[y:y+h, x:x+w]
    
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return laplacian.var()

def test_diopter_focus():
    """ジオプトリーベースのフォーカステスト"""
    
    print("Diopter-based Focus Test for Insect Observation")
    print("=" * 60)
    
    # Picamera2初期化
    picam2 = Picamera2()
    
    # 軽量設定で高速処理
    config = picam2.create_preview_configuration(
        main={"size": (1536, 864), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    
    # レンズ制御範囲を確認
    lens_controls = picam2.camera_controls.get("LensPosition")
    if lens_controls:
        lp_min, lp_max, lp_default = lens_controls
        print(f"\nLens Position Range:")
        print(f"  Min: {lp_min:.2f} diopters ({diopters_to_distance(lp_min):.1f}cm)")
        print(f"  Max: {lp_max:.2f} diopters ({diopters_to_distance(lp_max):.1f}cm)")  
        print(f"  Default: {lp_default:.2f} diopters ({diopters_to_distance(lp_default):.1f}cm)")
    else:
        print("Warning: LensPosition control not available")
        return False
    
    # 昆虫観察用の距離設定
    test_distances = [
        (5, "Extreme macro - minimum distance"),
        (10, "Super macro - very close"),
        (15, "Ultra macro - close detail"),
        (20, "Macro - standard insect observation"),
        (25, "Close - larger insects"),
        (30, "Medium - flying insects"),
        (50, "Normal - general observation"),
        (100, "Far - landscape insects")
    ]
    
    print(f"\nTesting focus distances:")
    print("-" * 40)
    
    # マニュアルモードに設定
    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
    time.sleep(0.5)
    
    # ウィンドウ作成
    window_name = "Diopter Focus Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    results = []
    
    try:
        for distance_cm, description in test_distances:
            target_diopters = distance_to_diopters(distance_cm)
            
            # レンズ制御範囲内にクランプ
            clamped_diopters = max(lp_min, min(target_diopters, lp_max))
            
            print(f"\nTesting {distance_cm}cm ({description})")
            print(f"  Target diopters: {target_diopters:.2f}")
            print(f"  Clamped diopters: {clamped_diopters:.2f}")
            
            # レンズ位置を設定
            picam2.set_controls({"LensPosition": float(clamped_diopters)})
            
            # レンズ移動を待つ
            time.sleep(1.0)
            
            # 実際の位置を確認
            metadata = picam2.capture_metadata()
            actual_pos = metadata.get("LensPosition", -1)
            actual_distance = diopters_to_distance(actual_pos) if actual_pos > 0 else float('inf')
            
            # フレーム取得とシャープネス計算
            frame = picam2.capture_array()
            
            # 中央部でシャープネス測定
            h, w = frame.shape[:2]
            center_roi = (w//4, h//4, w//2, h//2)
            sharpness = calculate_sharpness(frame, center_roi)
            
            print(f"  Actual position: {actual_pos:.3f} diopters")
            print(f"  Actual distance: {actual_distance:.1f}cm")
            print(f"  Sharpness score: {sharpness:.0f}")
            
            # 結果を記録
            results.append({
                'target_cm': distance_cm,
                'target_diopters': target_diopters,
                'actual_diopters': actual_pos,
                'actual_cm': actual_distance,
                'sharpness': sharpness,
                'description': description
            })
            
            # フレームに情報を描画
            info_lines = [
                f"Distance: {distance_cm}cm target",
                f"Diopters: {clamped_diopters:.2f} -> {actual_pos:.3f}",
                f"Actual: {actual_distance:.1f}cm",
                f"Sharpness: {sharpness:.0f}",
                f"{description}",
                "",
                "Press 'n' for next, 'q' to quit"
            ]
            
            display_frame = frame.copy()
            y_offset = 30
            for i, text in enumerate(info_lines):
                cv2.putText(display_frame, text, (10, y_offset + i * 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # ROI枠を表示
            x, y, w, h = center_roi
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
            cv2.putText(display_frame, "Sharpness ROI", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            cv2.imshow(window_name, display_frame)
            
            # キー待ち
            while True:
                key = cv2.waitKey(100) & 0xFF
                if key == ord('n') or key == 13:  # 'n' or Enter
                    break
                elif key == ord('q') or key == 27:  # 'q' or ESC
                    raise KeyboardInterrupt
                    
        # 結果分析
        print("\n" + "=" * 60)
        print("FOCUS TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # シャープネスでソート
        results.sort(key=lambda x: x['sharpness'], reverse=True)
        
        print(f"{'Rank':<4} {'Distance':<8} {'Diopters':<10} {'Sharpness':<10} {'Description'}")
        print("-" * 60)
        
        for i, result in enumerate(results[:5]):  # トップ5のみ表示
            print(f"{i+1:<4} {result['target_cm']:<8}cm "
                  f"{result['actual_diopters']:<10.3f} {result['sharpness']:<10.0f} "
                  f"{result['description'][:30]}")
        
        # 最適距離の推定
        best_result = results[0]
        print(f"\nRECOMMENDED SETTINGS:")
        print(f"  Best focus distance: {best_result['target_cm']}cm")
        print(f"  Optimal diopter value: {best_result['actual_diopters']:.3f}")
        print(f"  Maximum sharpness: {best_result['sharpness']:.0f}")
        
        # 昆虫観察用の推奨値
        insect_recommendations = []
        for result in results:
            if 15 <= result['target_cm'] <= 30:  # 昆虫観察に適した範囲
                insect_recommendations.append(result)
        
        if insect_recommendations:
            print(f"\nINSECT OBSERVATION RECOMMENDATIONS:")
            insect_recommendations.sort(key=lambda x: x['sharpness'], reverse=True)
            top_insect = insect_recommendations[0]
            print(f"  Recommended distance: {top_insect['target_cm']}cm")
            print(f"  Diopter setting: {top_insect['actual_diopters']:.3f}")
            print(f"  Use: --focus-mode manual --focus-value {top_insect['actual_diopters']:.1f}")
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    
    finally:
        # クリーンアップ
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()
        print("\nTest completed.")

if __name__ == "__main__":
    test_diopter_focus()