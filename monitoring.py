"""
システム監視統合管理モジュール

システム全体の健全性監視とパフォーマンス追跡を行う。
- リアルタイムシステム監視
- パフォーマンスメトリクス収集
- リソース使用量監視
- 健全性チェックとアラート
- 監視ダッシュボード機能
"""

import logging
import time
import psutil
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
from collections import deque, defaultdict
import subprocess
import platform


class ComponentStatus(Enum):
    """コンポーネント状態"""
    HEALTHY = "healthy"          # 正常
    WARNING = "warning"          # 警告
    ERROR = "error"             # エラー
    CRITICAL = "critical"       # 致命的
    UNKNOWN = "unknown"         # 不明
    OFFLINE = "offline"         # オフライン


class MetricType(Enum):
    """メトリクス種別"""
    COUNTER = "counter"         # カウンター（累積値）
    GAUGE = "gauge"            # ゲージ（現在値）
    HISTOGRAM = "histogram"     # ヒストグラム（分布）
    TIMER = "timer"            # タイマー（実行時間）


@dataclass
class SystemResources:
    """システムリソース情報"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_available_mb: float = 0.0
    disk_usage_percent: float = 0.0
    disk_free_gb: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    load_average: List[float] = field(default_factory=list)
    temperature_celsius: Optional[float] = None
    uptime_seconds: float = 0.0


@dataclass
class ComponentHealth:
    """コンポーネント健全性情報"""
    name: str
    status: ComponentStatus
    last_check_time: str
    response_time_ms: float = 0.0
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    restart_count: int = 0
    last_restart_time: Optional[str] = None


@dataclass
class PerformanceMetric:
    """パフォーマンスメトリクス"""
    name: str
    type: MetricType
    value: float
    timestamp: str
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""


@dataclass
class MonitoringAlert:
    """監視アラート"""
    alert_id: str
    component: str
    severity: str
    message: str
    timestamp: str
    resolved: bool = False
    resolution_time: Optional[str] = None
    acknowledgment: bool = False


class HealthChecker:
    """健全性チェック基底クラス"""
    def __init__(self, name: str, timeout_seconds: float = 5.0):
        self.name = name
        self.timeout_seconds = timeout_seconds
    
    def check(self) -> ComponentHealth:
        """健全性チェックを実行"""
        raise NotImplementedError


class ProcessHealthChecker(HealthChecker):
    """プロセス健全性チェック"""
    def __init__(self, name: str, process_name: str):
        super().__init__(name)
        self.process_name = process_name
    
    def check(self) -> ComponentHealth:
        """プロセスの存在と状態をチェック"""
        start_time = time.time()
        try:
            processes = [p for p in psutil.process_iter(['pid', 'name', 'status']) 
                        if self.process_name in p.info['name']]
            
            if not processes:
                return ComponentHealth(
                    name=self.name,
                    status=ComponentStatus.CRITICAL,
                    last_check_time=datetime.now().isoformat(),
                    response_time_ms=(time.time() - start_time) * 1000,
                    error_message=f"プロセス '{self.process_name}' が見つかりません"
                )
            
            return ComponentHealth(
                name=self.name,
                status=ComponentStatus.HEALTHY,
                last_check_time=datetime.now().isoformat(),
                response_time_ms=(time.time() - start_time) * 1000,
                metrics={
                    "process_count": len(processes),
                    "pids": [p.info['pid'] for p in processes]
                }
            )
        
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=ComponentStatus.ERROR,
                last_check_time=datetime.now().isoformat(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )


class FileSystemHealthChecker(HealthChecker):
    """ファイルシステム健全性チェック"""
    def __init__(self, name: str, path: str, min_free_gb: float = 1.0):
        super().__init__(name)
        self.path = Path(path)
        self.min_free_gb = min_free_gb
    
    def check(self) -> ComponentHealth:
        """ディスク容量と書き込み権限をチェック"""
        start_time = time.time()
        try:
            # ディスク使用量チェック
            usage = psutil.disk_usage(str(self.path))
            free_gb = usage.free / (1024**3)
            usage_percent = (usage.used / usage.total) * 100
            
            status = ComponentStatus.HEALTHY
            error_message = None
            
            if free_gb < self.min_free_gb:
                status = ComponentStatus.WARNING
                error_message = f"空き容量不足: {free_gb:.1f}GB < {self.min_free_gb}GB"
            
            if usage_percent > 95:
                status = ComponentStatus.CRITICAL
                error_message = f"ディスク使用率が危険レベル: {usage_percent:.1f}%"
            
            # 書き込み権限テスト
            test_file = self.path / ".health_check_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception:
                status = ComponentStatus.ERROR
                error_message = "書き込み権限がありません"
            
            return ComponentHealth(
                name=self.name,
                status=status,
                last_check_time=datetime.now().isoformat(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=error_message,
                metrics={
                    "free_gb": free_gb,
                    "usage_percent": usage_percent,
                    "total_gb": usage.total / (1024**3)
                }
            )
        
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=ComponentStatus.ERROR,
                last_check_time=datetime.now().isoformat(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )


class HardwareHealthChecker(HealthChecker):
    """ハードウェア健全性チェック"""
    def check(self) -> ComponentHealth:
        """CPU温度とハードウェア状態をチェック"""
        start_time = time.time()
        try:
            metrics = {}
            status = ComponentStatus.HEALTHY
            error_message = None
            
            # CPU温度取得（Raspberry Pi対応）
            try:
                if platform.system() == "Linux":
                    temp_result = subprocess.run(
                        ["cat", "/sys/class/thermal/thermal_zone0/temp"],
                        capture_output=True, text=True, timeout=2
                    )
                    if temp_result.returncode == 0:
                        temp_celsius = int(temp_result.stdout.strip()) / 1000.0
                        metrics["cpu_temperature"] = temp_celsius
                        
                        if temp_celsius > 80:
                            status = ComponentStatus.WARNING
                            error_message = f"CPU温度が高温: {temp_celsius}°C"
                        elif temp_celsius > 85:
                            status = ComponentStatus.CRITICAL
                            error_message = f"CPU温度が危険レベル: {temp_celsius}°C"
            except Exception:
                pass  # 温度取得失敗は致命的ではない
            
            # GPU メモリ使用量（Raspberry Pi GPU対応）
            try:
                gpu_mem_result = subprocess.run(
                    ["vcgencmd", "get_mem", "gpu"],
                    capture_output=True, text=True, timeout=2
                )
                if gpu_mem_result.returncode == 0:
                    gpu_mem = gpu_mem_result.stdout.strip()
                    metrics["gpu_memory"] = gpu_mem
            except Exception:
                pass  # GPU情報取得失敗は致命的ではない
            
            return ComponentHealth(
                name=self.name,
                status=status,
                last_check_time=datetime.now().isoformat(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=error_message,
                metrics=metrics
            )
        
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=ComponentStatus.ERROR,
                last_check_time=datetime.now().isoformat(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )


class SystemMonitor:
    """システム監視統合管理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 監視対象コンポーネント
        self.health_checkers: Dict[str, HealthChecker] = {}
        self.component_status: Dict[str, ComponentHealth] = {}
        
        # メトリクス収集
        self.metrics_history: deque = deque(maxlen=10000)  # 最新10000件を保持
        self.current_metrics: Dict[str, PerformanceMetric] = {}
        
        # アラート管理
        self.active_alerts: Dict[str, MonitoringAlert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        
        # 監視設定
        self.monitoring_interval = config.get("monitoring_interval", 30.0)  # 30秒間隔
        self.metrics_interval = config.get("metrics_interval", 10.0)      # 10秒間隔
        
        # 監視スレッド
        self.monitoring_active = False
        self.health_check_thread: Optional[threading.Thread] = None
        self.metrics_thread: Optional[threading.Thread] = None
        
        # ロック
        self.lock = threading.Lock()
        
        # システムリソース監視
        self.start_time = time.time()
        
        # ログディレクトリ
        self.log_path = Path("logs/monitoring")
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self._setup_default_checkers()
    
    def _setup_default_checkers(self):
        """デフォルトの健全性チェッカーを設定"""
        # ファイルシステムチェック
        self.register_health_checker(
            FileSystemHealthChecker("filesystem_logs", "logs", min_free_gb=0.5)
        )
        self.register_health_checker(
            FileSystemHealthChecker("filesystem_temp", "/tmp", min_free_gb=0.1)
        )
        
        # ハードウェアチェック
        self.register_health_checker(
            HardwareHealthChecker("hardware")
        )
    
    def register_health_checker(self, checker: HealthChecker):
        """健全性チェッカーを登録"""
        self.health_checkers[checker.name] = checker
        self.logger.info(f"健全性チェッカーを登録: {checker.name}")
    
    def start_monitoring(self):
        """監視を開始"""
        if self.monitoring_active:
            self.logger.warning("監視は既に開始されています")
            return
        
        self.monitoring_active = True
        
        # 健全性チェックスレッド
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_check_thread.start()
        
        # メトリクス収集スレッド
        self.metrics_thread = threading.Thread(
            target=self._metrics_collection_loop,
            daemon=True
        )
        self.metrics_thread.start()
        
        self.logger.info("システム監視を開始しました")
    
    def stop_monitoring(self):
        """監視を停止"""
        self.monitoring_active = False
        
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5.0)
        if self.metrics_thread:
            self.metrics_thread.join(timeout=5.0)
        
        self.logger.info("システム監視を停止しました")
    
    def _health_check_loop(self):
        """健全性チェックループ"""
        while self.monitoring_active:
            try:
                self._perform_health_checks()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"健全性チェック中にエラー: {e}")
                time.sleep(5.0)  # エラー時は短い間隔で再試行
    
    def _metrics_collection_loop(self):
        """メトリクス収集ループ"""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                time.sleep(self.metrics_interval)
            except Exception as e:
                self.logger.error(f"メトリクス収集中にエラー: {e}")
                time.sleep(5.0)  # エラー時は短い間隔で再試行
    
    def _perform_health_checks(self):
        """すべての健全性チェックを実行"""
        with self.lock:
            for name, checker in self.health_checkers.items():
                try:
                    health = checker.check()
                    self.component_status[name] = health
                    
                    # アラート生成
                    if health.status in [ComponentStatus.WARNING, ComponentStatus.ERROR, ComponentStatus.CRITICAL]:
                        self._generate_alert(health)
                    else:
                        # 復旧したアラートを解決
                        self._resolve_alerts(name)
                    
                except Exception as e:
                    self.logger.error(f"健全性チェック失敗 ({name}): {e}")
                    # エラー時のフォールバック
                    self.component_status[name] = ComponentHealth(
                        name=name,
                        status=ComponentStatus.ERROR,
                        last_check_time=datetime.now().isoformat(),
                        error_message=f"健全性チェック実行エラー: {e}"
                    )
    
    def _collect_system_metrics(self):
        """システムメトリクスを収集"""
        timestamp = datetime.now().isoformat()
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self._record_metric("system.cpu_percent", MetricType.GAUGE, cpu_percent, timestamp, unit="%")
        
        # メモリ使用量
        memory = psutil.virtual_memory()
        self._record_metric("system.memory_percent", MetricType.GAUGE, memory.percent, timestamp, unit="%")
        self._record_metric("system.memory_available_mb", MetricType.GAUGE, memory.available / (1024**2), timestamp, unit="MB")
        
        # ディスク使用量
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self._record_metric("system.disk_percent", MetricType.GAUGE, disk_percent, timestamp, unit="%")
        self._record_metric("system.disk_free_gb", MetricType.GAUGE, disk.free / (1024**3), timestamp, unit="GB")
        
        # ネットワーク統計
        network = psutil.net_io_counters()
        self._record_metric("system.network_bytes_sent", MetricType.COUNTER, network.bytes_sent, timestamp, unit="bytes")
        self._record_metric("system.network_bytes_recv", MetricType.COUNTER, network.bytes_recv, timestamp, unit="bytes")
        
        # システムアップタイム
        uptime = time.time() - self.start_time
        self._record_metric("system.uptime_seconds", MetricType.GAUGE, uptime, timestamp, unit="seconds")
        
        # ロードアベレージ（Linux専用）
        try:
            load_avg = psutil.getloadavg()
            self._record_metric("system.load_1min", MetricType.GAUGE, load_avg[0], timestamp)
            self._record_metric("system.load_5min", MetricType.GAUGE, load_avg[1], timestamp)
            self._record_metric("system.load_15min", MetricType.GAUGE, load_avg[2], timestamp)
        except AttributeError:
            pass  # Windows等ではgetloadavgが利用できない
    
    def _record_metric(self, name: str, metric_type: MetricType, value: float, 
                      timestamp: str, tags: Dict[str, str] = None, unit: str = ""):
        """メトリクスを記録"""
        metric = PerformanceMetric(
            name=name,
            type=metric_type,
            value=value,
            timestamp=timestamp,
            tags=tags or {},
            unit=unit
        )
        
        self.current_metrics[name] = metric
        self.metrics_history.append(metric)
    
    def _generate_alert(self, health: ComponentHealth):
        """アラートを生成"""
        alert_key = health.name
        
        # 既存のアクティブアラートがあるかチェック
        if alert_key in self.active_alerts and not self.active_alerts[alert_key].resolved:
            return  # 既にアラート済み
        
        severity_map = {
            ComponentStatus.WARNING: "WARNING",
            ComponentStatus.ERROR: "ERROR",
            ComponentStatus.CRITICAL: "CRITICAL"
        }
        
        alert = MonitoringAlert(
            alert_id=f"ALERT-{health.name}-{int(time.time())}",
            component=health.name,
            severity=severity_map.get(health.status, "UNKNOWN"),
            message=health.error_message or f"コンポーネント状態異常: {health.status.value}",
            timestamp=datetime.now().isoformat()
        )
        
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        self.logger.warning(f"アラート生成: {alert.alert_id} - {alert.message}")
    
    def _resolve_alerts(self, component_name: str):
        """コンポーネントのアラートを解決"""
        if component_name in self.active_alerts:
            alert = self.active_alerts[component_name]
            if not alert.resolved:
                alert.resolved = True
                alert.resolution_time = datetime.now().isoformat()
                self.logger.info(f"アラート解決: {alert.alert_id}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """システム全体の健全性情報を取得"""
        with self.lock:
            overall_status = ComponentStatus.HEALTHY
            
            # 最も深刻な状態を全体状態とする
            status_priority = {
                ComponentStatus.HEALTHY: 0,
                ComponentStatus.WARNING: 1,
                ComponentStatus.ERROR: 2,
                ComponentStatus.CRITICAL: 3,
                ComponentStatus.UNKNOWN: 2,
                ComponentStatus.OFFLINE: 3
            }
            
            for health in self.component_status.values():
                if status_priority[health.status] > status_priority[overall_status]:
                    overall_status = health.status
            
            return {
                "overall_status": overall_status.value,
                "components": {name: asdict(health) for name, health in self.component_status.items()},
                "active_alerts_count": len([a for a in self.active_alerts.values() if not a.resolved]),
                "last_check_time": datetime.now().isoformat()
            }
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """現在のメトリクス情報を取得"""
        with self.lock:
            return {name: asdict(metric) for name, metric in self.current_metrics.items()}
    
    def get_metric_history(self, metric_name: str, hours: int = 1) -> List[PerformanceMetric]:
        """指定メトリクスの履歴を取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metric for metric in self.metrics_history
            if metric.name == metric_name and 
            datetime.fromisoformat(metric.timestamp) > cutoff_time
        ]
    
    def get_active_alerts(self) -> List[MonitoringAlert]:
        """アクティブなアラートを取得"""
        with self.lock:
            return [alert for alert in self.active_alerts.values() if not alert.resolved]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """アラートを確認済みにする"""
        with self.lock:
            for alert in self.active_alerts.values():
                if alert.alert_id == alert_id:
                    alert.acknowledgment = True
                    self.logger.info(f"アラート確認済み: {alert_id}")
                    return True
            return False
    
    def export_monitoring_report(self, output_path: Path) -> Path:
        """監視レポートをエクスポート"""
        report = {
            "report_time": datetime.now().isoformat(),
            "system_health": self.get_system_health(),
            "current_metrics": self.get_current_metrics(),
            "active_alerts": [asdict(alert) for alert in self.get_active_alerts()],
            "alert_history": [asdict(alert) for alert in list(self.alert_history)[-50:]],  # 最新50件
            "uptime_hours": (time.time() - self.start_time) / 3600
        }
        
        report_file = output_path / f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        return report_file


# テスト用メイン関数
if __name__ == "__main__":
    # システム監視の初期化
    config = {
        "monitoring_interval": 10.0,
        "metrics_interval": 5.0
    }
    monitor = SystemMonitor(config)
    
    # 監視開始
    monitor.start_monitoring()
    
    try:
        # テスト実行
        time.sleep(30.0)
        
        # システム健全性の表示
        health = monitor.get_system_health()
        print(f"システム状態: {health['overall_status']}")
        print(f"アクティブアラート数: {health['active_alerts_count']}")
        
        # 現在のメトリクス表示
        metrics = monitor.get_current_metrics()
        if "system.cpu_percent" in metrics:
            print(f"CPU使用率: {metrics['system.cpu_percent']['value']:.1f}%")
        if "system.memory_percent" in metrics:
            print(f"メモリ使用率: {metrics['system.memory_percent']['value']:.1f}%")
        
        # 監視レポートのエクスポート
        report_path = monitor.export_monitoring_report(Path("logs"))
        print(f"監視レポート出力: {report_path}")
        
    finally:
        # 監視停止
        monitor.stop_monitoring()