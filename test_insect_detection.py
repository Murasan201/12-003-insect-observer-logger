#!/usr/bin/env python3
"""
昆虫検出専用テストモジュール
カスタムファインチューニング済みYOLOv8モデルを使用したリアルタイム昆虫検出

特徴:
- Murasan/beetle-detection-yolov8 モデルを使用
- 昆虫（カブトムシ）専用の高精度検出
- リアルタイム表示とログ記録
- 検出統計の詳細表示
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
from datetime import datetime
import json

try:
    from ultralytics import YOLO
    print("✓ Ultralyticsが利用可能です")
except ImportError as e:
    print(f"エラー: ultralyticsがインストールされていません: {e}")
    sys.exit(1)


class InsectDetectionLogger:
    """昆虫検出ログ管理クラス"""
    
    def __init__(self, log_dir="insect_detection_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 今日の日付でログファイル名を作成
        today = datetime.now().strftime("%Y%m%d")
        self.csv_log_file = self.log_dir / f"insect_detection_{today}.csv"
        self.json_log_file = self.log_dir / f"insect_detection_{today}.json"
        
        # CSVヘッダーを初期化
        if not self.csv_log_file.exists():
            with open(self.csv_log_file, 'w') as f:
                f.write("timestamp,detected,beetle_count,confidence_max,confidence_avg,processing_time_ms\n")
        
        # JSON形式の詳細ログ
        self.detailed_logs = []
    
    def log_detection(self, detections, processing_time):
        """検出結果をログに記録"""
        timestamp = datetime.now().isoformat()
        
        # 基本統計
        beetle_count = len(detections)
        detected = 1 if beetle_count > 0 else 0
        
        confidences = [d['confidence'] for d in detections] if detections else [0]
        confidence_max = max(confidences)
        confidence_avg = sum(confidences) / len(confidences) if confidences else 0
        
        # CSV形式でログ
        with open(self.csv_log_file, 'a') as f:
            f.write(f"{timestamp},{detected},{beetle_count},{confidence_max:.3f},{confidence_avg:.3f},{processing_time:.1f}\n")
        
        # JSON形式で詳細ログ
        detailed_log = {
            "timestamp": timestamp,
            "detected": detected,
            "beetle_count": beetle_count,
            "processing_time_ms": processing_time,
            "detections": detections
        }
        self.detailed_logs.append(detailed_log)
        
        # 定期的にJSONファイルに保存（100件ごと）
        if len(self.detailed_logs) % 100 == 0:
            self.save_detailed_logs()
    
    def save_detailed_logs(self):
        """詳細ログをJSONファイルに保存"""
        if self.detailed_logs:
            existing_data = []
            if self.json_log_file.exists():
                try:
                    with open(self.json_log_file, 'r') as f:
                        existing_data = json.load(f)
                except:
                    pass
            
            existing_data.extend(self.detailed_logs)
            
            with open(self.json_log_file, 'w') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            self.detailed_logs = []
    
    def get_session_stats(self):
        """セッション統計を取得"""
        try:
            with open(self.csv_log_file, 'r') as f:
                lines = f.readlines()[1:]  # ヘッダーを除く
            
            if not lines:
                return {}
            
            total_detections = 0
            total_beetles = 0
            total_processing_time = 0
            
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 6:
                    total_detections += int(parts[1])
                    total_beetles += int(parts[2])
                    total_processing_time += float(parts[5])
            
            return {
                'total_frames': len(lines),
                'detection_frames': total_detections,
                'total_beetles': total_beetles,
                'detection_rate': (total_detections / len(lines)) * 100,
                'avg_processing_time': total_processing_time / len(lines)
            }
        except:
            return {}


def capture_and_detect_insect(model, temp_dir, logger, confidence=0.4, 
                             width=640, height=480, quality=50):
    """
    昆虫検出専用の撮影・検出処理
    
    Args:
        model: 昆虫検出用YOLOv8モデル
        temp_dir: 一時ディレクトリ
        logger: ログ管理インスタンス
        confidence: 信頼度閾値（昆虫検出用に0.4に設定）
        width: 画像幅
        height: 画像高さ
        quality: JPEG品質
        
    Returns:
        (検出結果画像, 推論時間, 検出情報リスト)
    """
    
    # 一時ファイルパス
    temp_image = temp_dir / "current_insect_frame.jpg"
    
    try:
        # libcamera-stillで高速撮影
        cmd = [
            'libcamera-still',
            '-o', str(temp_image),
            '--width', str(width),
            '--height', str(height),
            '--timeout', '500',
            '--nopreview',
            '--quality', str(quality),
            '--immediate'
        ]
        
        # 撮影実行
        subprocess.run(cmd, capture_output=True, timeout=2)
        
        if not temp_image.exists():
            return None, 0, []
        
        # 画像を読み込み
        image = cv2.imread(str(temp_image))
        if image is None:
            return None, 0, []
        
        # YOLOv8で昆虫検出
        start_time = time.time()
        results = model.predict(
            source=image,
            device='cpu',
            conf=confidence,  # 昆虫検出用に調整された閾値
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
                
                detection_info = {
                    "class": class_name,
                    "confidence": conf,
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "center": [int((x1+x2)/2), int((y1+y2)/2)],
                    "size": [int(x2-x1), int(y2-y1)]
                }
                detections.append(detection_info)
        
        # ログに記録
        logger.log_detection(detections, inference_time)
        
        # 検出結果を描画
        annotated_frame = results[0].plot()
        # RGB to BGR変換
        display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
        
        # 一時ファイルを削除
        temp_image.unlink()
        
        return display_frame, inference_time, detections
        
    except Exception as e:
        print(f"撮影・検出エラー: {e}")
        return None, 0, []


def run_insect_detection(model_path="weights/best.pt", confidence=0.4, 
                        width=640, height=480, 
                        display_size=(800, 600),
                        target_fps=3,
                        auto_save_detections=True):
    """
    昆虫検出専用リアルタイム検出を実行
    
    Args:
        model_path: 昆虫検出モデルパス
        confidence: 検出信頼度閾値
        width: カメラ解像度幅
        height: カメラ解像度高さ
        display_size: 表示ウィンドウサイズ
        target_fps: 目標FPS
        auto_save_detections: 検出時の自動画像保存
    """
    
    # 昆虫検出モデルを読み込み
    print(f"昆虫検出モデルを読み込み中: {model_path}")
    try:
        model = YOLO(model_path)
        print(f"✓ モデル読み込み成功")
        print(f"検出可能クラス: {list(model.names.values())}")
        print(f"モデル性能: mAP@0.5: 97.63%, mAP@0.5:0.95: 89.56%")
    except Exception as e:
        print(f"エラー: モデルの読み込みに失敗: {e}")
        return False
    
    # ログ管理を初期化
    logger = InsectDetectionLogger()
    print(f"✓ ログシステム初期化: {logger.log_dir}")
    
    # 一時ディレクトリを作成
    temp_dir = Path(tempfile.mkdtemp())
    
    # 検出画像保存ディレクトリ
    if auto_save_detections:
        detection_save_dir = Path("insect_detections")
        detection_save_dir.mkdir(exist_ok=True)
        print(f"✓ 検出画像保存先: {detection_save_dir}")
    
    # OpenCVウィンドウを作成
    window_name = "Insect Detection - Beetle Specialist (Fine-tuned YOLOv8)"
    try:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, display_size[0], display_size[1])
        print("✓ 表示ウィンドウ作成")
    except Exception as e:
        print(f"警告: ウィンドウの作成に失敗 (ヘッドレス環境?): {e}")
        window_name = None
    
    print(f"\n🪲 昆虫検出システム開始")
    print(f"解像度: {width}x{height}")
    print(f"信頼度閾値: {confidence}")
    print(f"目標FPS: {target_fps}")
    print("操作: 'q'キーで終了、's'キーでスクリーンショット、'r'キーで統計表示")
    print("-" * 70)
    
    frame_count = 0
    total_inference_time = 0
    total_cycle_time = 0
    beetle_detection_count = 0
    last_detection_time = None
    
    frame_interval = 1.0 / target_fps
    
    try:
        while True:
            cycle_start = time.time()
            
            # 撮影・検出・表示
            display_frame, inference_time, detections = capture_and_detect_insect(
                model, temp_dir, logger, confidence, width, height
            )
            
            if display_frame is not None:
                frame_count += 1
                total_inference_time += inference_time
                beetle_count = len(detections)
                beetle_detection_count += beetle_count
                
                if beetle_count > 0:
                    last_detection_time = datetime.now()
                
                cycle_time = (time.time() - cycle_start) * 1000
                total_cycle_time += cycle_time
                
                # 統計情報を計算
                avg_inference = total_inference_time / frame_count
                avg_cycle = total_cycle_time / frame_count
                actual_fps = 1000 / avg_cycle
                detection_rate = (beetle_detection_count / frame_count) * 100
                
                # 情報を画面に表示
                info_text = [
                    f"Insect Detection System (Beetle Specialist)",
                    f"Frame: {frame_count} | FPS: {actual_fps:.1f}",
                    f"Inference: {inference_time:.1f}ms | Avg: {avg_inference:.1f}ms",
                    f"Beetles in frame: {beetle_count}",
                    f"Total beetles detected: {beetle_detection_count}",
                    f"Detection rate: {detection_rate:.1f}%",
                    f"Last detection: {last_detection_time.strftime('%H:%M:%S') if last_detection_time else 'None'}"
                ]
                
                # 背景付きテキストを描画
                y_offset = 25
                for i, text in enumerate(info_text):
                    y_pos = y_offset + i * 30
                    
                    # フォントサイズを調整
                    font_scale = 0.6 if i == 0 else 0.5
                    thickness = 2 if i == 0 else 1
                    color = (0, 255, 255) if i == 0 else (0, 255, 0)  # 最初の行は黄色
                    
                    # テキストサイズを取得
                    (text_width, text_height), _ = cv2.getTextSize(
                        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
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
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness
                    )
                
                # 検出結果をコンソールに表示
                if beetle_count > 0:
                    detection_details = []
                    for detection in detections:
                        conf = detection['confidence']
                        size = detection['size']
                        detection_details.append(f"beetle(conf:{conf:.3f},size:{size[0]}x{size[1]})")
                    
                    print(f"🪲 フレーム {frame_count}: {', '.join(detection_details)} "
                          f"| FPS: {actual_fps:.1f} | 推論: {inference_time:.1f}ms")
                    
                    # 自動保存
                    if auto_save_detections:
                        save_filename = detection_save_dir / f"beetle_{frame_count:06d}_{datetime.now().strftime('%H%M%S')}.jpg"
                        cv2.imwrite(str(save_filename), display_frame)
                
                # フレームを表示
                if window_name:
                    cv2.imshow(window_name, display_frame)
            
            # キー入力をチェック
            if window_name:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nユーザーによって終了されました")
                    break
                elif key == ord('s') and display_frame is not None:
                    # スクリーンショット保存
                    filename = f"insect_screenshot_{int(time.time())}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"📸 スクリーンショットを保存: {filename}")
                elif key == ord('r'):
                    # 統計表示
                    stats = logger.get_session_stats()
                    print(f"\n📊 現在の統計:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                    print()
            else:
                # ヘッドレス環境では一定時間で自動終了
                if frame_count >= 100:
                    print("\nヘッドレス環境で100フレーム処理完了")
                    break
            
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
        # 最終ログ保存
        logger.save_detailed_logs()
        
        # リソースを解放
        if window_name:
            cv2.destroyAllWindows()
        
        # 一時ディレクトリを削除
        try:
            temp_dir.rmdir()
        except:
            pass
        
        # 最終統計情報を表示
        stats = logger.get_session_stats()
        print("\n" + "=" * 70)
        print("🪲 昆虫検出システム結果サマリー")
        print("=" * 70)
        print(f"総フレーム数: {frame_count}")
        print(f"昆虫検出フレーム数: {beetle_detection_count}")
        print(f"総昆虫数: {beetle_detection_count}")
        if frame_count > 0:
            print(f"検出率: {(beetle_detection_count/frame_count)*100:.1f}%")
            print(f"平均推論時間: {total_inference_time/frame_count:.1f}ms")
            print(f"平均サイクル時間: {total_cycle_time/frame_count:.1f}ms")
            print(f"実際のFPS: {1000/(total_cycle_time/frame_count):.1f}")
        print(f"ログファイル: {logger.csv_log_file}")
        print(f"詳細ログ: {logger.json_log_file}")
        if auto_save_detections:
            print(f"検出画像: insect_detections/")
        print("=" * 70)
    
    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="昆虫検出専用リアルタイム検出システム (Fine-tuned YOLOv8)"
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='weights/best.pt',
        help='昆虫検出モデルファイルのパス'
    )
    
    parser.add_argument(
        '--conf',
        type=float,
        default=0.4,
        help='検出の信頼度閾値 (昆虫検出用: 推奨0.3-0.5)'
    )
    
    parser.add_argument(
        '--size',
        type=str,
        default='640x480',
        help='カメラ解像度 (例: 640x480, 1280x720)'
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
        default='900x700',
        help='表示ウィンドウサイズ'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='検出画像の自動保存を無効化'
    )
    
    args = parser.parse_args()
    
    # モデルファイルの存在確認
    if not Path(args.model).exists():
        print(f"エラー: モデルファイル '{args.model}' が見つかりません。")
        print("以下のコマンドでダウンロードしてください:")
        print("python3 -c \"from huggingface_hub import hf_hub_download; hf_hub_download('Murasan/beetle-detection-yolov8', 'best.pt', local_dir='./weights')\"")
        sys.exit(1)
    
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
    
    # 昆虫検出を実行
    success = run_insect_detection(
        model_path=args.model,
        confidence=args.conf,
        width=width,
        height=height,
        display_size=(display_width, display_height),
        target_fps=args.fps,
        auto_save_detections=not args.no_save
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()