"""
昆虫自動観察システム メインコントローラー

システム全体の統合制御とライフサイクル管理を行う。
- システム初期化・終了処理
- 定期実行スケジューリング
- 各モジュール間の連携制御
- エラーハンドリングと復旧処理
- システム状態監視
"""

import logging
import time
import signal
import sys
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import json

# プロジェクト内モジュール
from config.config_manager import ConfigManager
from hardware_controller import HardwareController
from insect_detector import InsectDetector, DetectionSettings
from detection_processor import DetectionProcessor, ProcessingSettings
from activity_calculator import ActivityCalculator, CalculationSettings
from data_processor import DataProcessor, ProcessingSettings as DataProcessingSettings
from visualization import Visualizer, VisualizationSettings
from model_manager import ModelManager
from system_controller import SystemController
from scheduler import SchedulerManager
from error_handler import ErrorHandler, ErrorSeverity, ErrorCategory, ErrorContext, error_handler_decorator
from monitoring import SystemMonitor


@dataclass
class SystemStatus:
    """システム状態情報"""
    is_running: bool = False
    start_time: str = ""
    uptime_seconds: float = 0.0
    total_detections: int = 0
    total_images_processed: int = 0
    last_detection_time: str = ""
    current_mode: str = "idle"  # idle, detecting, analyzing, maintenance
    error_count: int = 0
    last_error: str = ""


