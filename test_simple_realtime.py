#!/usr/bin/env python3
"""
シンプルなリアルタイム表示スクリプト
libcamera-stillを高速で連続実行してリアルタイム風に表示

簡単で確実に動作する方式
"""

import argparse
import sys
import time
import os
import subprocess
import tempfile
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO


def capture_and_detect(model, temp_dir, confidence=0.25, 
                      width=640, height=480, quality=50):
    """
    1フレーム分の撮影・検出・表示を実行
    
    Args:
        model: YOLOv8モデル
        temp_dir: 一時ディレクトリ
        confidence: 信頼度閾値
        width: 画像幅
        height: 画像高さ
        quality: JPEG品質（低品質で高速化）
        
    Returns:
        (検出結果画像, 推論時間, 検出数)
    """
    
    # 一時ファイルパス
    temp_image = temp_dir / "current_frame.jpg"
    
    try:
        # libcamera-stillで高速撮影
        cmd = [
            'libcamera-still',
            '-o', str(temp_image),
            '--width', str(width),
            '--height', str(height),
            '--timeout', '500',  # 500ms
            '--nopreview',
            '--quality', str(quality),  # 低品質で高速化
            '--immediate'  # 即座に撮影
        ]
        
        # 撮影実行
        subprocess.run(cmd, capture_output=True, timeout=2)
        
        if not temp_image.exists():
            return None, 0, 0
        
        # 画像を読み込み
        image = cv2.imread(str(temp_image))
        if image is None:
            return None, 0, 0
        
        # YOLOv8で検出
        start_time = time.time()
        results = model.predict(
            source=image,
            device='cpu',
            conf=confidence,
            verbose=False
        )
        inference_time = (time.time() - start_time) * 1000
        
        # 検出結果を描画
        annotated_frame = results[0].plot()
        # RGB to BGR変換
        display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
        
        # 検出数を計算
        detection_count = 0
        if results[0].boxes is not None:
            detection_count = len(results[0].boxes)
        
        # 一時ファイルを削除
        temp_image.unlink()
        
        return display_frame, inference_time, detection_count
        
    except Exception as e:
        print(f"撮影・検出エラー: {e}")
        return None, 0, 0


