"""
システム統合管理モジュール

各モジュール間の連携制御と統合オーケストレーションを行う。
- モジュール間の依存関係管理
- 処理パイプライン制御
- システム状態管理
- ヘルスチェック・診断
- パフォーマンス監視
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import json
from pathlib import Path

# プロジェクト内モジュール
from config.config_manager import SystemConfiguration
from hardware_controller import HardwareController
from insect_detector import InsectDetector
from detection_processor import DetectionProcessor
from activity_calculator import ActivityCalculator
from visualization import Visualizer
from models.detection_models import DetectionRecord
from models.activity_models import ActivityMetrics
from error_handler import ErrorHandler, ErrorSeverity, ErrorCategory, ErrorContext
from monitoring import SystemMonitor


@dataclass
class SystemHealthStatus:
    """システム健全性状態"""
    overall_healthy: bool = True
    hardware_status: str = "unknown"
    detector_status: str = "unknown"
    processor_status: str = "unknown"
    calculator_status: str = "unknown"
    visualizer_status: str = "unknown"
    error_messages: List[str] = None
    warnings: List[str] = None
    last_check_time: str = ""
    uptime_seconds: float = 0.0


@dataclass
class PerformanceMetrics:
    """パフォーマンス指標"""
    avg_detection_time_ms: float = 0.0
    avg_processing_time_ms: float = 0.0
    detection_success_rate: float = 0.0
    system_throughput: float = 0.0  # detections per hour
    memory_usage_mb: float = 0.0
    cpu_temperature: float = 0.0
    total_detections: int = 0
    total_errors: int = 0


class SystemController:
    """
    システム統合管理クラス
    
    Features:
    - モジュール間オーケストレーション
    - 統合ワークフロー制御
    - システム健全性監視
    - パフォーマンス分析
    - エラー統合管理
    - 自動復旧機能
    """
    
    def __init__(self,
                 config: SystemConfiguration,
                 hardware_controller: HardwareController,
                 detector: InsectDetector,
                 detection_processor: DetectionProcessor,
                 activity_calculator: ActivityCalculator,
                 visualizer: Visualizer):
        """
        システム制御器初期化
        
        Args:
            config: システム設定
            hardware_controller: ハードウェア制御器
            detector: 検出器
            detection_processor: 検出処理器
            activity_calculator: 活動量算出器
            visualizer: 可視化器
        """
        self.logger = logging.getLogger(__name__ + '.SystemController')
        
        # 設定
        self.config = config
        
        # 各モジュール
        self.hardware_controller = hardware_controller
        self.detector = detector
        self.detection_processor = detection_processor
        self.activity_calculator = activity_calculator
        self.visualizer = visualizer
        
        # エラーハンドリング・監視
        error_config = config.system.get('error_handling', {})
        self.error_handler = ErrorHandler(error_config)
        
        # 状態管理
        self.health_status = SystemHealthStatus()
        self.performance_metrics = PerformanceMetrics()
        self.start_time = datetime.now()
        
        # 履歴データ
        self.detection_history: List[DetectionRecord] = []
        self.performance_history: List[PerformanceMetrics] = []
        
        # 同期制御
        self.processing_lock = threading.Lock()
        
        self.logger.info("System controller initialized")
    
    def execute_detection_workflow(self, 
                                 use_ir_led: bool = True,
                                 save_results: bool = True) -> Optional[DetectionRecord]:
        """
        統合検出ワークフロー実行
        
        Args:
            use_ir_led: IR LED使用可否
            save_results: 結果保存可否
            
        Returns:
            Optional[DetectionRecord]: 処理済み検出記録
        """
        with self.processing_lock:
            context = ErrorContext(
                module_name=__name__,
                function_name="execute_detection_workflow",
                input_data={"use_ir_led": use_ir_led, "save_results": save_results}
            )
            
            try:
                workflow_start = time.time()
                self.logger.debug("Starting integrated detection workflow")
                
                # Phase 1: ハードウェア前処理
                if not self._prepare_hardware():
                    return None
                
                # Phase 2: 検出実行
                detection_record = self.detector.detect_single_image(
                    use_ir_led=use_ir_led,
                    save_result=save_results
                )
                
                if detection_record is None:
                    self.logger.error("Detection failed in workflow")
                    self.performance_metrics.total_errors += 1
                    return None
                
                # Phase 3: 検出結果処理
                processed_record = self.detection_processor.process_detection_record(
                    detection_record
                )
                
                # Phase 4: 履歴更新
                self.detection_history.append(processed_record)
                if len(self.detection_history) > 1000:  # 履歴サイズ制限
                    self.detection_history = self.detection_history[-1000:]
                
                # Phase 5: パフォーマンス指標更新
                workflow_time = (time.time() - workflow_start) * 1000
                self._update_performance_metrics(processed_record, workflow_time)
                
                # Phase 6: ハードウェア後処理
                self._cleanup_hardware()
                
                self.logger.debug(f"Detection workflow completed in {workflow_time:.1f}ms")
                return processed_record
                
            except Exception as e:
                self.error_handler.handle_error(
                    exception=e,
                    context=context,
                    severity=ErrorSeverity.ERROR,
                    category=ErrorCategory.DETECTION
                )
                self.performance_metrics.total_errors += 1
                return None
    
    def execute_analysis_workflow(self, 
                                date: str,
                                generate_report: bool = True) -> Optional[ActivityMetrics]:
        """
        統合分析ワークフロー実行
        
        Args:
            date: 分析対象日 (YYYY-MM-DD)
            generate_report: レポート生成可否
            
        Returns:
            Optional[ActivityMetrics]: 活動量指標
        """
        try:
            self.logger.info(f"Starting analysis workflow for {date}")
            
            # Phase 1: データ読み込み・検証
            detection_data = self.activity_calculator.load_detection_data(date)
            if detection_data is None or len(detection_data) == 0:
                self.logger.warning(f"No valid data for analysis: {date}")
                return None
            
            # Phase 2: 活動量算出
            activity_metrics = self.activity_calculator.calculate_activity_metrics(detection_data)
            if activity_metrics is None:
                self.logger.error("Activity metrics calculation failed")
                return None
            
            # Phase 3: レポート生成
            if generate_report:
                hourly_summaries = self.activity_calculator.generate_hourly_summaries(detection_data)
                
                report_path = self.visualizer.export_visualization_report(
                    activity_metrics,
                    detection_data,
                    hourly_summaries
                )
                
                if report_path:
                    self.logger.info(f"Analysis report generated: {report_path}")
                else:
                    self.logger.warning("Report generation failed")
            
            self.logger.info(f"Analysis workflow completed for {date}")
            return activity_metrics
            
        except Exception as e:
            self.logger.error(f"Analysis workflow failed for {date}: {e}")
            return None
    
    def _prepare_hardware(self) -> bool:
        """ハードウェア前処理"""
        try:
            # ハードウェア状態確認
            hw_status = self.hardware_controller.get_system_status()
            if not hw_status.camera_initialized:
                self.logger.error("Camera not ready for detection")
                return False
            
            # 温度チェック
            if hw_status.temperature > 85.0:
                self.logger.warning(f"High temperature detected: {hw_status.temperature}°C")
                # 高温時は少し待機
                time.sleep(2.0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Hardware preparation failed: {e}")
            return False
    
    def _cleanup_hardware(self) -> None:
        """ハードウェア後処理"""
        try:
            # LED確実消灯
            self.hardware_controller.control_ir_led(0.0)
            
        except Exception as e:
            self.logger.error(f"Hardware cleanup failed: {e}")
    
    def _update_performance_metrics(self, 
                                  record: DetectionRecord, 
                                  workflow_time: float) -> None:
        """パフォーマンス指標更新"""
        try:
            # 基本指標更新
            self.performance_metrics.total_detections += 1
            
            # 平均検出時間更新
            current_count = self.performance_metrics.total_detections
            current_avg = self.performance_metrics.avg_detection_time_ms
            new_avg = ((current_avg * (current_count - 1)) + record.processing_time_ms) / current_count
            self.performance_metrics.avg_detection_time_ms = new_avg
            
            # 平均処理時間更新（ワークフロー全体）
            current_avg_workflow = self.performance_metrics.avg_processing_time_ms
            new_avg_workflow = ((current_avg_workflow * (current_count - 1)) + workflow_time) / current_count
            self.performance_metrics.avg_processing_time_ms = new_avg_workflow
            
            # 成功率更新
            success_count = sum(1 for r in self.detection_history[-100:] if r.detection_count >= 0)
            total_recent = min(len(self.detection_history), 100)
            if total_recent > 0:
                self.performance_metrics.detection_success_rate = success_count / total_recent
            
            # スループット計算（1時間あたりの検出数）
            uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600.0
            if uptime_hours > 0:
                self.performance_metrics.system_throughput = self.performance_metrics.total_detections / uptime_hours
            
            # ハードウェア情報更新
            hw_status = self.hardware_controller.get_system_status()
            self.performance_metrics.cpu_temperature = hw_status.temperature
            
        except Exception as e:
            self.logger.error(f"Performance metrics update failed: {e}")
    
    def perform_health_check(self) -> Dict[str, Any]:
        """
        システム健全性チェック実行
        
        Returns:
            Dict[str, Any]: ヘルスチェック結果
        """
        try:
            self.logger.debug("Performing system health check")
            
            # 初期化
            self.health_status.error_messages = []
            self.health_status.warnings = []
            
            # 各モジュールのチェック
            hardware_ok = self._check_hardware_health()
            detector_ok = self._check_detector_health()
            processor_ok = self._check_processor_health()
            calculator_ok = self._check_calculator_health()
            visualizer_ok = self._check_visualizer_health()
            
            # 総合判定
            self.health_status.overall_healthy = all([
                hardware_ok, detector_ok, processor_ok, calculator_ok, visualizer_ok
            ])
            
            # システム稼働時間更新
            self.health_status.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            self.health_status.last_check_time = datetime.now().isoformat()
            
            # 結果辞書作成
            result = {
                "overall_healthy": self.health_status.overall_healthy,
                "modules": {
                    "hardware": self.health_status.hardware_status,
                    "detector": self.health_status.detector_status,
                    "processor": self.health_status.processor_status,
                    "calculator": self.health_status.calculator_status,
                    "visualizer": self.health_status.visualizer_status
                },
                "errors": self.health_status.error_messages,
                "warnings": self.health_status.warnings,
                "uptime_seconds": self.health_status.uptime_seconds,
                "last_check": self.health_status.last_check_time
            }
            
            if not self.health_status.overall_healthy:
                self.logger.warning(f"Health check issues detected: {self.health_status.error_messages}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "overall_healthy": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def _check_hardware_health(self) -> bool:
        """ハードウェア健全性チェック"""
        try:
            hw_status = self.hardware_controller.get_system_status()
            
            if not hw_status.camera_initialized:
                self.health_status.hardware_status = "camera_error"
                self.health_status.error_messages.append("Camera not initialized")
                return False
            
            if not hw_status.led_available:
                self.health_status.hardware_status = "led_warning"
                self.health_status.warnings.append("LED not available")
            
            if hw_status.temperature > 80.0:
                self.health_status.warnings.append(f"High temperature: {hw_status.temperature}°C")
            
            self.health_status.hardware_status = "healthy"
            return True
            
        except Exception as e:
            self.health_status.hardware_status = "check_error"
            self.health_status.error_messages.append(f"Hardware check failed: {e}")
            return False
    
    def _check_detector_health(self) -> bool:
        """検出器健全性チェック"""
        try:
            detector_status = self.detector.get_detailed_status()
            
            if not detector_status['detector_status']['initialized']:
                self.health_status.detector_status = "not_initialized"
                self.health_status.error_messages.append("Detector not initialized")
                return False
            
            if not detector_status['detector_status']['model_loaded']:
                self.health_status.detector_status = "model_error"
                self.health_status.error_messages.append("Detection model not loaded")
                return False
            
            # エラー率チェック
            stats = detector_status['statistics']
            if stats['error_count'] > 0:
                error_rate = stats['error_count'] / max(1, stats['total_images_processed'])
                if error_rate > 0.1:  # 10%以上のエラー率
                    self.health_status.warnings.append(f"High detection error rate: {error_rate:.1%}")
            
            self.health_status.detector_status = "healthy"
            return True
            
        except Exception as e:
            self.health_status.detector_status = "check_error"
            self.health_status.error_messages.append(f"Detector check failed: {e}")
            return False
    
    def _check_processor_health(self) -> bool:
        """処理器健全性チェック"""
        try:
            processor_stats = self.detection_processor.get_processing_stats()
            
            # 処理エラー率チェック
            if processor_stats.processing_errors > 0:
                error_rate = processor_stats.processing_errors / max(1, processor_stats.total_processed)
                if error_rate > 0.05:  # 5%以上のエラー率
                    self.health_status.warnings.append(f"High processing error rate: {error_rate:.1%}")
            
            self.health_status.processor_status = "healthy"
            return True
            
        except Exception as e:
            self.health_status.processor_status = "check_error"
            self.health_status.error_messages.append(f"Processor check failed: {e}")
            return False
    
    def _check_calculator_health(self) -> bool:
        """算出器健全性チェック"""
        try:
            calc_stats = self.activity_calculator.get_calculation_stats()
            
            # 計算エラー率チェック
            if calc_stats.calculation_errors > 0:
                error_rate = calc_stats.calculation_errors / max(1, calc_stats.total_records_processed)
                if error_rate > 0.1:  # 10%以上のエラー率
                    self.health_status.warnings.append(f"High calculation error rate: {error_rate:.1%}")
            
            self.health_status.calculator_status = "healthy"
            return True
            
        except Exception as e:
            self.health_status.calculator_status = "check_error"
            self.health_status.error_messages.append(f"Calculator check failed: {e}")
            return False
    
    def _check_visualizer_health(self) -> bool:
        """可視化器健全性チェック"""
        try:
            # 可視化器の基本機能確認
            if not (self.visualizer.matplotlib_available or self.visualizer.plotly_available):
                self.health_status.visualizer_status = "libraries_missing"
                self.health_status.error_messages.append("Visualization libraries not available")
                return False
            
            # 出力ディレクトリ確認
            if not self.visualizer.output_dir.exists():
                self.health_status.warnings.append("Visualization output directory not found")
            
            self.health_status.visualizer_status = "healthy"
            return True
            
        except Exception as e:
            self.health_status.visualizer_status = "check_error"
            self.health_status.error_messages.append(f"Visualizer check failed: {e}")
            return False
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        パフォーマンスレポート取得
        
        Returns:
            Dict[str, Any]: パフォーマンス情報
        """
        try:
            # 現在の指標
            current_metrics = {
                "avg_detection_time_ms": self.performance_metrics.avg_detection_time_ms,
                "avg_processing_time_ms": self.performance_metrics.avg_processing_time_ms,
                "detection_success_rate": self.performance_metrics.detection_success_rate,
                "system_throughput": self.performance_metrics.system_throughput,
                "cpu_temperature": self.performance_metrics.cpu_temperature,
                "total_detections": self.performance_metrics.total_detections,
                "total_errors": self.performance_metrics.total_errors
            }
            
            # 最近の検出統計
            recent_detections = self.detection_history[-100:] if self.detection_history else []
            recent_stats = {}
            
            if recent_detections:
                detection_counts = [r.detection_count for r in recent_detections]
                processing_times = [r.processing_time_ms for r in recent_detections]
                
                recent_stats = {
                    "recent_avg_detection_count": sum(detection_counts) / len(detection_counts),
                    "recent_max_processing_time": max(processing_times),
                    "recent_min_processing_time": min(processing_times),
                    "recent_detections_with_results": sum(1 for c in detection_counts if c > 0),
                    "recent_sample_size": len(recent_detections)
                }
            
            # システム稼働情報
            uptime = (datetime.now() - self.start_time).total_seconds()
            system_info = {
                "uptime_seconds": uptime,
                "uptime_hours": uptime / 3600.0,
                "start_time": self.start_time.isoformat(),
                "current_time": datetime.now().isoformat()
            }
            
            return {
                "current_metrics": current_metrics,
                "recent_statistics": recent_stats,
                "system_info": system_info,
                "report_generated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Performance report generation failed: {e}")
            return {"error": str(e)}
    
    def perform_system_maintenance(self) -> Dict[str, Any]:
        """
        システムメンテナンス実行
        
        Returns:
            Dict[str, Any]: メンテナンス結果
        """
        try:
            self.logger.info("Starting system maintenance")
            maintenance_results = {}
            
            # 1. キャッシュクリア
            try:
                self.activity_calculator.clear_cache()
                maintenance_results["cache_clear"] = "success"
            except Exception as e:
                maintenance_results["cache_clear"] = f"failed: {e}"
            
            # 2. 古いログファイルクリーンアップ
            try:
                log_dir = Path(self.config.paths.log_dir)
                if log_dir.exists():
                    cutoff_date = datetime.now() - timedelta(days=self.config.system.data_retention_days)
                    
                    cleaned_files = 0
                    for log_file in log_dir.glob("*.csv"):
                        if log_file.stat().st_mtime < cutoff_date.timestamp():
                            log_file.unlink()
                            cleaned_files += 1
                    
                    maintenance_results["log_cleanup"] = f"removed {cleaned_files} old files"
                else:
                    maintenance_results["log_cleanup"] = "log directory not found"
            except Exception as e:
                maintenance_results["log_cleanup"] = f"failed: {e}"
            
            # 3. パフォーマンス履歴圧縮
            try:
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-500:]
                    maintenance_results["history_compression"] = "compressed performance history"
                else:
                    maintenance_results["history_compression"] = "no compression needed"
            except Exception as e:
                maintenance_results["history_compression"] = f"failed: {e}"
            
            # 4. システム健全性チェック
            try:
                health_result = self.perform_health_check()
                maintenance_results["health_check"] = "completed"
                maintenance_results["health_status"] = health_result["overall_healthy"]
            except Exception as e:
                maintenance_results["health_check"] = f"failed: {e}"
            
            maintenance_results["maintenance_completed"] = datetime.now().isoformat()
            self.logger.info("System maintenance completed")
            
            return maintenance_results
            
        except Exception as e:
            self.logger.error(f"System maintenance failed: {e}")
            return {"error": str(e), "maintenance_completed": datetime.now().isoformat()}
    
    def get_system_diagnostics(self) -> Dict[str, Any]:
        """
        システム診断情報取得
        
        Returns:
            Dict[str, Any]: 診断情報
        """
        try:
            diagnostics = {}
            
            # 基本システム情報
            diagnostics["system_info"] = {
                "controller_start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "total_detections_processed": len(self.detection_history),
                "config_path": str(self.config_manager.config_path) if hasattr(self, 'config_manager') else "unknown"
            }
            
            # 各モジュール状態
            diagnostics["modules"] = {}
            
            try:
                diagnostics["modules"]["hardware"] = self.hardware_controller.get_detailed_status()
            except Exception as e:
                diagnostics["modules"]["hardware"] = {"error": str(e)}
            
            try:
                diagnostics["modules"]["detector"] = self.detector.get_detailed_status()
            except Exception as e:
                diagnostics["modules"]["detector"] = {"error": str(e)}
            
            # パフォーマンス指標
            diagnostics["performance"] = self.get_performance_report()
            
            # 健全性状態
            diagnostics["health"] = self.perform_health_check()
            
            diagnostics["diagnostics_generated"] = datetime.now().isoformat()
            
            return diagnostics
            
        except Exception as e:
            self.logger.error(f"System diagnostics failed: {e}")
            return {"error": str(e), "diagnostics_generated": datetime.now().isoformat()}
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            # 履歴データクリア
            self.detection_history.clear()
            self.performance_history.clear()
            
            self.logger.info("System controller cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"System controller cleanup failed: {e}")


# 使用例・テスト関数
def test_system_controller():
    """システム制御器のテスト"""
    import logging
    from config.config_manager import ConfigManager
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("System controller test - placeholder")
        # 実際のテストは統合テスト時に実施
        
    except Exception as e:
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    test_system_controller()