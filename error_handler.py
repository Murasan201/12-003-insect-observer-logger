"""
エラーハンドリング統合管理モジュール

システム全体の統一的なエラー処理とリカバリー機能を提供する。
- エラー分類と重要度管理
- エラーロギングとレポート生成
- 自動リトライとフォールバック処理
- エラー統計と分析
- アラート通知連携
"""

import logging
import traceback
import json
import time
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import threading
from collections import deque, defaultdict
import functools


class ErrorSeverity(Enum):
    """エラー重要度レベル"""
    DEBUG = "debug"      # デバッグ情報
    INFO = "info"        # 情報メッセージ
    WARNING = "warning"  # 警告（処理は継続）
    ERROR = "error"      # エラー（部分的な失敗）
    CRITICAL = "critical"  # 致命的エラー（システム停止が必要）


class ErrorCategory(Enum):
    """エラーカテゴリー"""
    HARDWARE = "hardware"        # ハードウェア関連
    NETWORK = "network"          # ネットワーク関連
    DETECTION = "detection"      # 検出処理関連
    PROCESSING = "processing"    # データ処理関連
    STORAGE = "storage"          # ストレージ関連
    CONFIGURATION = "configuration"  # 設定関連
    RESOURCE = "resource"        # リソース不足
    PERMISSION = "permission"    # 権限関連
    VALIDATION = "validation"    # データ検証関連
    UNKNOWN = "unknown"          # 不明なエラー


@dataclass
class ErrorContext:
    """エラーコンテキスト情報"""
    module_name: str
    function_name: str
    input_data: Optional[Dict[str, Any]] = None
    state_info: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    recovery_attempted: bool = False
    recovery_successful: bool = False


@dataclass
class ErrorRecord:
    """エラー記録データ"""
    error_id: str
    timestamp: str
    severity: ErrorSeverity
    category: ErrorCategory
    error_type: str
    error_message: str
    traceback: str
    context: ErrorContext
    resolved: bool = False
    resolution_time: Optional[str] = None
    resolution_method: Optional[str] = None
    impact_assessment: Optional[str] = None


@dataclass
class ErrorStatistics:
    """エラー統計情報"""
    total_errors: int = 0
    errors_by_severity: Dict[str, int] = field(default_factory=dict)
    errors_by_category: Dict[str, int] = field(default_factory=dict)
    errors_by_module: Dict[str, int] = field(default_factory=dict)
    error_rate_per_hour: float = 0.0
    most_frequent_errors: List[Dict[str, Any]] = field(default_factory=list)
    recovery_success_rate: float = 0.0
    average_recovery_time_seconds: float = 0.0


class RecoveryStrategy:
    """リカバリー戦略基底クラス"""
    def can_handle(self, error: ErrorRecord) -> bool:
        """このストラテジーがエラーを処理できるか判定"""
        raise NotImplementedError
    
    def recover(self, error: ErrorRecord) -> bool:
        """リカバリー処理を実行"""
        raise NotImplementedError


class RetryStrategy(RecoveryStrategy):
    """リトライベースのリカバリー戦略"""
    def __init__(self, max_retries: int = 3, backoff_seconds: float = 1.0):
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
    
    def can_handle(self, error: ErrorRecord) -> bool:
        """一時的なエラーに対してリトライ可能か判定"""
        return (error.category in [ErrorCategory.NETWORK, ErrorCategory.RESOURCE] and
                error.context.retry_count < self.max_retries)
    
    def recover(self, error: ErrorRecord) -> bool:
        """指数バックオフでリトライ"""
        wait_time = self.backoff_seconds * (2 ** error.context.retry_count)
        time.sleep(wait_time)
        return True  # リトライ実行を示す


class RestartStrategy(RecoveryStrategy):
    """モジュール再起動によるリカバリー戦略"""
    def can_handle(self, error: ErrorRecord) -> bool:
        """ハードウェアエラーに対して再起動可能か判定"""
        return error.category == ErrorCategory.HARDWARE
    
    def recover(self, error: ErrorRecord) -> bool:
        """モジュールの再初期化を要求"""
        logging.info(f"モジュール再起動を要求: {error.context.module_name}")
        return True


