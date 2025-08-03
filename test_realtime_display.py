#!/usr/bin/env python3
"""
リアルタイム物体検出表示スクリプト
libcamera + YOLOv8をリアルタイムでデスクトップに表示

libcamera-vidのストリーミング出力をfifoパイプ経由で読み取り、
YOLOv8で処理してOpenCVで表示する
"""

import argparse
import sys
import time
import os
import subprocess
import threading
import queue
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO


class LibcameraStream:
    """libcameraストリーミングクラス"""
    
    def __init__(self, width=640, height=480, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.process = None
        self.frame_queue = queue.Queue(maxsize=5)
        self.running = False
        
    def start_stream(self):
        """ストリーミングを開始"""
        try:
            # libcamera-vidでraw出力
            cmd = [
                'libcamera-vid',
                '--width', str(self.width),
                '--height', str(self.height),
                '--framerate', str(self.fps),
                '--timeout', '0',  # 無制限
                '--nopreview',
                '--codec', 'yuv420',
                '--output', '-'  # 標準出力
            ]
            
            print(f"libcamera-vidを開始: {self.width}x{self.height}@{self.fps}fps")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
            self.running = True
            
            # フレーム読み取りスレッドを開始
            self.read_thread = threading.Thread(target=self._read_frames)
            self.read_thread.daemon = True
            self.read_thread.start()
            
            return True
            
        except Exception as e:
            print(f"ストリーミング開始エラー: {e}")
            return False
    
    def _read_frames(self):
        """フレームを読み取るスレッド"""
        frame_size = self.width * self.height * 3 // 2  # YUV420
        
        while self.running and self.process and self.process.poll() is None:
            try:
                # YUV420データを読み取り
                yuv_data = self.process.stdout.read(frame_size)
                
                if len(yuv_data) != frame_size:
                    continue
                
                # YUV420をBGRに変換
                yuv_array = np.frombuffer(yuv_data, dtype=np.uint8)
                yuv_frame = yuv_array.reshape((self.height * 3 // 2, self.width))
                
                # OpenCVでYUV420からBGRに変換
                bgr_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV420p2BGR)
                
                # キューに追加（満杯の場合は古いフレームを削除）
                try:
                    self.frame_queue.put_nowait(bgr_frame)
                except queue.Full:
                    try:
                        self.frame_queue.get_nowait()  # 古いフレームを削除
                        self.frame_queue.put_nowait(bgr_frame)
                    except queue.Empty:
                        pass
                        
            except Exception as e:
                print(f"フレーム読み取りエラー: {e}")
                break
    
    def get_frame(self):
        """フレームを取得"""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """ストリーミングを停止"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()


class RealtimeDetector:
    """リアルタイム検出クラス"""
    
    def __init__(self, model_path, confidence=0.25, display_size=(800, 600)):
        self.model_path = model_path
        self.confidence = confidence
        self.display_size = display_size
        self.model = None
        self.camera_stream = None
        
    def initialize(self, stream_width=640, stream_height=480, fps=15):
        """システムを初期化"""
        
        # YOLOv8モデルを読み込み
        print(f"YOLOv8モデルを読み込み中: {self.model_path}")
        try:
            self.model = YOLO(self.model_path)
            print(f"✓ モデル読み込み成功。クラス数: {len(self.model.names)}")
        except Exception as e:
            print(f"エラー: モデルの読み込みに失敗: {e}")
            return False
        
        # カメラストリームを初期化
        self.camera_stream = LibcameraStream(stream_width, stream_height, fps)
        if not self.camera_stream.start_stream():
            return False
        
        return True
    
    def run_detection(self):
        """リアルタイム検出を実行"""
        
        # OpenCVウィンドウを作成
        window_name = "Real-time Object Detection (libcamera + YOLOv8)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.display_size[0], self.display_size[1])
        
        print("\nリアルタイム検出を開始します")
        print("'q'キーで終了します")
        print("-" * 60)
        
        frame_count = 0
        detection_count = 0
        total_inference_time = 0
        last_fps_time = time.time()
        fps_counter = 0
        current_fps = 0
        
        try:
            while True:
                # フレームを取得
                frame = self.camera_stream.get_frame()
                
                if frame is None:
                    time.sleep(0.001)  # 短時間待機
                    continue
                
                frame_count += 1
                fps_counter += 1
                
                # FPS計算（1秒ごと）
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    current_fps = fps_counter / (current_time - last_fps_time)
                    fps_counter = 0
                    last_fps_time = current_time
                
                # YOLOv8で検出
                start_time = time.time()
                results = self.model.predict(
                    source=frame,
                    device='cpu',
                    conf=self.confidence,
                    verbose=False
                )
                inference_time = (time.time() - start_time) * 1000
                total_inference_time += inference_time
                
                # 検出結果を処理
                detections = []
                if results[0].boxes is not None and len(results[0].boxes) > 0:
                    detection_count += 1
                    for box in results[0].boxes:
                        cls_id = int(box.cls)
                        conf = float(box.conf)
                        class_name = self.model.names[cls_id]
                        detections.append(f"{class_name}({conf:.2f})")
                
                # 検出結果を描画
                annotated_frame = results[0].plot()
                
                # RGB to BGR変換
                display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
                
                # 統計情報を画面に表示
                avg_inference = total_inference_time / frame_count
                info_text = [
                    f"Frame: {frame_count}",
                    f"FPS: {current_fps:.1f}",
                    f"Inference: {inference_time:.1f}ms",
                    f"Avg Inference: {avg_inference:.1f}ms",
                    f"Detections: {len(detections)}",
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
                if detections:
                    print(f"フレーム {frame_count}: {', '.join(detections)} "
                          f"| FPS: {current_fps:.1f} | 推論: {inference_time:.1f}ms")
                
                # フレームを表示
                cv2.imshow(window_name, display_frame)
                
                # キー入力をチェック
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nユーザーによって終了されました")
                    break
                elif key == ord('s'):
                    # スクリーンショット保存
                    filename = f"screenshot_{int(time.time())}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"スクリーンショットを保存: {filename}")
                    
        except KeyboardInterrupt:
            print("\n\nキーボード割り込みで終了")
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
        finally:
            # リソースを解放
            if self.camera_stream:
                self.camera_stream.stop()
            cv2.destroyAllWindows()
            
            # 統計情報を表示
            print("\n" + "=" * 60)
            print("リアルタイム検出結果サマリー")
            print("=" * 60)
            print(f"総フレーム数: {frame_count}")
            print(f"検出フレーム数: {detection_count}")
            if frame_count > 0:
                print(f"検出率: {detection_count/frame_count*100:.1f}%")
                print(f"平均推論時間: {total_inference_time/frame_count:.1f}ms")
                print(f"理論最大FPS: {1000/(total_inference_time/frame_count):.1f}")
            print("=" * 60)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="リアルタイム物体検出表示 (libcamera + YOLOv8)"
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
        help='カメラ解像度 (例: 640x480, 1280x720)'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=15,
        help='フレームレート'
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
    
    # 検出器を初期化
    detector = RealtimeDetector(
        model_path=args.model,
        confidence=args.conf,
        display_size=(display_width, display_height)
    )
    
    if not detector.initialize(width, height, args.fps):
        print("初期化に失敗しました")
        sys.exit(1)
    
    # リアルタイム検出を実行
    detector.run_detection()


if __name__ == "__main__":
    main()