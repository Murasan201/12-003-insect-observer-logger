#!/usr/bin/env python3
"""
libcameraを使用したカメラテスト
Raspberry Pi Camera Module 3用
"""

import cv2
import numpy as np
import time

def test_libcamera():
    """libcameraを使用してカメラをテスト"""
    
    print("libcameraを使用したカメラテストを開始...")
    
    # いくつかの異なる設定を試す
    pipelines = [
        # 基本的なlibcameraパイプライン
        "libcamerasrc ! video/x-raw,width=640,height=480 ! videoconvert ! appsink",
        
        # フォーマットを明示的に指定
        "libcamerasrc ! video/x-raw,format=RGB,width=640,height=480 ! videoconvert ! appsink",
        
        # より低い解像度で試す
        "libcamerasrc ! video/x-raw,width=320,height=240 ! videoconvert ! appsink",
    ]
    
    for i, pipeline in enumerate(pipelines):
        print(f"\n試行 {i+1}: {pipeline[:50]}...")
        
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        
        if cap.isOpened():
            print("✓ カメラを開けました")
            
            # 複数フレーム取得を試みる
            success_count = 0
            for j in range(10):
                ret, frame = cap.read()
                if ret:
                    success_count += 1
                    if success_count == 1:
                        print(f"✓ フレーム取得成功: {frame.shape}")
                        cv2.imwrite(f"libcamera_test_{i}.jpg", frame)
                        print(f"  libcamera_test_{i}.jpg として保存")
                
                time.sleep(0.1)
            
            print(f"  成功フレーム数: {success_count}/10")
            cap.release()
            
            if success_count > 0:
                return True
        else:
            print("✗ カメラを開けませんでした")
    
    return False

def test_v4l2_direct():
    """V4L2を直接使用してテスト"""
    print("\nV4L2直接アクセスをテスト...")
    
    # 異なるビデオデバイスを試す
    for device_id in range(5):
        device_path = f"/dev/video{device_id}"
        print(f"\n{device_path}を試行中...")
        
        cap = cv2.VideoCapture(device_id, cv2.CAP_V4L2)
        
        if cap.isOpened():
            # いくつかのプロパティを設定
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # フレーム取得
            for _ in range(5):
                ret, frame = cap.read()
                if ret:
                    print(f"✓ {device_path} からフレーム取得成功: {frame.shape}")
                    cv2.imwrite(f"v4l2_test_{device_id}.jpg", frame)
                    cap.release()
                    return True
                time.sleep(0.2)
            
            cap.release()
    
    return False

def main():
    """メイン処理"""
    print("Raspberry Pi Camera Module 3 テスト")
    print("=" * 50)
    
    # libcameraテスト
    if test_libcamera():
        print("\n成功: libcameraでカメラが動作しました")
        return
    
    # V4L2直接テスト
    if test_v4l2_direct():
        print("\n成功: V4L2でカメラが動作しました")
        return
    
    print("\nすべての方法が失敗しました")
    print("\n推奨される対処法:")
    print("1. libcamera-hello -t 5000 でカメラが動作するか確認")
    print("2. sudo systemctl restart camera でカメラサービスを再起動")
    print("3. Raspberry Piを再起動")

if __name__ == "__main__":
    main()