def run_simple_realtime(model_path, confidence=0.25, 
                       width=640, height=480, 
                       display_size=(800, 600),
                       target_fps=5):
    """
    シンプルなリアルタイム検出を実行
    
    Args:
        model_path: YOLOv8モデルパス
        confidence: 信頼度閾値
        width: カメラ解像度幅
        height: カメラ解像度高さ
        display_size: 表示ウィンドウサイズ
        target_fps: 目標FPS
    """
    
    # YOLOv8モデルを読み込み
    print(f"YOLOv8モデルを読み込み中: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"✓ モデル読み込み成功。クラス数: {len(model.names)}")
    except Exception as e:
        print(f"エラー: モデルの読み込みに失敗: {e}")
        return False
    
    # 一時ディレクトリを作成
    temp_dir = Path(tempfile.mkdtemp())
    
    # OpenCVウィンドウを作成
    window_name = "Simple Real-time Detection (libcamera + YOLOv8)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, display_size[0], display_size[1])
    
    print(f"\nシンプルリアルタイム検出を開始")
    print(f"解像度: {width}x{height}")
    print(f"目標FPS: {target_fps}")
    print("'q'キーで終了、's'キーでスクリーンショット保存")
    print("-" * 60)
    
    frame_count = 0
    detection_count = 0
    total_inference_time = 0
    total_cycle_time = 0
    
    frame_interval = 1.0 / target_fps
    
    try:
        while True:
            cycle_start = time.time()
            
            # 撮影・検出・表示
            display_frame, inference_time, detections = capture_and_detect(
                model, temp_dir, confidence, width, height
            )
            
            if display_frame is not None:
                frame_count += 1
                total_inference_time += inference_time
                detection_count += detections
                
                cycle_time = (time.time() - cycle_start) * 1000
                total_cycle_time += cycle_time
                
                # 統計情報を画面に表示
                avg_inference = total_inference_time / frame_count
                avg_cycle = total_cycle_time / frame_count
                actual_fps = 1000 / avg_cycle
                
                info_text = [
                    f"Frame: {frame_count}",
                    f"FPS: {actual_fps:.1f}",
                    f"Inference: {inference_time:.1f}ms",
                    f"Cycle: {cycle_time:.1f}ms",
                    f"Detections: {detections}",
                    f"Total Detected: {detection_count}"
                ]
                
                # 背景付きテキストを描画
                y_offset = 30
                for i, text in enumerate(info_text):
                    y_pos = y_offset + i * 30
                    
                    # テキストサイズを取得
                    (text_width, text_height), _ = cv2.getTextSize(
                        text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                    )
                    
                    # 背景矩形を描画
                    cv2.rectangle(
                        display_frame, 
                        (5, y_pos - text_height - 5), 
                        (text_width + 15, y_pos + 5),
                        (0, 0, 0), 
                        -1
                    )
                    
                    # テキストを描画
                    cv2.putText(
                        display_frame, text, (10, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )
                
                # 検出結果をコンソールに表示（検出があった場合のみ）
                if detections > 0:
                    print(f"フレーム {frame_count}: 検出 {detections} 個 "
                          f"| FPS: {actual_fps:.1f} | 推論: {inference_time:.1f}ms")
                
                # フレームを表示
                cv2.imshow(window_name, display_frame)
            
            # キー入力をチェック
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nユーザーによって終了されました")
                break
            elif key == ord('s') and display_frame is not None:
                # スクリーンショット保存
                filename = f"screenshot_{int(time.time())}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"スクリーンショットを保存: {filename}")
            
            # フレームレート制御
            elapsed = time.time() - cycle_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\n\nキーボード割り込みで終了")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
    finally:
        # リソースを解放
        cv2.destroyAllWindows()
        
        # 一時ディレクトリを削除
        try:
            temp_dir.rmdir()
        except:
            pass
        
        # 統計情報を表示
        print("\n" + "=" * 60)
        print("シンプルリアルタイム検出結果サマリー")
        print("=" * 60)
        print(f"総フレーム数: {frame_count}")
        print(f"総検出数: {detection_count}")
        if frame_count > 0:
            print(f"検出率: {(detection_count/frame_count)*100:.1f}%")
            print(f"平均推論時間: {total_inference_time/frame_count:.1f}ms")
            print(f"平均サイクル時間: {total_cycle_time/frame_count:.1f}ms")
            print(f"実際のFPS: {1000/(total_cycle_time/frame_count):.1f}")
        print("=" * 60)
    
    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="シンプルリアルタイム物体検出表示"
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
        '--size',
        type=str,
        default='640x480',
        help='カメラ解像度 (例: 640x480)'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=3,
        help='目標FPS（推奨: 2-5）'
    )
    
    parser.add_argument(
        '--display-size',
        type=str,
        default='800x600',
        help='表示ウィンドウサイズ'
    )
    
    args = parser.parse_args()
    
    # サイズを解析
    try:
        width, height = map(int, args.size.split('x'))
        display_width, display_height = map(int, args.display_size.split('x'))
    except ValueError:
        print("エラー: 無効なサイズ形式")
        sys.exit(1)
    
    # libcamera-stillが利用可能か確認
    try:
        result = subprocess.run(['libcamera-still', '--help'], 
                              capture_output=True, timeout=5)
        if result.returncode != 0:
            print("エラー: libcamera-stillが利用できません")
            sys.exit(1)
    except Exception as e:
        print(f"エラー: libcameraの確認に失敗: {e}")
        sys.exit(1)
    
    # リアルタイム検出を実行
    success = run_simple_realtime(
        model_path=args.model,
        confidence=args.conf,
        width=width,
        height=height,
        display_size=(display_width, display_height),
        target_fps=args.fps
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()