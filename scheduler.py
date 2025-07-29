"""
スケジューラー管理モジュール

定期的な検出・分析処理のスケジューリングと実行管理を行う。
- 定期検出処理のスケジューリング
- 日次分析処理の自動実行
- タスクキューとジョブ管理
- スケジュール動的変更
- 障害時の自動復旧
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, time as dt_time
from collections import defaultdict
import json
from enum import Enum


class TaskStatus(Enum):
    """タスク状態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """スケジュールタスク"""
    task_id: str
    name: str
    function: Callable
    interval_seconds: int
    next_run_time: datetime
    last_run_time: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    run_count: int = 0
    error_count: int = 0
    last_error: str = ""
    enabled: bool = True
    max_retries: int = 3


@dataclass
class SchedulerStats:
    """スケジューラー統計"""
    total_tasks_executed: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    current_active_tasks: int = 0
    scheduler_uptime_seconds: float = 0.0
    last_execution_time: str = ""
    average_execution_time_ms: float = 0.0


class SchedulerManager:
    """
    スケジューラー管理クラス
    
    Features:
    - 定期検出処理スケジューリング
    - 日次分析処理の自動実行
    - タスク実行状態監視
    - エラーハンドリング・リトライ
    - 動的スケジュール調整
    - パフォーマンス統計
    """
    
    def __init__(self, 
                 detection_interval: int = 300,  # 5分間隔
                 analysis_time: str = "23:00"):  # 23時に日次分析
        """
        スケジューラー初期化
        
        Args:
            detection_interval: 検出間隔 (秒)
            analysis_time: 日次分析時刻 (HH:MM)
        """
        self.logger = logging.getLogger(__name__ + '.SchedulerManager')
        
        # 設定
        self.detection_interval = detection_interval
        self.analysis_time = analysis_time
        
        # タスク管理
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_threads: Dict[str, threading.Thread] = {}
        
        # 状態管理
        self.running = False
        self.paused = False
        self.start_time: Optional[datetime] = None
        self.stats = SchedulerStats()
        
        # スレッド管理
        self.scheduler_thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
        
        # 実行時間履歴
        self.execution_times: List[float] = []
        
        self.logger.info("Scheduler manager initialized")
    
    def schedule_detection(self, detection_function: Callable) -> str:
        """
        検出処理スケジューリング
        
        Args:
            detection_function: 検出処理関数
            
        Returns:
            str: タスクID
        """
        try:
            task_id = "detection_task"
            next_run = datetime.now() + timedelta(seconds=self.detection_interval)
            
            task = ScheduledTask(
                task_id=task_id,
                name="昆虫検出処理",
                function=detection_function,
                interval_seconds=self.detection_interval,
                next_run_time=next_run,
                max_retries=3
            )
            
            self.tasks[task_id] = task
            self.logger.info(f"Detection task scheduled: interval={self.detection_interval}s")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Detection scheduling failed: {e}")
            return ""
    
    def schedule_daily_analysis(self, analysis_function: Callable) -> str:
        """
        日次分析スケジューリング
        
        Args:
            analysis_function: 分析処理関数
            
        Returns:
            str: タスクID
        """
        try:
            task_id = "daily_analysis_task"
            
            # 次回実行時刻計算
            next_run = self._calculate_next_daily_run()
            
            task = ScheduledTask(
                task_id=task_id,
                name="日次分析処理",
                function=analysis_function,
                interval_seconds=24 * 3600,  # 24時間間隔
                next_run_time=next_run,
                max_retries=2
            )
            
            self.tasks[task_id] = task
            self.logger.info(f"Daily analysis scheduled: time={self.analysis_time}")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Daily analysis scheduling failed: {e}")
            return ""
    
    def _calculate_next_daily_run(self) -> datetime:
        """次回日次分析実行時刻計算"""
        try:
            # 分析時刻パース
            hour, minute = map(int, self.analysis_time.split(':'))
            
            # 今日の分析時刻
            today = datetime.now().date()
            analysis_datetime = datetime.combine(today, dt_time(hour, minute))
            
            # 既に過ぎている場合は明日
            if analysis_datetime <= datetime.now():
                analysis_datetime += timedelta(days=1)
            
            return analysis_datetime
            
        except Exception as e:
            self.logger.error(f"Daily run time calculation failed: {e}")
            return datetime.now() + timedelta(hours=1)
    
    def schedule_custom_task(self, 
                           task_id: str,
                           name: str,
                           function: Callable,
                           interval_seconds: int,
                           delay_seconds: int = 0) -> bool:
        """
        カスタムタスクスケジューリング
        
        Args:
            task_id: タスクID
            name: タスク名
            function: 実行関数
            interval_seconds: 実行間隔 (秒)
            delay_seconds: 初回実行遅延 (秒)
            
        Returns:
            bool: スケジュール成功可否
        """
        try:
            if task_id in self.tasks:
                self.logger.warning(f"Task {task_id} already exists, replacing")
            
            next_run = datetime.now() + timedelta(seconds=delay_seconds)
            
            task = ScheduledTask(
                task_id=task_id,
                name=name,
                function=function,
                interval_seconds=interval_seconds,
                next_run_time=next_run
            )
            
            self.tasks[task_id] = task
            self.logger.info(f"Custom task scheduled: {task_id} ({name})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Custom task scheduling failed: {e}")
            return False
    
    def start(self) -> bool:
        """スケジューラー開始"""
        try:
            if self.running:
                self.logger.warning("Scheduler already running")
                return True
            
            self.running = True
            self.start_time = datetime.now()
            self.shutdown_event.clear()
            
            # スケジューラースレッド開始
            self.scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True
            )
            self.scheduler_thread.start()
            
            self.logger.info("Scheduler started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Scheduler start failed: {e}")
            self.running = False
            return False
    
    def stop(self) -> bool:
        """スケジューラー停止"""
        try:
            if not self.running:
                self.logger.warning("Scheduler not running")
                return True
            
            self.logger.info("Stopping scheduler...")
            self.running = False
            self.shutdown_event.set()
            
            # 実行中タスクの停止待機
            self._wait_for_tasks_completion(timeout=30)
            
            # スレッド終了待機
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            self.logger.info("Scheduler stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Scheduler stop failed: {e}")
            return False
    
    def pause_detection(self, duration_seconds: int) -> None:
        """検出処理の一時停止"""
        try:
            if "detection_task" in self.tasks:
                task = self.tasks["detection_task"]
                task.next_run_time = datetime.now() + timedelta(seconds=duration_seconds)
                task.enabled = False
                
                self.logger.info(f"Detection paused for {duration_seconds} seconds")
                
                # 自動再開タスク
                def resume_detection():
                    time.sleep(duration_seconds)
                    if "detection_task" in self.tasks:
                        self.tasks["detection_task"].enabled = True
                        self.logger.info("Detection resumed automatically")
                
                resume_thread = threading.Thread(target=resume_detection, daemon=True)
                resume_thread.start()
            
        except Exception as e:
            self.logger.error(f"Detection pause failed: {e}")
    
    def update_detection_interval(self, new_interval: int) -> bool:
        """検出間隔更新"""
        try:
            if "detection_task" in self.tasks:
                task = self.tasks["detection_task"]
                task.interval_seconds = new_interval
                
                # 次回実行時刻を新しい間隔で調整
                task.next_run_time = datetime.now() + timedelta(seconds=new_interval)
                
                self.detection_interval = new_interval
                self.logger.info(f"Detection interval updated to {new_interval} seconds")
                return True
            else:
                self.logger.error("Detection task not found")
                return False
            
        except Exception as e:
            self.logger.error(f"Detection interval update failed: {e}")
            return False
    
    def _scheduler_loop(self) -> None:
        """メインスケジューラーループ"""
        try:
            while self.running and not self.shutdown_event.is_set():
                try:
                    # 実行すべきタスクをチェック
                    self._check_and_execute_tasks()
                    
                    # 統計更新
                    self._update_stats()
                    
                    # 短時間待機
                    time.sleep(1.0)
                    
                except Exception as e:
                    self.logger.error(f"Scheduler loop error: {e}")
                    time.sleep(5.0)  # エラー時は少し長く待機
                    
        except Exception as e:
            self.logger.error(f"Scheduler loop failed: {e}")
        finally:
            self.running = False
    
    def _check_and_execute_tasks(self) -> None:
        """実行すべきタスクのチェック・実行"""
        try:
            current_time = datetime.now()
            
            for task_id, task in self.tasks.items():
                if not task.enabled or task.status == TaskStatus.RUNNING:
                    continue
                
                # 実行時刻チェック
                if current_time >= task.next_run_time:
                    self._execute_task(task)
            
        except Exception as e:
            self.logger.error(f"Task checking failed: {e}")
    
    def _execute_task(self, task: ScheduledTask) -> None:
        """タスク実行"""
        try:
            task.status = TaskStatus.RUNNING
            task.last_run_time = datetime.now()
            
            # 別スレッドで実行
            thread = threading.Thread(
                target=self._task_runner,
                args=(task,),
                daemon=True
            )
            
            self.task_threads[task.task_id] = thread
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.error_count += 1
            task.last_error = str(e)
    
    def _task_runner(self, task: ScheduledTask) -> None:
        """タスク実行ランナー"""
        try:
            start_time = time.time()
            
            self.logger.debug(f"Executing task: {task.name}")
            
            # タスク関数実行
            result = task.function()
            
            # 実行時間記録
            execution_time = (time.time() - start_time) * 1000  # ms
            self.execution_times.append(execution_time)
            if len(self.execution_times) > 100:
                self.execution_times = self.execution_times[-100:]
            
            # 成功処理
            task.status = TaskStatus.COMPLETED
            task.run_count += 1
            self.stats.successful_executions += 1
            
            # 次回実行時刻設定
            task.next_run_time = datetime.now() + timedelta(seconds=task.interval_seconds)
            
            self.logger.debug(f"Task completed: {task.name} in {execution_time:.1f}ms")
            
        except Exception as e:
            # エラー処理
            task.status = TaskStatus.FAILED
            task.error_count += 1
            task.last_error = str(e)
            self.stats.failed_executions += 1
            
            self.logger.error(f"Task failed: {task.name} - {e}")
            
            # リトライ処理
            if task.error_count <= task.max_retries:
                retry_delay = min(60 * task.error_count, 300)  # 最大5分
                task.next_run_time = datetime.now() + timedelta(seconds=retry_delay)
                task.status = TaskStatus.PENDING
                self.logger.info(f"Task {task.name} scheduled for retry in {retry_delay}s")
            else:
                # 最大リトライ回数に達した場合は無効化
                task.enabled = False
                self.logger.error(f"Task {task.name} disabled after {task.max_retries} failures")
                
        finally:
            # スレッド管理から削除
            if task.task_id in self.task_threads:
                del self.task_threads[task.task_id]
            
            self.stats.total_tasks_executed += 1
    
    def _wait_for_tasks_completion(self, timeout: int = 30) -> None:
        """実行中タスクの完了待機"""
        try:
            start_time = time.time()
            
            while self.task_threads and (time.time() - start_time) < timeout:
                # 完了したスレッドを削除
                completed_threads = []
                for task_id, thread in self.task_threads.items():
                    if not thread.is_alive():
                        completed_threads.append(task_id)
                
                for task_id in completed_threads:
                    del self.task_threads[task_id]
                
                if self.task_threads:
                    time.sleep(1.0)
                else:
                    break
            
            # タイムアウト時の強制終了
            if self.task_threads:
                self.logger.warning(f"Forcing termination of {len(self.task_threads)} tasks")
                
        except Exception as e:
            self.logger.error(f"Task completion wait failed: {e}")
    
    def _update_stats(self) -> None:
        """統計情報更新"""
        try:
            if self.start_time:
                self.stats.scheduler_uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            
            self.stats.current_active_tasks = len(self.task_threads)
            self.stats.last_execution_time = datetime.now().isoformat()
            
            # 平均実行時間
            if self.execution_times:
                self.stats.average_execution_time_ms = sum(self.execution_times) / len(self.execution_times)
            
        except Exception as e:
            self.logger.error(f"Stats update failed: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """タスク状態取得"""
        try:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            
            return {
                "task_id": task.task_id,
                "name": task.name,
                "status": task.status.value,
                "enabled": task.enabled,
                "run_count": task.run_count,
                "error_count": task.error_count,
                "last_run_time": task.last_run_time.isoformat() if task.last_run_time else None,
                "next_run_time": task.next_run_time.isoformat(),
                "last_error": task.last_error,
                "interval_seconds": task.interval_seconds
            }
            
        except Exception as e:
            self.logger.error(f"Task status retrieval failed: {e}")
            return None
    
    def get_all_tasks_status(self) -> Dict[str, Any]:
        """全タスク状態取得"""
        try:
            tasks_status = {}
            
            for task_id in self.tasks:
                task_status = self.get_task_status(task_id)
                if task_status:
                    tasks_status[task_id] = task_status
            
            return {
                "scheduler_running": self.running,
                "scheduler_paused": self.paused,
                "total_tasks": len(self.tasks),
                "active_tasks": len(self.task_threads),
                "tasks": tasks_status,
                "stats": {
                    "total_executions": self.stats.total_tasks_executed,
                    "successful_executions": self.stats.successful_executions,
                    "failed_executions": self.stats.failed_executions,
                    "uptime_seconds": self.stats.scheduler_uptime_seconds,
                    "average_execution_time_ms": self.stats.average_execution_time_ms
                }
            }
            
        except Exception as e:
            self.logger.error(f"All tasks status retrieval failed: {e}")
            return {"error": str(e)}
    
    def enable_task(self, task_id: str) -> bool:
        """タスク有効化"""
        try:
            if task_id in self.tasks:
                self.tasks[task_id].enabled = True
                self.tasks[task_id].error_count = 0  # エラーカウントリセット
                self.logger.info(f"Task enabled: {task_id}")
                return True
            else:
                self.logger.error(f"Task not found: {task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Task enabling failed: {e}")
            return False
    
    def disable_task(self, task_id: str) -> bool:
        """タスク無効化"""
        try:
            if task_id in self.tasks:
                self.tasks[task_id].enabled = False
                self.logger.info(f"Task disabled: {task_id}")
                return True
            else:
                self.logger.error(f"Task not found: {task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Task disabling failed: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """タスク削除"""
        try:
            if task_id in self.tasks:
                # 実行中の場合は停止
                if task_id in self.task_threads:
                    # スレッドの自然終了を待つ（強制終了は行わない）
                    self.logger.info(f"Waiting for running task to complete: {task_id}")
                
                del self.tasks[task_id]
                self.logger.info(f"Task removed: {task_id}")
                return True
            else:
                self.logger.error(f"Task not found: {task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Task removal failed: {e}")
            return False
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            # スケジューラー停止
            self.stop()
            
            # タスククリア
            self.tasks.clear()
            self.task_threads.clear()
            
            # 履歴クリア
            self.execution_times.clear()
            
            self.logger.info("Scheduler manager cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Scheduler cleanup failed: {e}")


# 使用例・テスト関数
def test_scheduler():
    """スケジューラーのテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # スケジューラー作成
    scheduler = SchedulerManager(
        detection_interval=10,  # 10秒間隔
        analysis_time="12:00"
    )
    
    try:
        # テスト関数定義
        def test_detection():
            logger.info("Test detection executed")
            return {"result": "detection_success"}
        
        def test_analysis():
            logger.info("Test analysis executed")
            return {"result": "analysis_success"}
        
        # タスクスケジューリング
        detection_id = scheduler.schedule_detection(test_detection)
        analysis_id = scheduler.schedule_daily_analysis(test_analysis)
        
        logger.info(f"Scheduled tasks: detection={detection_id}, analysis={analysis_id}")
        
        # スケジューラー開始
        if scheduler.start():
            logger.info("Scheduler started, running for 30 seconds...")
            
            # 30秒間実行
            time.sleep(30)
            
            # 状態確認
            status = scheduler.get_all_tasks_status()
            logger.info(f"Scheduler status: {status}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        scheduler.cleanup()


if __name__ == "__main__":
    test_scheduler()