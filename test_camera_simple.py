#!/usr/bin/env python3
"""
シンプルなカメラテストスクリプト
OpenCVのみを使用してカメラが動作するか確認します
"""

import cv2
import sys

def test_camera():
    """カメラの基本動作をテスト"""
    print("シンプルなカメラテストを開始...")
    
    # 複数の方法でカメラを開く
    methods = [
        (0, "デフォルト (index 0)"),
        (0, "V4L2バックエンド", cv2.CAP_V4L2),
        ("/dev/video0", "デバイスパス直接指定"),
    ]
    
    for method in methods:
        if len(method) == 2:
            cam_id, desc = method
            print(f"\n試行中: {desc}")
            cap = cv2.VideoCapture(cam_id)
        else:
            cam_id, desc, backend = method
            print(f"\n試行中: {desc}")
            cap = cv2.VideoCapture(cam_id, backend)
        
        if cap.isOpened():
            print("✓ カメラを開けました！")
            
            # 1フレーム取得を試みる
            ret, frame = cap.read()
            if ret:
                print(f"✓ フレーム取得成功: {frame.shape}")
                print(f"  解像度: {frame.shape[1]}x{frame.shape[0]}")
                
                # フレームを保存
                cv2.imwrite("test_frame.jpg", frame)
                print("✓ test_frame.jpg として保存しました")
            else:
                print("✗ フレーム取得失敗")
            
            cap.release()
            return True
        else:
            print("✗ カメラを開けませんでした")
    
    return False

if __name__ == "__main__":
    print("OpenCV version:", cv2.__version__)
    
    if test_camera():
        print("\n成功: カメラは正常に動作しています")
        sys.exit(0)
    else:
        print("\nエラー: カメラにアクセスできません")
        print("\n確認事項:")
        print("1. カメラが正しく接続されているか")
        print("2. raspi-configでカメラが有効になっているか") 
        print("3. 他のプロセスがカメラを使用していないか")
        sys.exit(1)