class ErrorHandler:
    """エラーハンドリング統合管理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # エラー記録
        self.error_history: deque = deque(maxlen=1000)  # 最新1000件を保持
        self.error_counts = defaultdict(int)
        self.module_errors = defaultdict(list)
        
        # リカバリー戦略
        self.recovery_strategies: List[RecoveryStrategy] = [
            RetryStrategy(),
            RestartStrategy()
        ]
        
        # 統計情報
        self.statistics = ErrorStatistics()
        self.start_time = datetime.now()
        
        # エラーハンドラー登録
        self.error_handlers: Dict[ErrorCategory, List[Callable]] = defaultdict(list)
        
        # ロック
        self.lock = threading.Lock()
        
        # エラーログファイル
        self.error_log_path = Path("logs/errors")
        self.error_log_path.mkdir(parents=True, exist_ok=True)
        
        self._setup_error_logging()
    
    def _setup_error_logging(self):
        """エラー専用ロギング設定"""
        error_handler = logging.FileHandler(
            self.error_log_path / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        )
        error_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def handle_error(self, 
                    exception: Exception,
                    context: ErrorContext,
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    category: ErrorCategory = ErrorCategory.UNKNOWN) -> ErrorRecord:
        """エラーを処理し記録する"""
        with self.lock:
            # エラーレコード作成
            error_record = ErrorRecord(
                error_id=self._generate_error_id(),
                timestamp=datetime.now().isoformat(),
                severity=severity,
                category=category,
                error_type=type(exception).__name__,
                error_message=str(exception),
                traceback=traceback.format_exc(),
                context=context
            )
            
            # エラー記録
            self._record_error(error_record)
            
            # リカバリー処理
            if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                self._attempt_recovery(error_record)
            
            # アラート通知（必要に応じて）
            if severity == ErrorSeverity.CRITICAL:
                self._send_alert(error_record)
            
            return error_record
    
    def _generate_error_id(self) -> str:
        """一意のエラーIDを生成"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len(self.error_history)
        return f"ERR-{timestamp}-{count:04d}"
    
    def _record_error(self, error: ErrorRecord):
        """エラーを記録"""
        # メモリ内記録
        self.error_history.append(error)
        self.error_counts[error.severity.value] += 1
        self.module_errors[error.context.module_name].append(error)
        
        # 統計更新
        self._update_statistics(error)
        
        # ファイル記録
        self._save_error_to_file(error)
        
        # ログ出力
        log_method = getattr(self.logger, error.severity.value)
        log_method(
            f"[{error.category.value}] {error.error_message} "
            f"(Module: {error.context.module_name})"
        )
    
    def _update_statistics(self, error: ErrorRecord):
        """統計情報を更新"""
        self.statistics.total_errors += 1
        
        # 重要度別カウント
        severity_key = error.severity.value
        if severity_key not in self.statistics.errors_by_severity:
            self.statistics.errors_by_severity[severity_key] = 0
        self.statistics.errors_by_severity[severity_key] += 1
        
        # カテゴリー別カウント
        category_key = error.category.value
        if category_key not in self.statistics.errors_by_category:
            self.statistics.errors_by_category[category_key] = 0
        self.statistics.errors_by_category[category_key] += 1
        
        # モジュール別カウント
        module_key = error.context.module_name
        if module_key not in self.statistics.errors_by_module:
            self.statistics.errors_by_module[module_key] = 0
        self.statistics.errors_by_module[module_key] += 1
        
        # エラー率計算
        uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
        if uptime_hours > 0:
            self.statistics.error_rate_per_hour = self.statistics.total_errors / uptime_hours
    
    def _save_error_to_file(self, error: ErrorRecord):
        """エラーをファイルに保存"""
        error_file = self.error_log_path / f"error_{error.error_id}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(error), f, ensure_ascii=False, indent=2, default=str)
    
    def _attempt_recovery(self, error: ErrorRecord):
        """エラーリカバリーを試行"""
        for strategy in self.recovery_strategies:
            if strategy.can_handle(error):
                try:
                    error.context.recovery_attempted = True
                    success = strategy.recover(error)
                    error.context.recovery_successful = success
                    
                    if success:
                        error.resolved = True
                        error.resolution_time = datetime.now().isoformat()
                        error.resolution_method = type(strategy).__name__
                        self.logger.info(
                            f"エラーリカバリー成功: {error.error_id} "
                            f"(Method: {error.resolution_method})"
                        )
                        break
                except Exception as e:
                    self.logger.error(f"リカバリー処理中にエラー: {e}")
    
    def _send_alert(self, error: ErrorRecord):
        """重大エラーのアラート送信"""
        # TODO: アラートマネージャーと連携
        self.logger.critical(
            f"CRITICAL ERROR ALERT: {error.error_id} - {error.error_message}"
        )
    
    def register_handler(self, category: ErrorCategory, handler: Callable):
        """カテゴリー別のエラーハンドラーを登録"""
        self.error_handlers[category].append(handler)
    
    def get_statistics(self) -> ErrorStatistics:
        """エラー統計情報を取得"""
        with self.lock:
            # 最頻出エラーの計算
            error_messages = defaultdict(int)
            for error in self.error_history:
                error_messages[error.error_message] += 1
            
            self.statistics.most_frequent_errors = [
                {"message": msg, "count": count}
                for msg, count in sorted(
                    error_messages.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ]
            
            # リカバリー成功率の計算
            recovery_attempts = sum(
                1 for e in self.error_history if e.context.recovery_attempted
            )
            recovery_successes = sum(
                1 for e in self.error_history if e.context.recovery_successful
            )
            if recovery_attempts > 0:
                self.statistics.recovery_success_rate = (
                    recovery_successes / recovery_attempts * 100
                )
            
            return self.statistics
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorRecord]:
        """最近のエラーを取得"""
        with self.lock:
            return list(self.error_history)[-count:]
    
    def get_errors_by_module(self, module_name: str) -> List[ErrorRecord]:
        """モジュール別のエラーを取得"""
        with self.lock:
            return self.module_errors.get(module_name, [])
    
    def clear_resolved_errors(self):
        """解決済みエラーをクリア"""
        with self.lock:
            self.error_history = deque(
                (e for e in self.error_history if not e.resolved),
                maxlen=1000
            )
    
    def export_error_report(self, output_path: Path) -> Path:
        """エラーレポートをエクスポート"""
        report = {
            "report_time": datetime.now().isoformat(),
            "statistics": asdict(self.get_statistics()),
            "recent_errors": [
                asdict(e) for e in self.get_recent_errors(50)
            ],
            "unresolved_critical_errors": [
                asdict(e) for e in self.error_history
                if e.severity == ErrorSeverity.CRITICAL and not e.resolved
            ]
        }
        
        report_file = output_path / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        return report_file