class InsectObserverSystem:
    """
    昆虫観察システムのメインコントローラー
    
    Features:
    - 全モジュールの統合管理
    - 定期検出スケジューリング
    - 自動分析・レポート生成
    - システム監視・ヘルスチェック
    - エラー処理・自動復旧
    - 設定動的更新
    """
    
    def __init__(self, config_path: str = "./config/system_config.json"):
        """
        システム初期化
        
        Args:
            config_path: 設定ファイルパス
        """
        self.logger = logging.getLogger(__name__ + '.InsectObserverSystem')
        
        # 設定管理
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        
        # システム状態
        self.status = SystemStatus()
        self.shutdown_requested = False
        
        # エラーハンドリング・監視機能
        error_config = self.config.system.get('error_handling', {})
        self.error_handler = ErrorHandler(error_config)
        
        monitoring_config = self.config.system.get('monitoring', {})
        self.system_monitor = SystemMonitor(monitoring_config)
        
        # 各モジュール
        self.hardware_controller: Optional[HardwareController] = None
        self.model_manager: Optional[ModelManager] = None
        self.detector: Optional[InsectDetector] = None
        self.detection_processor: Optional[DetectionProcessor] = None
        self.activity_calculator: Optional[ActivityCalculator] = None
        self.data_processor: Optional[DataProcessor] = None
        self.visualizer: Optional[Visualizer] = None
        self.system_controller: Optional[SystemController] = None
        self.scheduler: Optional[SchedulerManager] = None
        
        # スレッド管理
        self.main_thread: Optional[threading.Thread] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # シグナルハンドラ設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Insect Observer System initialized")
    
    def initialize_system(self) -> bool:
        """
        システム初期化処理
        
        Returns:
            bool: 初期化成功可否
        """
        context = ErrorContext(
            module_name=__name__,
            function_name="initialize_system"
        )
        
        try:
            self.logger.info("Starting system initialization...")
            
            # 監視開始
            self.system_monitor.start_monitoring()
            
            # 1. モデル管理器初期化
            self.model_manager = ModelManager(
                model_dir=self.config.paths.weights_dir,
                config_manager=self.config_manager
            )
            
            # モデル自動セットアップ
            if not self.model_manager.auto_setup():
                self.logger.error("Model setup failed")
                return False
            
            # 2. ハードウェア制御器初期化
            hardware_config = {
                'camera': {
                    'resolution': self.config.hardware.camera.resolution,
                    'exposure_time': self.config.hardware.camera.exposure_time,
                    'analogue_gain': self.config.hardware.camera.analogue_gain
                },
                'led': {
                    'led_pin': self.config.hardware.ir_led.pin,
                    'brightness': self.config.hardware.ir_led.brightness
                }
            }
            
            self.hardware_controller = HardwareController(hardware_config)
            if not self.hardware_controller.initialize_hardware():
                self.logger.error("Hardware initialization failed")
                return False
            
            # 3. 検出器初期化
            detection_settings = DetectionSettings(
                model_path=self.model_manager.get_model_path(),
                confidence_threshold=self.config.detection.confidence_threshold,
                nms_threshold=self.config.detection.nms_threshold,
                max_detections=self.config.detection.max_detections,
                device=self.config.detection.device
            )
            
            self.detector = InsectDetector(
                settings=detection_settings,
                hardware_controller=self.hardware_controller
            )
            if not self.detector.initialize():
                self.logger.error("Detector initialization failed")
                return False
            
            # 4. データ処理モジュール初期化
            processing_settings = ProcessingSettings(
                min_confidence=self.config.detection.confidence_threshold,
                enable_duplicate_filter=True,
                save_filtered_data=True
            )
            
            self.detection_processor = DetectionProcessor(
                settings=processing_settings,
                output_dir=self.config.paths.log_dir
            )
            
            # 5. 活動量算出器初期化
            calculation_settings = CalculationSettings(
                movement_threshold=self.config.analysis.movement_threshold,
                time_window_minutes=self.config.analysis.time_window // 60,
                outlier_threshold=self.config.analysis.outlier_threshold
            )
            
            self.activity_calculator = ActivityCalculator(
                settings=calculation_settings,
                data_dir=self.config.paths.log_dir
            )
            
            # 6. データ処理器初期化
            data_processing_settings = DataProcessingSettings(
                outlier_detection_method="zscore",
                apply_smoothing=True,
                feature_scaling=True
            )
            
            self.data_processor = DataProcessor(data_processing_settings)
            
            # 7. 可視化器初期化
            viz_settings = VisualizationSettings(
                output_dir=self.config.paths.output_dir,
                output_format="png",
                interactive_mode=True
            )
            
            self.visualizer = Visualizer(viz_settings)
            
            # 8. システム制御器初期化
            self.system_controller = SystemController(
                config=self.config,
                hardware_controller=self.hardware_controller,
                detector=self.detector,
                detection_processor=self.detection_processor,
                activity_calculator=self.activity_calculator,
                visualizer=self.visualizer
            )
            
            # 9. スケジューラー初期化
            self.scheduler = SchedulerManager(
                detection_interval=self.config.system.detection_interval,
                analysis_time=self.config.system.daily_analysis_time
            )
            
            # スケジュール設定
            self.scheduler.schedule_detection(self._perform_detection_cycle)
            self.scheduler.schedule_daily_analysis(self._perform_daily_analysis)
            
            # システム状態更新
            self.status.start_time = datetime.now().isoformat()
            
            self.logger.info("System initialization completed successfully")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                exception=e,
                context=context,
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.CONFIGURATION
            )
            self.logger.error(f"System initialization failed: {e}")
            return False
    
    def run_main_loop(self) -> None:
        """メインループ実行"""
        try:
            self.logger.info("Starting main system loop...")
            self.status.is_running = True
            self.status.current_mode = "detecting"
            
            # 監視スレッド開始
            self.monitoring_thread = threading.Thread(
                target=self._system_monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            # スケジューラー開始
            if self.scheduler:
                self.scheduler.start()
            
            # メインループ
            while not self.shutdown_requested:
                try:
                    # システム状態更新
                    self._update_system_status()
                    
                    # 設定更新チェック
                    self._check_config_updates()
                    
                    # 定期ヘルスチェック
                    if self.system_controller:
                        health_status = self.system_controller.perform_health_check()
                        if not health_status.get('overall_healthy', True):
                            self.logger.warning(f"Health check issues: {health_status}")
                    
                    # 短時間待機
                    time.sleep(1.0)
                    
                except KeyboardInterrupt:
                    self.logger.info("Shutdown requested by user")
                    break
                except Exception as e:
                    context = ErrorContext(
                        module_name=__name__,
                        function_name="run_main_loop",
                        state_info={"error_count": self.status.error_count}
                    )
                    
                    self.error_handler.handle_error(
                        exception=e,
                        context=context,
                        severity=ErrorSeverity.ERROR,
                        category=ErrorCategory.PROCESSING
                    )
                    
                    self.status.error_count += 1
                    self.status.last_error = str(e)
                    
                    # エラー復旧試行
                    if self.status.error_count < 5:
                        time.sleep(5.0)  # 短時間待機後に継続
                    else:
                        self.logger.critical("Too many errors, shutting down")
                        break
            
            self.logger.info("Main loop ended")
            
        except Exception as e:
            self.logger.critical(f"Main loop critical error: {e}")
        finally:
            self.status.is_running = False
            self.status.current_mode = "shutdown"
    
    def _perform_detection_cycle(self) -> Dict[str, Any]:
        """
        検出サイクル実行
        
        Returns:
            Dict[str, Any]: 検出結果
        """
        try:
            self.status.current_mode = "detecting"
            self.logger.debug("Starting detection cycle")
            
            if not self.detector or not self.detection_processor:
                return {"error": "Detector not initialized"}
            
            # 検出実行
            detection_record = self.detector.detect_single_image(
                use_ir_led=True,
                save_result=True
            )
            
            if detection_record is None:
                return {"error": "Detection failed"}
            
            # 検出結果処理
            processed_record = self.detection_processor.process_detection_record(detection_record)
            
            # 統計更新
            self.status.total_detections += processed_record.detection_count
            self.status.total_images_processed += 1
            
            if processed_record.detection_count > 0:
                self.status.last_detection_time = processed_record.timestamp
            
            result = {
                "success": True,
                "timestamp": processed_record.timestamp,
                "detection_count": processed_record.detection_count,
                "processing_time_ms": processed_record.processing_time_ms
            }
            
            self.logger.debug(f"Detection cycle completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Detection cycle failed: {e}")
            self.status.error_count += 1
            return {"error": str(e)}
        finally:
            self.status.current_mode = "idle"
    
    def _perform_daily_analysis(self) -> None:
        """日次分析処理実行"""
        try:
            self.status.current_mode = "analyzing"
            self.logger.info("Starting daily analysis")
            
            if not self.activity_calculator or not self.visualizer:
                self.logger.error("Analysis modules not initialized")
                return
            
            # 昨日のデータを分析
            yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
            
            # データ読み込み
            detection_data = self.activity_calculator.load_detection_data(yesterday)
            if detection_data is None or len(detection_data) == 0:
                self.logger.warning(f"No data found for analysis: {yesterday}")
                return
            
            # データ前処理
            if self.data_processor:
                processed_data = self.data_processor.process_detection_data(detection_data)
            else:
                processed_data = detection_data
            
            # 活動量算出
            activity_metrics = self.activity_calculator.calculate_activity_metrics(processed_data)
            if activity_metrics is None:
                self.logger.error("Activity metrics calculation failed")
                return
            
            # 時間別サマリー生成
            hourly_summaries = self.activity_calculator.generate_hourly_summaries(processed_data)
            
            # 可視化レポート生成
            report_path = self.visualizer.export_visualization_report(
                activity_metrics,
                processed_data,
                hourly_summaries
            )
            
            if report_path:
                self.logger.info(f"Daily analysis report generated: {report_path}")
            else:
                self.logger.error("Report generation failed")
            
        except Exception as e:
            self.logger.error(f"Daily analysis failed: {e}")
            self.status.error_count += 1
        finally:
            self.status.current_mode = "idle"
    
    def _system_monitoring_loop(self) -> None:
        """システム監視ループ"""
        try:
            while self.status.is_running and not self.shutdown_requested:
                try:
                    # システムリソース監視
                    self._monitor_system_resources()
                    
                    # モジュール健全性チェック
                    self._check_module_health()
                    
                    # 長期間待機
                    time.sleep(30.0)
                    
                except Exception as e:
                    self.logger.error(f"System monitoring error: {e}")
                    time.sleep(10.0)
                    
        except Exception as e:
            self.logger.error(f"System monitoring loop failed: {e}")
    
    def _monitor_system_resources(self) -> None:
        """システムリソース監視"""
        try:
            # CPU温度チェック
            if self.hardware_controller:
                hw_status = self.hardware_controller.get_system_status()
                if hw_status.temperature > 80.0:  # 80℃以上で警告
                    self.logger.warning(f"High CPU temperature: {hw_status.temperature}°C")
                    
                    # 温度が高い場合は検出間隔を延長
                    if hw_status.temperature > 85.0 and self.scheduler:
                        self.scheduler.pause_detection(300)  # 5分間一時停止
                        self.logger.info("Detection paused due to high temperature")
            
        except Exception as e:
            self.logger.error(f"Resource monitoring failed: {e}")
    
    def _check_module_health(self) -> None:
        """モジュール健全性チェック"""
        try:
            # 各モジュールの状態確認
            modules_status = {}
            
            if self.hardware_controller:
                hw_status = self.hardware_controller.get_system_status()
                modules_status['hardware'] = hw_status.camera_initialized and hw_status.led_available
            
            if self.detector:
                det_status = self.detector.get_detailed_status()
                modules_status['detector'] = det_status['detector_status']['initialized']
            
            # 問題のあるモジュールがあれば警告
            failed_modules = [name for name, status in modules_status.items() if not status]
            if failed_modules:
                self.logger.warning(f"Module health issues: {failed_modules}")
            
        except Exception as e:
            self.logger.error(f"Module health check failed: {e}")
    
    def _update_system_status(self) -> None:
        """システム状態更新"""
        try:
            if self.status.start_time:
                start_datetime = datetime.fromisoformat(self.status.start_time)
                self.status.uptime_seconds = (datetime.now() - start_datetime).total_seconds()
                
        except Exception as e:
            self.logger.error(f"Status update failed: {e}")
    
    def _check_config_updates(self) -> None:
        """設定更新チェック"""
        try:
            # 設定ファイルの更新時刻チェック（簡易実装）
            config_file = Path(self.config_manager.config_path)
            if config_file.exists():
                current_mtime = config_file.stat().st_mtime
                if hasattr(self, '_last_config_mtime'):
                    if current_mtime > self._last_config_mtime:
                        self.logger.info("Configuration file updated, reloading...")
                        self._reload_configuration()
                self._last_config_mtime = current_mtime
            
        except Exception as e:
            self.logger.error(f"Config update check failed: {e}")
    
    def _reload_configuration(self) -> None:
        """設定再読み込み"""
        try:
            new_config = self.config_manager.load_config()
            
            # 検出器設定更新
            if self.detector:
                detection_settings = DetectionSettings(
                    model_path=self.model_manager.get_model_path(),
                    confidence_threshold=new_config.detection.confidence_threshold,
                    nms_threshold=new_config.detection.nms_threshold,
                    max_detections=new_config.detection.max_detections
                )
                self.detector.update_settings(detection_settings)
            
            # スケジューラー設定更新
            if self.scheduler:
                self.scheduler.update_detection_interval(new_config.system.detection_interval)
            
            self.config = new_config
            self.logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Configuration reload failed: {e}")
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラ"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_requested = True
    
    def run_single_detection(self) -> Dict[str, Any]:
        """
        単発検出実行
        
        Returns:
            Dict[str, Any]: 検出結果
        """
        if not self.status.is_running:
            if not self.initialize_system():
                return {"error": "System initialization failed"}
        
        return self._perform_detection_cycle()
    
    def run_analysis_for_date(self, date: str) -> bool:
        """
        指定日の分析実行
        
        Args:
            date: 分析対象日 (YYYY-MM-DD)
            
        Returns:
            bool: 分析成功可否
        """
        try:
            if not self.activity_calculator or not self.visualizer:
                if not self.initialize_system():
                    return False
            
            # データ読み込み
            detection_data = self.activity_calculator.load_detection_data(date)
            if detection_data is None:
                self.logger.error(f"No data found for {date}")
                return False
            
            # 活動量算出
            activity_metrics = self.activity_calculator.calculate_activity_metrics(detection_data)
            if activity_metrics is None:
                return False
            
            # レポート生成
            report_path = self.visualizer.export_visualization_report(
                activity_metrics,
                detection_data
            )
            
            return report_path is not None
            
        except Exception as e:
            self.logger.error(f"Analysis for {date} failed: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態取得"""
        status_dict = {
            "system_status": {
                "is_running": self.status.is_running,
                "start_time": self.status.start_time,
                "uptime_seconds": self.status.uptime_seconds,
                "current_mode": self.status.current_mode,
                "total_detections": self.status.total_detections,
                "total_images_processed": self.status.total_images_processed,
                "last_detection_time": self.status.last_detection_time,
                "error_count": self.status.error_count,
                "last_error": self.status.last_error
            }
        }
        
        # 各モジュールの状態
        if self.hardware_controller:
            status_dict["hardware"] = self.hardware_controller.get_detailed_status()
        
        if self.detector:
            status_dict["detector"] = self.detector.get_detailed_status()
        
        if self.detection_processor:
            status_dict["processor"] = self.detection_processor.get_processing_stats()
        
        return status_dict
    
    def shutdown_system(self) -> None:
        """システム終了処理"""
        try:
            self.logger.info("Starting system shutdown...")
            self.shutdown_requested = True
            self.status.current_mode = "shutdown"
            
            # スケジューラー停止
            if self.scheduler:
                self.scheduler.stop()
            
            # 各モジュールのクリーンアップ
            modules = [
                self.visualizer,
                self.data_processor,
                self.activity_calculator,
                self.detection_processor,
                self.detector,
                self.hardware_controller,
                self.model_manager
            ]
            
            for module in modules:
                if module and hasattr(module, 'cleanup'):
                    try:
                        module.cleanup()
                    except Exception as e:
                        self.logger.error(f"Module cleanup error: {e}")
            
            # 設定保存
            try:
                self.config_manager.save_config(self.config)
            except Exception as e:
                self.logger.error(f"Config save error: {e}")
            
            self.status.is_running = False
            self.logger.info("System shutdown completed")
            
        except Exception as e:
            self.logger.error(f"System shutdown error: {e}")


def setup_logging(log_level: str = "INFO") -> None:
    """ログ設定"""
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"system_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="昆虫自動観察システム")
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='./config/system_config.json',
        help='設定ファイルパス'
    )
    parser.add_argument(
        '--mode', '-m',
        choices=['continuous', 'single', 'analysis'],
        default='continuous',
        help='動作モード'
    )
    parser.add_argument(
        '--date', '-d',
        type=str,
        help='分析対象日付 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='ログレベル'
    )
    
    args = parser.parse_args()
    
    # ログ設定
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Insect Observer System")
        logger.info(f"Mode: {args.mode}, Config: {args.config}")
        
        # システム作成
        system = InsectObserverSystem(args.config)
        
        if args.mode == 'continuous':
            # 連続動作モード
            if system.initialize_system():
                system.run_main_loop()
            else:
                logger.error("System initialization failed")
                return 1
                
        elif args.mode == 'single':
            # 単発検出モード
            result = system.run_single_detection()
            logger.info(f"Single detection result: {result}")
            
        elif args.mode == 'analysis':
            # 分析モード
            if not args.date:
                args.date = (datetime.now() - timedelta(days=1)).date().isoformat()
            
            success = system.run_analysis_for_date(args.date)
            if success:
                logger.info(f"Analysis completed for {args.date}")
            else:
                logger.error(f"Analysis failed for {args.date}")
                return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.critical(f"System critical error: {e}")
        return 1
    finally:
        try:
            if 'system' in locals():
                system.shutdown_system()
        except:
            pass


if __name__ == "__main__":
    sys.exit(main())