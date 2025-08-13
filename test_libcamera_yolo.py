#!/usr/bin/env python3
"""
libcamera + YOLOv8 物体検出スクリプト
ファイルベースでの検出を行う

libcameraで画像を撮影し、YOLOv8で処理する方式
"""

import argparse
import sys
import time
import os
import subprocess
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO


def capture_image_libcamera(output_path: str, width: int = 640, height: int = 480) -> bool:
    """
    libcamera-stillを使用して画像を撮影
    
    Args:
        output_path: 出力ファイルパス
        width: 画像幅
        height: 画像高さ
        
    Returns:
        撮影成功可否
    """
    try:
        cmd = [
            'libcamera-still',
            '-o', output_path,
            '--width', str(width),
            '--height', str(height),
            '--timeout', '1000',  # 1秒
            '--nopreview'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and Path(output_path).exists():
            return True
        else:
            print(f"libcamera-still エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("撮影がタイムアウトしました")
        return False
    except Exception as e:
        print(f"撮影エラー: {e}")
        return False


def process_image_yolo(image_path: str, model: YOLO, confidence: float = 0.25,
                      save_result: bool = False) -> dict:
    """
    YOLOv8で画像を処理
    
    Args:
        image_path: 入力画像パス
        model: YOLOv8モデル
        confidence: 信頼度閾値
        save_result: 結果画像を保存するか
        
    Returns:
        検出結果情報
    """
    try:
        # 画像を読み込み
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "画像の読み込みに失敗"}
        
        # YOLOv8で検出
        start_time = time.time()
        results = model.predict(
            source=image,
            device='cpu',
            conf=confidence,
            verbose=False
        )
        inference_time = (time.time() - start_time) * 1000
        
        # 検出結果を処理
        detections = []
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                cls_id = int(box.cls)
                conf = float(box.conf)
                class_name = model.names[cls_id]
                
                # バウンディングボックス座標
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                detections.append({
                    "class": class_name,
                    "confidence": conf,
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                })
        
        # 結果画像を保存
        result_image_path = None
        if save_result:
            annotated_frame = results[0].plot()
            result_image_path = image_path.replace('.jpg', '_result.jpg')
            # RGB to BGR
            annotated_bgr = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(result_image_path, annotated_bgr)
        
        return {
            "detections": detections,
            "inference_time": inference_time,
            "result_image": result_image_path
        }
        
    except Exception as e:
        return {"error": f"処理エラー: {e}"}


def continuous_detection(model_path: str, confidence: float = 0.25, 
                        interval: float = 2.0, max_frames: int = 50,
                        image_size: tuple = (640, 480)):
    """
    連続的な物体検出を実行
    
    Args:
        model_path: YOLOv8モデルパス
        confidence: 信頼度閾値
        interval: 撮影間隔（秒）
        max_frames: 最大フレーム数
        image_size: 画像サイズ (width, height)
    """
    
    # モデルを読み込み
    print(f"モデルを読み込み中: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"✓ モデル読み込み成功。クラス数: {len(model.names)}")
    except Exception as e:
        print(f"エラー: モデルの読み込みに失敗: {e}")
        return False
    
    # 出力ディレクトリを作成
    output_dir = Path("libcamera_detection_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n連続検出を開始します...")
    print(f"撮影間隔: {interval}秒")
    print(f"最大フレーム数: {max_frames}")
    print(f"画像サイズ: {image_size[0]}x{image_size[1]}")
    print("Ctrl+Cで中断できます")
    print("-" * 60)
    
    frame_count = 0
    total_inference_time = 0
    total_detections = 0
    
    try:
        while frame_count < max_frames:
            frame_count += 1
            
            # 画像を撮影
            image_path = output_dir / f"frame_{frame_count:06d}.jpg"
            print(f"フレーム {frame_count}: 撮影中...", end=" ")
            
            if capture_image_libcamera(str(image_path), 
                                     image_size[0], image_size[1]):
                print("✓", end=" ")
                
                # YOLOv8で処理
                result = process_image_yolo(str(image_path), model, 
                                          confidence, save_result=True)
                
                if "error" in result:
                    print(f"エラー: {result['error']}")
                else:
                    inference_time = result["inference_time"]
                    detections = result["detections"]
                    total_inference_time += inference_time
                    total_detections += len(detections)
                    
                    if detections:
                        detection_names = [d["class"] for d in detections]
                        print(f"検出 {len(detections)} 個: {', '.join(detection_names)} "
                              f"({inference_time:.1f}ms)")
                    else:
                        print(f"検出なし ({inference_time:.1f}ms)")
                
                # 元画像を削除（結果画像のみ保持）
                if image_path.exists():
                    image_path.unlink()
                    
            else:
                print("✗ 撮影失敗")
            
            # 次の撮影まで待機
            if frame_count < max_frames:
                time.sleep(interval)
                
    except KeyboardInterrupt:
        print("\n\nキーボード割り込みで終了")
    
    # 統計情報を表示
    print("\n" + "=" * 60)
    print("検出結果サマリー")
    print("=" * 60)
    print(f"処理フレーム数: {frame_count}")
    print(f"総検出数: {total_detections}")
    if frame_count > 0:
        print(f"平均推論時間: {total_inference_time/frame_count:.1f}ms")
        print(f"検出率: {(total_detections/frame_count)*100:.1f}%")
    print(f"結果画像保存先: {output_dir}")
    print("=" * 60)
    
    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="libcamera + YOLOv8物体検出テスト"
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8n.pt',
        help='YOLOv8モデルファイルのパス'
    )
    
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='検出の信頼度閾値'
    )
    
    parser.add_argument(
        '--interval',
        type=float,
        default=2.0,
        help='撮影間隔（秒）'
    )
    
    parser.add_argument(
        '--frames',
        type=int,
        default=50,
        help='最大フレーム数'
    )
    
    parser.add_argument(
        '--size',
        type=str,
        default='640x480',
        help='画像サイズ (例: 640x480)'
    )
    
    args = parser.parse_args()
    
    # サイズを解析
    try:
        width, height = map(int, args.size.split('x'))
        image_size = (width, height)
    except ValueError:
        print(f"エラー: 無効なサイズ形式: {args.size}")
        sys.exit(1)
    
    # libcamera-stillが利用可能か確認
    try:
        result = subprocess.run(['libcamera-still', '--help'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("エラー: libcamera-stillが利用できません")
            sys.exit(1)
    except Exception as e:
        print(f"エラー: libcameraの確認に失敗: {e}")
        sys.exit(1)
    
    # 検出を実行
    success = continuous_detection(
        model_path=args.model,
        confidence=args.conf,
        interval=args.interval,
        max_frames=args.frames,
        image_size=image_size
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()