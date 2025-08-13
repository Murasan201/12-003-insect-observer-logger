#!/usr/bin/env python3
"""
シンプル昆虫観測アプリケーション

既存のinsect_detector.pyを利用して、継続的に昆虫の観測を行い、
結果をCSVファイルに保存するシンプルなアプリケーション。

使用方法:
    python simple_observer.py --interval 60 --duration 3600
    
    --interval: 観測間隔（秒）デフォルト: 60秒
    --duration: 観測時間（秒）デフォルト: 継続実行
"""

import logging
import time
import csv
import signal
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# 既存の検出器をインポート
from insect_detector import InsectDetector, DetectionSettings


class SimpleObserver:
    """シンプル昆虫観測クラス"""
    
    def __init__(self, interval: int = 60, duration: Optional[int] = None, 
                 output_dir: str = "./simple_logs"):
        """
        初期化
        
        Args:
            interval: 観測間隔（秒）
            duration: 観測時間（秒、Noneで無制限）
            output_dir: 出力ディレクトリ
        """
        self.interval = interval
        self.duration = duration
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # ログ設定
        self._setup_logging()
        
        # 検出器設定
        self.detector_settings = DetectionSettings(
            model_path="./weights/beetle_detection.pt",
            confidence_threshold=0.5,
            device="cpu",
            save_detection_images=True,
            save_detection_logs=False  # 独自のCSV保存を使用
        )
        
        # 検出器初期化
        self.detector = None
        self.is_running = False
        self.start_time = None
        self.observation_count = 0
        
        # CSVファイル設定
        self.csv_file = None
        self.csv_writer = None
        
        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """ログ設定"""
        log_file = self.output_dir / f"observer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラー（Ctrl+C対応）"""
        self.logger.info(f"Signal {signum} received. Stopping observation...")
        self.stop()
    
    def _setup_csv(self) -> bool:
        """CSV出力ファイルの設定"""
        try:
            csv_filename = f"observations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_path = self.output_dir / csv_filename
            
            self.csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            
            # CSVヘッダー書き込み
            headers = [
                'timestamp',
                'detection_count',
                'has_detection',
                'confidence_avg',
                'x_center_avg',
                'y_center_avg',
                'processing_time_ms',
                'observation_number'
            ]
            self.csv_writer.writerow(headers)
            self.csv_file.flush()
            
            self.logger.info(f"CSV file created: {csv_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup CSV file: {e}")
            return False
    
    def _save_observation_to_csv(self, observation_data: Dict[str, Any]):
        """観測結果をCSVに保存"""
        try:
            if self.csv_writer:
                row = [
                    observation_data['timestamp'],
                    observation_data['detection_count'],
                    observation_data['has_detection'],
                    observation_data['confidence_avg'],
                    observation_data['x_center_avg'],
                    observation_data['y_center_avg'],
                    observation_data['processing_time_ms'],
                    observation_data['observation_number']
                ]
                self.csv_writer.writerow(row)
                self.csv_file.flush()
                
        except Exception as e:
            self.logger.error(f"Failed to save observation to CSV: {e}")
    
    def initialize(self) -> bool:
        """観測システム初期化"""
        try:
            self.logger.info("Initializing Simple Observer...")
            
            # CSV設定
            if not self._setup_csv():
                return False
            
            # 検出器初期化
            self.detector = InsectDetector(self.detector_settings)
            if not self.detector.initialize():
                self.logger.error("Failed to initialize detector")
                return False
            
            self.logger.info("Simple Observer initialized successfully")
            self.logger.info(f"Observation interval: {self.interval} seconds")
            if self.duration:
                self.logger.info(f"Observation duration: {self.duration} seconds")
            else:
                self.logger.info("Observation duration: Unlimited (until stopped)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def start_observation(self):
        """観測開始"""
        if not self.initialize():
            self.logger.error("Cannot start observation due to initialization failure")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        self.observation_count = 0
        
        self.logger.info("=== Starting Simple Insect Observation ===")
        self.logger.info(f"Start time: {self.start_time}")
        
        try:
            while self.is_running:
                # 観測実行
                observation_result = self._perform_single_observation()
                
                if observation_result:
                    self._save_observation_to_csv(observation_result)
                    self._log_observation_result(observation_result)
                
                # 終了条件チェック
                if self.duration and self._should_stop():
                    self.logger.info("Observation duration completed")
                    break
                
                # 次の観測まで待機
                if self.is_running:
                    self.logger.debug(f"Waiting {self.interval} seconds for next observation...")
                    time.sleep(self.interval)
                    
        except KeyboardInterrupt:
            self.logger.info("Observation interrupted by user")
        except Exception as e:
            self.logger.error(f"Observation error: {e}")
        finally:
            self.stop()
    
    def _perform_single_observation(self) -> Optional[Dict[str, Any]]:
        """単一観測の実行"""
        try:
            self.observation_count += 1
            start_time = time.time()
            
            self.logger.debug(f"Performing observation #{self.observation_count}")
            
            # 検出実行
            detection_record = self.detector.detect_single_image(
                use_ir_led=True,
                save_result=True
            )
            
            processing_time = (time.time() - start_time) * 1000  # ミリ秒
            
            if detection_record is None:
                self.logger.warning("Detection failed")
                return None
            
            # 結果の集計
            detections = detection_record.detections
            detection_count = len(detections)
            has_detection = detection_count > 0
            
            # 平均値計算
            if has_detection:
                confidence_avg = sum(d.confidence for d in detections) / detection_count
                x_center_avg = sum(d.x_center for d in detections) / detection_count
                y_center_avg = sum(d.y_center for d in detections) / detection_count
            else:
                confidence_avg = 0.0
                x_center_avg = 0.0
                y_center_avg = 0.0
            
            # 結果データ作成
            observation_data = {
                'timestamp': detection_record.timestamp,
                'detection_count': detection_count,
                'has_detection': has_detection,
                'confidence_avg': round(confidence_avg, 3),
                'x_center_avg': round(x_center_avg, 1),
                'y_center_avg': round(y_center_avg, 1),
                'processing_time_ms': round(processing_time, 1),
                'observation_number': self.observation_count
            }
            
            return observation_data
            
        except Exception as e:
            self.logger.error(f"Single observation failed: {e}")
            return None
    
    def _log_observation_result(self, result: Dict[str, Any]):
        """観測結果のログ出力"""
        if result['has_detection']:
            self.logger.info(
                f"#{result['observation_number']}: "
                f"{result['detection_count']} insects detected "
                f"(confidence: {result['confidence_avg']}, "
                f"time: {result['processing_time_ms']}ms)"
            )
        else:
            self.logger.info(
                f"#{result['observation_number']}: "
                f"No insects detected "
                f"(time: {result['processing_time_ms']}ms)"
            )
    
    def _should_stop(self) -> bool:
        """終了判定"""
        if not self.duration:
            return False
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed >= self.duration
    
    def stop(self):
        """観測停止"""
        self.is_running = False
        
        # 統計情報表示
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            self.logger.info("=== Observation Summary ===")
            self.logger.info(f"Total observations: {self.observation_count}")
            self.logger.info(f"Total time: {elapsed}")
            self.logger.info(f"Average interval: {elapsed.total_seconds() / max(1, self.observation_count):.1f} seconds")
        
        # リソースクリーンアップ
        if self.detector:
            self.detector.cleanup()
        
        if self.csv_file:
            self.csv_file.close()
            self.logger.info("CSV file closed")
        
        self.logger.info("Simple Observer stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """現在の状態取得"""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
        else:
            elapsed = timedelta(0)
        
        return {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'elapsed_time': str(elapsed),
            'observation_count': self.observation_count,
            'interval_seconds': self.interval,
            'duration_seconds': self.duration,
            'output_directory': str(self.output_dir)
        }


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='Simple Insect Observer')
    parser.add_argument('--interval', type=int, default=60,
                       help='Observation interval in seconds (default: 60)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Observation duration in seconds (default: unlimited)')
    parser.add_argument('--output-dir', type=str, default='./simple_logs',
                       help='Output directory (default: ./simple_logs)')
    
    args = parser.parse_args()
    
    # 観測器作成・実行
    observer = SimpleObserver(
        interval=args.interval,
        duration=args.duration,
        output_dir=args.output_dir
    )
    
    try:
        observer.start_observation()
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()