def error_handler_decorator(
    handler: ErrorHandler,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    max_retries: int = 3
):
    """エラーハンドリングデコレーター"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context = ErrorContext(
                module_name=func.__module__,
                function_name=func.__name__,
                max_retries=max_retries
            )
            
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    context.retry_count = attempt
                    
                    error_record = handler.handle_error(
                        exception=e,
                        context=context,
                        severity=severity,
                        category=category
                    )
                    
                    if attempt < max_retries and error_record.context.recovery_successful:
                        logging.info(f"リトライ {attempt + 1}/{max_retries}")
                        continue
                    else:
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator


# テスト用メイン関数
if __name__ == "__main__":
    # エラーハンドラーの初期化
    config = {
        "max_error_history": 1000,
        "alert_threshold": 10
    }
    error_handler = ErrorHandler(config)
    
    # テスト用のエラー生成
    try:
        # ネットワークエラーのシミュレーション
        raise ConnectionError("サーバーに接続できません")
    except Exception as e:
        context = ErrorContext(
            module_name="test_module",
            function_name="test_function",
            input_data={"url": "http://example.com"}
        )
        error_handler.handle_error(
            e, context,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.NETWORK
        )
    
    # 統計情報の表示
    stats = error_handler.get_statistics()
    print(f"総エラー数: {stats.total_errors}")
    print(f"エラー率: {stats.error_rate_per_hour:.2f} errors/hour")
    
    # エラーレポートのエクスポート
    report_path = error_handler.export_error_report(Path("logs"))
    print(f"エラーレポート出力: {report_path}")