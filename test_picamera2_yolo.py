#!/usr/bin/env python3
"""
Picamera2 + YOLOv8 物体検出スクリプト
Raspberry Pi Camera Module 3専用

numpyの互換性問題を回避するため、システムのPicamera2を使用
"""

import argparse
import sys
import time
import os
from pathlib import Path

# numpy互換性のため、最初にPicamera2をインポート
try:
    from picamera2 import Picamera2
    print("✓ Picamera2が利用可能です")
except ImportError as e:
    print(f"エラー: Picamera2がインストールされていません: {e}")
    print("sudo apt install -y python3-picamera2")
    sys.exit(1)

import cv2
import numpy as np

# YOLOv8をインポート
try:
    from ultralytics import YOLO
    print("✓ Ultralyticsが利用可能です")
except ImportError as e:
    print(f"エラー: ultralyticsがインストールされていません: {e}")
    print("sudo pip3 install ultralytics --break-system-packages")
    sys.exit(1)


def test_picamera2_yolo(model_path: str = 'yolov8n.pt', confidence: float = 0.25, 
                       preview_size: tuple = (640, 480), save_images: bool = False):
    """
    Picamera2とYOLOv8を使用した物体検出
    
    Args:
        model_path: YOLOv8モデルファイルのパス
        confidence: 検出の信頼度閾値
        preview_size: プレビューサイズ (width, height)
        save_images: 検出画像を保存するかどうか
    """
    
    # YOLOv8モデルを読み込み
    print(f"モデルを読み込み中: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"✓ モデルの読み込み成功。クラス数: {len(model.names)}")
        print(f"検出可能クラス: {list(model.names.values())[:10]}..." + 
              ("など" if len(model.names) > 10 else ""))
    except Exception as e:
        print(f"エラー: モデルの読み込みに失敗: {e}")
        return False
    
    # Picamera2を初期化
    print("\nPicamera2を初期化中...")
    try:
        picam2 = Picamera2()
        
        # カメラ設定を作成
        config = picam2.create_preview_configuration(
            main={"size": preview_size, "format": "RGB888"}
        )
        picam2.configure(config)
        
        print(f"✓ カメラ設定完了: {preview_size[0]}x{preview_size[1]}")
        
        # カメラを開始
        picam2.start()
        print("✓ カメラ開始")
        
        # ウォームアップ
        print("カメラのウォームアップ中...")
        time.sleep(2)
        
    except Exception as e:
        print(f"エラー: Picamera2の初期化に失敗: {e}")
        return False
    
    # OpenCVウィンドウを作成
    window_name = "Picamera2 + YOLOv8 Detection"
    try:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        print("✓ OpenCVウィンドウ作成")
    except Exception as e:
        print(f"警告: ウィンドウの作成に失敗 (ヘッドレス環境?): {e}")
        window_name = None
    
    print("\n物体検出を開始します。'q'キーで終了します。")
    print("-" * 60)
    
    frame_count = 0
    total_inference_time = 0
    detection_count = 0
    
    try:
        while True:
            start_time = time.time()
            
            # フレームを取得
            frame = picam2.capture_array()
            
            if frame is None:
                print("警告: フレームの取得に失敗")
                continue
            
            frame_count += 1
            
            # YOLOv8で検出を実行
            inference_start = time.time()
            results = model.predict(
                source=frame,
                device='cpu',
                conf=confidence,
                verbose=False
            )
            inference_time = (time.time() - inference_start) * 1000
            total_inference_time += inference_time
            
            # 検出結果を処理
            detections = []
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                detection_count += 1
                for box in results[0].boxes:
                    cls_id = int(box.cls)
                    conf = float(box.conf)
                    class_name = model.names[cls_id]
                    detections.append(f"{class_name}({conf:.2f})")
                
                print(f"フレーム {frame_count}: 検出 {len(detections)} 個 - "
                      f"{', '.join(detections)} | 推論時間: {inference_time:.1f}ms")
            
            # 検出結果を描画（RGB→BGR変換）
            annotated_frame = results[0].plot()
            bgr_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
            
            # FPS情報を追加
            fps = 1000 / inference_time if inference_time > 0 else 0
            avg_inference = total_inference_time / frame_count
            
            info_text = [
                f"Frame: {frame_count}",
                f"Inference: {inference_time:.1f}ms",
                f"Avg: {avg_inference:.1f}ms",
                f"FPS: {fps:.1f}",
                f"Detections: {detection_count}"
            ]
            
            y_offset = 30
            for i, text in enumerate(info_text):
                cv2.putText(bgr_frame, text, (10, y_offset + i * 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 画像を保存（オプション）
            if save_images and len(detections) > 0:
                filename = f"detection_{frame_count:06d}.jpg"
                cv2.imwrite(filename, bgr_frame)
            
            # フレームを表示
            if window_name:
                cv2.imshow(window_name, bgr_frame)
                
                # キー入力をチェック
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nユーザーによって終了されました")
                    break
            else:
                # ヘッドレス環境では一定時間で自動終了
                if frame_count >= 100:
                    print("\nヘッドレス環境で100フレーム処理完了")
                    break
            
            # フレームレート制御
            time.sleep(0.033)  # 約30fps
                
    except KeyboardInterrupt:
        print("\n\nキーボード割り込みで終了")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        return False
    finally:
        # リソースを解放
        picam2.stop()
        if window_name:
            cv2.destroyAllWindows()
        
        # 統計情報を表示
        print("\n" + "=" * 60)
        print("テスト結果サマリー")
        print("=" * 60)
        print(f"総フレーム数: {frame_count}")
        print(f"検出フレーム数: {detection_count}")
        print(f"検出率: {detection_count/frame_count*100:.1f}%")
        if frame_count > 0:
            print(f"平均推論時間: {total_inference_time/frame_count:.1f}ms")
            print(f"平均FPS: {1000/(total_inference_time/frame_count):.1f}")
        print("=" * 60)
    
    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Picamera2 + YOLOv8物体検出テスト"
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8n.pt',
        help='YOLOv8モデルファイルのパス (デフォルト: yolov8n.pt)'
    )
    
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='検出の信頼度閾値 (デフォルト: 0.25)'
    )
    
    parser.add_argument(
        '--size',
        type=str,
        default='640x480',
        help='プレビューサイズ (例: 640x480, 1280x720)'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='検出画像を保存する'
    )
    
    args = parser.parse_args()
    
    # サイズを解析
    try:
        width, height = map(int, args.size.split('x'))
        preview_size = (width, height)
    except ValueError:
        print(f"エラー: 無効なサイズ形式: {args.size}")
        sys.exit(1)
    
    # モデルファイルの存在確認
    if not Path(args.model).exists() and not args.model.endswith('.pt'):
        print(f"警告: モデルファイル '{args.model}' が見つかりません。")
        print("Ultralyticsが自動的にダウンロードを試みます。")
    
    # テストを実行
    success = test_picamera2_yolo(
        model_path=args.model,
        confidence=args.conf,
        preview_size=preview_size,
        save_images=args.save
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()