#!/usr/bin/env python3
"""
Picamera2を使用したカメラテスト
Raspberry Pi Camera Module 3専用
"""

import sys

try:
    from picamera2 import Picamera2
    import cv2
    import numpy as np
    print("Picamera2モジュールが見つかりました")
except ImportError:
    print("エラー: Picamera2がインストールされていません")
    print("インストール方法: sudo apt install -y python3-picamera2")
    sys.exit(1)

def test_picamera2():
    """Picamera2でカメラをテスト"""
    
    try:
        # Picamera2インスタンスを作成
        picam2 = Picamera2()
        
        # 利用可能な設定を表示
        print("利用可能なカメラ設定:")
        configs = picam2.sensor_modes
        for i, config in enumerate(configs):
            print(f"  {i}: {config}")
        
        # プレビュー設定を作成
        preview_config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        picam2.configure(preview_config)
        
        print("\nカメラを起動中...")
        picam2.start()
        
        print("フレームを取得中...")
        for i in range(5):
            # フレームを取得
            frame = picam2.capture_array()
            
            if frame is not None:
                print(f"✓ フレーム {i+1} 取得成功: {frame.shape}")
                
                # 最初のフレームを保存
                if i == 0:
                    # BGRに変換してOpenCVで保存
                    bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    cv2.imwrite("picamera2_test.jpg", bgr_frame)
                    print("  picamera2_test.jpg として保存しました")
        
        picam2.stop()
        print("\n成功: Picamera2でカメラが正常に動作しています")
        return True
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

def convert_to_opencv_capture():
    """Picamera2からOpenCVで使用できる形式に変換"""
    print("\nPicamera2 + OpenCV統合テスト...")
    
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
        
        print("OpenCV形式での表示テスト（qキーで終了）")
        
        while True:
            frame = picam2.capture_array()
            
            # RGB to BGR変換
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # OpenCVで表示
            cv2.imshow("Picamera2 + OpenCV", bgr_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        picam2.stop()
        cv2.destroyAllWindows()
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("Picamera2を使用したカメラテスト")
    print("=" * 50)
    
    # 基本テスト
    if test_picamera2():
        print("\n次にOpenCVとの統合をテストしますか？ (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            convert_to_opencv_capture()
    else:
        print("\nPicamera2でのカメラアクセスに失敗しました")
        print("推奨される対処法:")
        print("1. sudo apt update && sudo apt install -y python3-picamera2")
        print("2. カメラケーブルの接続を確認")
        print("3. sudo raspi-config でカメラインターフェースを有効化")

if __name__ == "__main__":
    main()