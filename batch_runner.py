"""
昆虫自動観察システム - バッチ処理・スケジューリング

cronやタスクスケジューラからの定期実行、
バッチ処理スクリプトの実行をサポート。
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import schedule
import time
import threading
import signal
from dataclasses import dataclass, asdict
import subprocess

# プロジェクト内モジュール
from main import InsectObserverSystem, setup_logging
from config.config_manager import ConfigManager


@dataclass
class BatchJob:
    """バッチジョブ定義"""
    name: str
    command: str
    schedule_type: str  # 'interval', 'daily', 'weekly'
    schedule_time: str  # '10:30' for daily, '60' for interval
    enabled: bool = True
    last_run: Optional[str] = None
    last_status: Optional[str] = None
    error_count: int = 0
    

@dataclass
class BatchResult:
    """バッチ実行結果"""
    job_name: str
    start_time: str
    end_time: str
    status: str  # 'success', 'error', 'timeout'
    output: str
    error: Optional[str] = None
    

class BatchRunner:
    """
    バッチ処理実行エンジン
    
    Features:
    - 定期実行スケジューリング
    - 複数ジョブの並列実行
    - エラーハンドリング・リトライ
    - 実行ログ記録
    - 実行結果通知
    """
    
    def __init__(self, config_path: str = "./config/batch_config.json"):
        """
        初期化
        
        Args:
            config_path: バッチ設定ファイルパス
        """
        self.logger = logging.getLogger(__name__ + '.BatchRunner')
        self.config_path = config_path
        self.jobs: Dict[str, BatchJob] = {}
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # ジョブ設定読み込み
        self._load_job_config()
        
        # シグナルハンドラ設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _load_job_config(self) -> None:
        """ジョブ設定読み込み"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                for job_data in config_data.get('jobs', []):
                    job = BatchJob(**job_data)
                    self.jobs[job.name] = job
                    
                self.logger.info(f"Loaded {len(self.jobs)} batch jobs")
            else:
                # デフォルト設定作成
                self._create_default_config()
                
        except Exception as e:
            self.logger.error(f"Failed to load job config: {e}")
    
    def _create_default_config(self) -> None:
        """デフォルト設定作成"""
        default_jobs = [
            {
                "name": "hourly_detection",
                "command": "python main.py --mode single",
                "schedule_type": "interval",
                "schedule_time": "3600",  # 1時間ごと
                "enabled": True
            },
            {
                "name": "daily_analysis",
                "command": "python main.py --mode analysis",
                "schedule_type": "daily",
                "schedule_time": "02:00",  # 深夜2時
                "enabled": True
            },
            {
                "name": "weekly_cleanup",
                "command": "python cli.py cleanup --older-than 30",
                "schedule_type": "weekly",
                "schedule_time": "sunday",
                "enabled": True
            },
            {
                "name": "daily_backup",
                "command": "python scripts/backup_data.py",
                "schedule_type": "daily", 
                "schedule_time": "03:00",
                "enabled": False
            }
        ]
        
        config_data = {"jobs": default_jobs}
        
        # ディレクトリ作成
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 設定保存
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Created default batch config: {self.config_path}")
        
        # 再読み込み
        self._load_job_config()
    
    def save_job_config(self) -> None:
        """ジョブ設定保存"""
        try:
            jobs_data = [asdict(job) for job in self.jobs.values()]
            config_data = {"jobs": jobs_data}
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info("Job configuration saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save job config: {e}")
    
    def add_job(self, job: BatchJob) -> None:
        """ジョブ追加"""
        self.jobs[job.name] = job
        self.save_job_config()
        
        # スケジューラーが動作中なら再設定
        if self.running:
            self._setup_job_schedule(job)
            
        self.logger.info(f"Added job: {job.name}")
    
    def remove_job(self, job_name: str) -> bool:
        """ジョブ削除"""
        if job_name in self.jobs:
            del self.jobs[job_name]
            self.save_job_config()
            
            # スケジューラーから削除
            schedule.clear(job_name)
            
            self.logger.info(f"Removed job: {job_name}")
            return True
        return False
    
    def enable_job(self, job_name: str, enabled: bool = True) -> bool:
        """ジョブ有効/無効化"""
        if job_name in self.jobs:
            self.jobs[job_name].enabled = enabled
            self.save_job_config()
            
            if enabled and self.running:
                self._setup_job_schedule(self.jobs[job_name])
            elif not enabled:
                schedule.clear(job_name)
                
            self.logger.info(f"Job {job_name} {'enabled' if enabled else 'disabled'}")
            return True
        return False
    
    def _setup_job_schedule(self, job: BatchJob) -> None:
        """ジョブスケジュール設定"""
        if not job.enabled:
            return
            
        try:
            # 既存のスケジュールをクリア
            schedule.clear(job.name)
            
            # ジョブ実行関数
            run_func = lambda: self._run_job(job)
            
            if job.schedule_type == 'interval':
                # 間隔実行（秒単位）
                interval_seconds = int(job.schedule_time)
                schedule.every(interval_seconds).seconds.do(run_func).tag(job.name)
                
            elif job.schedule_type == 'daily':
                # 日次実行
                schedule.every().day.at(job.schedule_time).do(run_func).tag(job.name)
                
            elif job.schedule_type == 'weekly':
                # 週次実行
                day_name = job.schedule_time.lower()
                if hasattr(schedule.every(), day_name):
                    getattr(schedule.every(), day_name).do(run_func).tag(job.name)
                    
            self.logger.info(f"Scheduled job: {job.name} ({job.schedule_type} at {job.schedule_time})")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule job {job.name}: {e}")
    
    def _run_job(self, job: BatchJob) -> BatchResult:
        """ジョブ実行"""
        start_time = datetime.now()
        self.logger.info(f"Starting job: {job.name}")
        
        result = BatchResult(
            job_name=job.name,
            start_time=start_time.isoformat(),
            end_time="",
            status="running",
            output=""
        )
        
        try:
            # コマンド実行
            process = subprocess.Popen(
                job.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # タイムアウト付き実行（30分）
            stdout, stderr = process.communicate(timeout=1800)
            
            end_time = datetime.now()
            result.end_time = end_time.isoformat()
            
            if process.returncode == 0:
                result.status = "success"
                result.output = stdout
                job.error_count = 0  # エラーカウントリセット
                self.logger.info(f"Job completed successfully: {job.name}")
            else:
                result.status = "error"
                result.output = stdout
                result.error = stderr
                job.error_count += 1
                self.logger.error(f"Job failed: {job.name} (exit code: {process.returncode})")
                
        except subprocess.TimeoutExpired:
            result.status = "timeout"
            result.error = "Job execution timeout (30 minutes)"
            job.error_count += 1
            self.logger.error(f"Job timeout: {job.name}")
            process.kill()
            
        except Exception as e:
            result.status = "error"
            result.error = str(e)
            job.error_count += 1
            self.logger.error(f"Job execution error: {job.name} - {e}")
        
        # ジョブ状態更新
        job.last_run = start_time.isoformat()
        job.last_status = result.status
        self.save_job_config()
        
        # 結果記録
        self._save_job_result(result)
        
        # エラー通知
        if result.status != "success" and job.error_count >= 3:
            self._notify_job_failure(job, result)
        
        return result
    
    def _save_job_result(self, result: BatchResult) -> None:
        """ジョブ実行結果保存"""
        try:
            # ログディレクトリ
            log_dir = Path("./logs/batch")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 日付別ログファイル
            log_file = log_dir / f"batch_{datetime.now().strftime('%Y%m%d')}.jsonl"
            
            # JSONL形式で追記
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(asdict(result), f, ensure_ascii=False)
                f.write('\n')
                
        except Exception as e:
            self.logger.error(f"Failed to save job result: {e}")
    
    def _notify_job_failure(self, job: BatchJob, result: BatchResult) -> None:
        """ジョブ失敗通知"""
        self.logger.critical(
            f"Job {job.name} has failed {job.error_count} times consecutively. "
            f"Last error: {result.error}"
        )
        
        # TODO: メール通知、Slack通知などの実装
    
    def run_scheduler(self) -> None:
        """スケジューラー実行"""
        self.running = True
        self.logger.info("Batch scheduler started")
        
        # 全ジョブのスケジュール設定
        for job in self.jobs.values():
            self._setup_job_schedule(job)
        
        # スケジューラーループ
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
        finally:
            self.running = False
            self.logger.info("Batch scheduler stopped")
    
    def run_job_immediately(self, job_name: str) -> Optional[BatchResult]:
        """ジョブ即時実行"""
        if job_name not in self.jobs:
            self.logger.error(f"Job not found: {job_name}")
            return None
            
        job = self.jobs[job_name]
        return self._run_job(job)
    
    def get_job_status(self) -> List[Dict[str, Any]]:
        """全ジョブ状態取得"""
        status_list = []
        
        for job in self.jobs.values():
            # 次回実行時刻取得
            next_run = None
            for scheduled_job in schedule.jobs:
                if job.name in scheduled_job.tags:
                    next_run = scheduled_job.next_run.isoformat() if scheduled_job.next_run else None
                    break
            
            status_list.append({
                "name": job.name,
                "enabled": job.enabled,
                "schedule_type": job.schedule_type,
                "schedule_time": job.schedule_time,
                "last_run": job.last_run,
                "last_status": job.last_status,
                "error_count": job.error_count,
                "next_run": next_run
            })
        
        return status_list
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラ"""
        self.logger.info(f"Received signal {signum}, stopping scheduler...")
        self.running = False


def create_cron_entry(job_name: str, schedule_time: str, 
                     python_path: str = "python") -> str:
    """
    cron エントリ生成
    
    Args:
        job_name: ジョブ名
        schedule_time: スケジュール時刻
        python_path: Pythonパス
        
    Returns:
        str: cronエントリ
    """
    script_path = Path(__file__).parent / "batch_runner.py"
    
    # 日次実行の場合
    if ':' in schedule_time:
        hour, minute = schedule_time.split(':')
        cron_time = f"{minute} {hour} * * *"
    else:
        # 間隔実行（分単位）
        minutes = int(schedule_time) // 60
        if minutes > 0:
            cron_time = f"*/{minutes} * * * *"
        else:
            cron_time = "* * * * *"  # 毎分
    
    return f"{cron_time} cd {script_path.parent} && {python_path} {script_path} run-job {job_name}"


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="バッチ処理ランナー")
    
    subparsers = parser.add_subparsers(dest='command', help='実行コマンド')
    
    # スケジューラー実行
    parser_scheduler = subparsers.add_parser('scheduler', help='スケジューラーを起動')
    
    # ジョブ即時実行
    parser_run = subparsers.add_parser('run-job', help='ジョブを即時実行')
    parser_run.add_argument('job_name', help='実行するジョブ名')
    
    # ジョブ一覧
    parser_list = subparsers.add_parser('list', help='ジョブ一覧を表示')
    
    # ジョブ追加
    parser_add = subparsers.add_parser('add', help='ジョブを追加')
    parser_add.add_argument('name', help='ジョブ名')
    parser_add.add_argument('command', help='実行コマンド')
    parser_add.add_argument('--type', choices=['interval', 'daily', 'weekly'],
                          default='daily', help='スケジュールタイプ')
    parser_add.add_argument('--time', required=True, help='実行時刻/間隔')
    
    # ジョブ削除
    parser_remove = subparsers.add_parser('remove', help='ジョブを削除')
    parser_remove.add_argument('job_name', help='削除するジョブ名')
    
    # ジョブ有効/無効
    parser_enable = subparsers.add_parser('enable', help='ジョブを有効化')
    parser_enable.add_argument('job_name', help='ジョブ名')
    
    parser_disable = subparsers.add_parser('disable', help='ジョブを無効化')
    parser_disable.add_argument('job_name', help='ジョブ名')
    
    # cron エントリ生成
    parser_cron = subparsers.add_parser('cron', help='cronエントリを生成')
    parser_cron.add_argument('job_name', help='ジョブ名')
    
    # 共通オプション
    parser.add_argument('--config', '-c', default='./config/batch_config.json',
                       help='バッチ設定ファイル')
    parser.add_argument('--log-level', '-l', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='ログレベル')
    
    args = parser.parse_args()
    
    # ログ設定
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # バッチランナー作成
    runner = BatchRunner(args.config)
    
    try:
        if args.command == 'scheduler':
            # スケジューラー起動
            logger.info("Starting batch scheduler...")
            runner.run_scheduler()
            
        elif args.command == 'run-job':
            # ジョブ即時実行
            result = runner.run_job_immediately(args.job_name)
            if result:
                print(f"Job: {result.job_name}")
                print(f"Status: {result.status}")
                print(f"Duration: {result.start_time} - {result.end_time}")
                if result.output:
                    print(f"Output:\n{result.output}")
                if result.error:
                    print(f"Error:\n{result.error}")
            else:
                print(f"Job not found: {args.job_name}")
                return 1
                
        elif args.command == 'list':
            # ジョブ一覧表示
            jobs = runner.get_job_status()
            
            if not jobs:
                print("No jobs configured")
            else:
                print(f"{'Name':<20} {'Enabled':<8} {'Type':<10} {'Schedule':<15} {'Last Run':<20} {'Status':<10}")
                print("-" * 90)
                
                for job in jobs:
                    print(f"{job['name']:<20} "
                          f"{'Yes' if job['enabled'] else 'No':<8} "
                          f"{job['schedule_type']:<10} "
                          f"{job['schedule_time']:<15} "
                          f"{job['last_run'] or 'Never':<20} "
                          f"{job['last_status'] or 'N/A':<10}")
                          
        elif args.command == 'add':
            # ジョブ追加
            new_job = BatchJob(
                name=args.name,
                command=args.command,
                schedule_type=args.type,
                schedule_time=args.time,
                enabled=True
            )
            runner.add_job(new_job)
            print(f"Added job: {args.name}")
            
        elif args.command == 'remove':
            # ジョブ削除
            if runner.remove_job(args.job_name):
                print(f"Removed job: {args.job_name}")
            else:
                print(f"Job not found: {args.job_name}")
                return 1
                
        elif args.command == 'enable':
            # ジョブ有効化
            if runner.enable_job(args.job_name, True):
                print(f"Enabled job: {args.job_name}")
            else:
                print(f"Job not found: {args.job_name}")
                return 1
                
        elif args.command == 'disable':
            # ジョブ無効化
            if runner.enable_job(args.job_name, False):
                print(f"Disabled job: {args.job_name}")
            else:
                print(f"Job not found: {args.job_name}")
                return 1
                
        elif args.command == 'cron':
            # cron エントリ生成
            if args.job_name in runner.jobs:
                job = runner.jobs[args.job_name]
                cron_entry = create_cron_entry(job.name, job.schedule_time)
                print(f"Cron entry for {job.name}:")
                print(cron_entry)
                print("\nAdd this line to your crontab (crontab -e)")
            else:
                print(f"Job not found: {args.job_name}")
                return 1
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())