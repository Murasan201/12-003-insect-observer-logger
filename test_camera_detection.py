#!/usr/bin/env python3
"""
カメラ入力によるYOLOv8物体検出テストスクリプト

リアルタイムでカメラからの映像を取得し、YOLOv8モデルで物体検出を実行します。
検出結果をウィンドウに表示し、'q'キーで終了します。

使用方法:
    python test_camera_detection.py
    python test_camera_detection.py --model weights/best.pt
    python test_camera_detection.py --camera 1
"""

import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


def test_camera_detection(model_path: str = 'yolov8n.pt', camera_id: int = 0, confidence: float = 0.25, max_attempts: int = 5):
    """
    カメラからの映像でYOLOv8物体検出をテストします。
    
    Args:
        model_path: YOLOv8モデルファイルのパス
        camera_id: 使用するカメラのID（通常は0）
        confidence: 検出の信頼度閾値
    """
    # モデルを読み込み
    print(f"モデルを読み込み中: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"モデルの読み込みが成功しました。クラス数: {len(model.names)}")
        print(f"検出可能クラス: {list(model.names.values())}")
    except Exception as e:
        print(f"エラー: モデルの読み込みに失敗しました: {e}")
        return False
    
    # カメラを開く
    print(f"カメラ {camera_id} を初期化中...")
    
    # まずデフォルトのバックエンドで試す
    cap = cv2.VideoCapture(camera_id)
    
    # 開けない場合は、V4L2バックエンドを明示的に指定
    if not cap.isOpened():
        print("デフォルトバックエンドで開けませんでした。V4L2を試しています...")
        cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
    
    # それでも開けない場合は、GStreamerパイプラインを試す
    if not cap.isOpened():
        print("V4L2でも開けませんでした。libcameraを試しています...")
        # libcamera-vid互換のパイプライン
        pipeline = "libcamerasrc ! video/x-raw,width=640,height=480,framerate=30/1 ! videoconvert ! appsink"
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    
    if not cap.isOpened():
        print(f"エラー: カメラ {camera_id} を開けませんでした")
        print("ヒント: 仮想環境の外で実行するか、システムのOpenCVを使用してください")
        return False
    
    # カメラの解像度を取得
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"カメラ解像度: {width}x{height} @ {fps}fps")
    
    # ウィンドウを作成
    window_name = "YOLO Object Detection Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    print("\n検出を開始します。'q'キーで終了します。")
    print("-" * 50)
    
    frame_count = 0
    total_time = 0
    
    # 最初のフレーム取得を待つ
    print("カメラの初期化を待っています...")
    for i in range(max_attempts):
        ret, frame = cap.read()
        if ret:
            print("カメラの準備ができました！")
            break
        print(f"待機中... ({i+1}/{max_attempts})")
        time.sleep(1)
    else:
        print("エラー: カメラからフレームを取得できませんでした")
        cap.release()
        cv2.destroyAllWindows()
        return False

    try:
        while True:
            # フレームを取得
            ret, frame = cap.read()
            if not ret:
                print("警告: フレームの取得に失敗しました")
                # 少し待って再試行
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
            avg_time = total_time / frame_count
            current_fps = 1000 / inference_time if inference_time > 0 else 0
            
            # 検出結果を描画
            annotated_frame = results[0].plot()
            
            # 検出情報をコンソールに表示
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                detections = []
                for box in results[0].boxes:
                    cls_id = int(box.cls)
                    conf = float(box.conf)
                    class_name = model.names[cls_id]
                    detections.append(f"{class_name}({conf:.2f})")
                
                print(f"フレーム {frame_count}: 検出 {len(detections)} 個 - {', '.join(detections)} | "
                      f"処理時間: {inference_time:.1f}ms | FPS: {current_fps:.1f}")
            
            # 情報をフレームに追加
            info_text = [
                f"Frame: {frame_count}",
                f"Inference: {inference_time:.1f}ms",
                f"Avg: {avg_time:.1f}ms",
                f"FPS: {current_fps:.1f}"
            ]
            
            y_offset = 30
            for i, text in enumerate(info_text):
                cv2.putText(annotated_frame, text, (10, y_offset + i * 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # フレームを表示
            cv2.imshow(window_name, annotated_frame)
            
            # 'q'キーで終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nユーザーによって終了されました")
                break
                
    except KeyboardInterrupt:
        print("\n\nキーボード割り込みで終了しました")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        return False
    finally:
        # リソースを解放
        cap.release()
        cv2.destroyAllWindows()
        
        # 統計情報を表示
        print("\n" + "=" * 50)
        print("テスト結果サマリー")
        print("=" * 50)
        print(f"総フレーム数: {frame_count}")
        if frame_count > 0:
            print(f"平均処理時間: {avg_time:.1f}ms")
            print(f"平均FPS: {1000/avg_time:.1f}")
        else:
            print("警告: フレームが取得できませんでした")
        print("=" * 50)
    
    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="カメラ入力によるYOLOv8物体検出テスト"
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8n.pt',
        help='YOLOv8モデルファイルのパス (デフォルト: yolov8n.pt)'
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='使用するカメラのID (デフォルト: 0)'
    )
    
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='検出の信頼度閾値 (デフォルト: 0.25)'
    )
    
    args = parser.parse_args()
    
    # モデルファイルの存在確認
    if not Path(args.model).exists() and not args.model.endswith('.pt'):
        print(f"警告: モデルファイル '{args.model}' が見つかりません。")
        print("Ultralyticsが自動的にダウンロードを試みます。")
    
    # テストを実行
    success = test_camera_detection(
        model_path=args.model,
        camera_id=args.camera,
        confidence=args.conf
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()