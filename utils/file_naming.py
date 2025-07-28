"""
昆虫自動観察システム - ファイル命名規則ユーティリティ

このモジュールはシステム内で使用するファイルの命名規則を統一管理します。

Classes:
    FileNamingConvention: ファイル命名規則クラス
"""

import os
import re
from datetime import datetime, date
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path


class FileNamingConvention:
    """ファイル命名規則クラス
    
    システム内で使用される全てのファイルの命名規則を定義・管理します。
    """
    
    # 日付フォーマット定義
    DATE_FORMAT = "%Y%m%d"              # 20250727
    DATETIME_FORMAT = "%Y%m%d_%H%M%S"   # 20250727_103045
    TIME_FORMAT = "%H%M%S"              # 103045
    
    # ファイル名パターン定義
    # 検出関連ファイル
    DETECTION_LOG_PATTERN = "detection_{date}.csv"
    DETECTION_DETAIL_PATTERN = "details_{date}.csv"
    
    # 統計関連ファイル
    DAILY_SUMMARY_PATTERN = "daily_summary_{date}.csv"
    HOURLY_SUMMARY_PATTERN = "hourly_summary_{date}.csv"
    MONTHLY_REPORT_PATTERN = "monthly_report_{year}{month:02d}.json"
    
    # 画像ファイル
    ORIGINAL_IMAGE_PATTERN = "{datetime}_{sequence:03d}.jpg"
    ANNOTATED_IMAGE_PATTERN = "{datetime}_{sequence:03d}_annotated.png"
    THUMBNAIL_IMAGE_PATTERN = "{datetime}_{sequence:03d}_thumb.jpg"
    
    # 可視化ファイル
    ACTIVITY_CHART_PATTERN = "activity_chart_{date}.png"
    MOVEMENT_HEATMAP_PATTERN = "movement_heatmap_{date}.png"
    HOURLY_ACTIVITY_CHART_PATTERN = "hourly_activity_{date}.png"
    MOVEMENT_TRAJECTORY_PATTERN = "trajectory_{date}.png"
    SUMMARY_DASHBOARD_PATTERN = "dashboard_{date}.png"
    
    # ログファイル
    SYSTEM_LOG_PATTERN = "system_{date}.log"
    DETECTION_LOG_FILE_PATTERN = "detection_{date}.log"
    ERROR_LOG_PATTERN = "error_{date}.log"
    PERFORMANCE_LOG_PATTERN = "performance_{date}.log"
    
    # バックアップファイル
    DAILY_BACKUP_PATTERN = "backup_{date}.tar.gz"
    WEEKLY_BACKUP_PATTERN = "backup_week_{week_number:02d}.tar.gz"
    MONTHLY_BACKUP_PATTERN = "backup_month_{year}{month:02d}.tar.gz"
    
    # 設定ファイル
    CONFIG_BACKUP_PATTERN = "config_backup_{datetime}.json"
    
    # 一時ファイル
    TEMP_IMAGE_PATTERN = "temp_{datetime}_{random}.jpg" 
    TEMP_DATA_PATTERN = "temp_{datetime}_{purpose}.csv"
    
    @classmethod
    def generate_detection_log_filename(cls, target_date: datetime) -> str:
        """検出ログファイル名を生成
        
        Args:
            target_date: 対象日付
            
        Returns:
            検出ログファイル名
        """
        return cls.DETECTION_LOG_PATTERN.format(
            date=target_date.strftime(cls.DATE_FORMAT)
        )
    
    @classmethod
    def generate_detection_detail_filename(cls, target_date: datetime) -> str:
        """検出詳細ファイル名を生成
        
        Args:
            target_date: 対象日付
            
        Returns:
            検出詳細ファイル名
        """
        return cls.DETECTION_DETAIL_PATTERN.format(
            date=target_date.strftime(cls.DATE_FORMAT)
        )
    
    @classmethod
    def generate_daily_summary_filename(cls, target_date: datetime) -> str:
        """日次統計ファイル名を生成
        
        Args:
            target_date: 対象日付
            
        Returns:
            日次統計ファイル名
        """
        return cls.DAILY_SUMMARY_PATTERN.format(
            date=target_date.strftime(cls.DATE_FORMAT)
        )
    
    @classmethod
    def generate_hourly_summary_filename(cls, target_date: datetime) -> str:
        """時間別統計ファイル名を生成
        
        Args:
            target_date: 対象日付
            
        Returns:
            時間別統計ファイル名
        """
        return cls.HOURLY_SUMMARY_PATTERN.format(
            date=target_date.strftime(cls.DATE_FORMAT)
        )
    
    @classmethod
    def generate_monthly_report_filename(cls, year: int, month: int) -> str:
        """月次レポートファイル名を生成
        
        Args:
            year: 年
            month: 月
            
        Returns:
            月次レポートファイル名
        """
        return cls.MONTHLY_REPORT_PATTERN.format(year=year, month=month)
    
    @classmethod
    def generate_image_filename(cls, timestamp: datetime, sequence: int, 
                              annotated: bool = False, thumbnail: bool = False) -> str:
        """画像ファイル名を生成
        
        Args:
            timestamp: タイムスタンプ
            sequence: シーケンス番号
            annotated: 注釈付き画像かどうか
            thumbnail: サムネイル画像かどうか
            
        Returns:
            画像ファイル名
        """
        datetime_str = timestamp.strftime(cls.DATETIME_FORMAT)
        
        if thumbnail:
            return cls.THUMBNAIL_IMAGE_PATTERN.format(
                datetime=datetime_str, sequence=sequence
            )
        elif annotated:
            return cls.ANNOTATED_IMAGE_PATTERN.format(
                datetime=datetime_str, sequence=sequence
            )
        else:
            return cls.ORIGINAL_IMAGE_PATTERN.format(
                datetime=datetime_str, sequence=sequence
            )
    
    @classmethod
    def generate_visualization_filename(cls, target_date: datetime, 
                                      chart_type: str) -> str:
        """可視化ファイル名を生成
        
        Args:
            target_date: 対象日付
            chart_type: チャートタイプ（activity, heatmap, hourly, trajectory, dashboard）
            
        Returns:
            可視化ファイル名
            
        Raises:
            ValueError: サポートされていないチャートタイプの場合
        """
        date_str = target_date.strftime(cls.DATE_FORMAT)
        
        pattern_mapping = {
            'activity': cls.ACTIVITY_CHART_PATTERN,
            'heatmap': cls.MOVEMENT_HEATMAP_PATTERN,
            'hourly': cls.HOURLY_ACTIVITY_CHART_PATTERN,
            'trajectory': cls.MOVEMENT_TRAJECTORY_PATTERN,
            'dashboard': cls.SUMMARY_DASHBOARD_PATTERN
        }
        
        if chart_type not in pattern_mapping:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        return pattern_mapping[chart_type].format(date=date_str)
    
    @classmethod
    def generate_log_filename(cls, target_date: datetime, log_type: str) -> str:
        """ログファイル名を生成
        
        Args:
            target_date: 対象日付
            log_type: ログタイプ（system, detection, error, performance）
            
        Returns:
            ログファイル名
            
        Raises:
            ValueError: サポートされていないログタイプの場合
        """
        date_str = target_date.strftime(cls.DATE_FORMAT)
        
        pattern_mapping = {
            'system': cls.SYSTEM_LOG_PATTERN,
            'detection': cls.DETECTION_LOG_FILE_PATTERN,
            'error': cls.ERROR_LOG_PATTERN,
            'performance': cls.PERFORMANCE_LOG_PATTERN
        }
        
        if log_type not in pattern_mapping:
            raise ValueError(f"Unsupported log type: {log_type}")
        
        return pattern_mapping[log_type].format(date=date_str)
    
    @classmethod
    def generate_backup_filename(cls, target_date: datetime, 
                                backup_type: str = 'daily', 
                                week_number: Optional[int] = None) -> str:
        """バックアップファイル名を生成
        
        Args:
            target_date: 対象日付
            backup_type: バックアップタイプ（daily, weekly, monthly）
            week_number: 週番号（週次バックアップの場合）
            
        Returns:
            バックアップファイル名
            
        Raises:
            ValueError: サポートされていないバックアップタイプの場合
        """
        if backup_type == 'daily':
            date_str = target_date.strftime(cls.DATE_FORMAT)
            return cls.DAILY_BACKUP_PATTERN.format(date=date_str)
        
        elif backup_type == 'weekly':
            if week_number is None:
                week_number = target_date.isocalendar()[1]
            return cls.WEEKLY_BACKUP_PATTERN.format(week_number=week_number)
        
        elif backup_type == 'monthly':
            return cls.MONTHLY_BACKUP_PATTERN.format(
                year=target_date.year, month=target_date.month
            )
        
        else:
            raise ValueError(f"Unsupported backup type: {backup_type}")
    
    @classmethod
    def generate_config_backup_filename(cls, timestamp: datetime) -> str:
        """設定バックアップファイル名を生成
        
        Args:
            timestamp: タイムスタンプ
            
        Returns:
            設定バックアップファイル名
        """
        datetime_str = timestamp.strftime(cls.DATETIME_FORMAT)
        return cls.CONFIG_BACKUP_PATTERN.format(datetime=datetime_str)
    
    @classmethod
    def generate_temp_filename(cls, purpose: str, file_type: str = 'csv',
                             timestamp: Optional[datetime] = None) -> str:
        """一時ファイル名を生成
        
        Args:
            purpose: ファイルの用途
            file_type: ファイルタイプ（csv, jpg, png, etc.）
            timestamp: タイムスタンプ（Noneの場合は現在時刻）
            
        Returns:
            一時ファイル名
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        datetime_str = timestamp.strftime(cls.DATETIME_FORMAT)
        
        if file_type.lower() in ['jpg', 'jpeg', 'png']:
            import random
            random_str = f"{random.randint(1000, 9999)}"
            return cls.TEMP_IMAGE_PATTERN.format(
                datetime=datetime_str, random=random_str
            ).replace('.jpg', f'.{file_type}')
        else:
            return cls.TEMP_DATA_PATTERN.format(
                datetime=datetime_str, purpose=purpose
            ).replace('.csv', f'.{file_type}')
    
    @classmethod
    def parse_filename_timestamp(cls, filename: str) -> Optional[datetime]:
        """ファイル名からタイムスタンプを抽出
        
        Args:
            filename: 解析対象ファイル名
            
        Returns:
            抽出されたタイムスタンプ（抽出失敗の場合はNone）
        """
        # 日時パターンを抽出（YYYYMMDD_HHMMSS）
        datetime_pattern = r'(\d{8}_\d{6})'
        match = re.search(datetime_pattern, filename)
        
        if match:
            datetime_str = match.group(1)
            try:
                return datetime.strptime(datetime_str, cls.DATETIME_FORMAT)
            except ValueError:
                pass
        
        # 日付のみパターンを抽出（YYYYMMDD）
        date_pattern = r'(\d{8})'
        match = re.search(date_pattern, filename)
        
        if match:
            date_str = match.group(1)
            try:
                return datetime.strptime(date_str, cls.DATE_FORMAT)
            except ValueError:
                pass
        
        return None
    
    @classmethod
    def parse_filename_date(cls, filename: str) -> Optional[date]:
        """ファイル名から日付を抽出
        
        Args:
            filename: 解析対象ファイル名
            
        Returns:
            抽出された日付（抽出失敗の場合はNone）
        """
        timestamp = cls.parse_filename_timestamp(filename)
        return timestamp.date() if timestamp else None
    
    @classmethod
    def get_file_type_from_filename(cls, filename: str) -> str:
        """ファイル名からファイルタイプを判定
        
        Args:
            filename: 判定対象ファイル名
            
        Returns:
            ファイルタイプ（detection_log, image, visualization, log, backup, config, temp, unknown）
        """
        filename_lower = filename.lower()
        
        # 検出ログ
        if filename.startswith('detection_') and filename.endswith('.csv'):
            return 'detection_log'
        
        if filename.startswith('details_') and filename.endswith('.csv'):
            return 'detection_detail'
        
        # 統計ファイル
        if filename.startswith('daily_summary_'):
            return 'daily_summary'
        
        if filename.startswith('hourly_summary_'):
            return 'hourly_summary'
        
        if filename.startswith('monthly_report_'):
            return 'monthly_report'
        
        # 画像ファイル
        if '_annotated.png' in filename:
            return 'annotated_image'
        elif '_thumb.jpg' in filename:
            return 'thumbnail_image'
        elif filename_lower.endswith(('.jpg', '.jpeg', '.png')):
            return 'original_image'
        
        # 可視化ファイル
        visualization_prefixes = ['activity_chart_', 'movement_heatmap_', 
                                'hourly_activity_', 'trajectory_', 'dashboard_']
        if any(filename.startswith(prefix) for prefix in visualization_prefixes):
            return 'visualization'
        
        # ログファイル
        log_prefixes = ['system_', 'detection_', 'error_', 'performance_']
        if any(filename.startswith(prefix) for prefix in log_prefixes) and filename.endswith('.log'):
            return 'log'
        
        # バックアップファイル
        if filename.startswith('backup_') and filename.endswith('.tar.gz'):
            return 'backup'
        
        # 設定ファイル
        if filename.startswith('config_backup_'):
            return 'config'
        
        # 一時ファイル
        if filename.startswith('temp_'):
            return 'temp'
        
        return 'unknown'
    
    @classmethod
    def list_files_by_pattern(cls, directory: str, pattern_type: str, 
                            start_date: Optional[date] = None,
                            end_date: Optional[date] = None) -> List[str]:
        """パターンに基づくファイル一覧取得
        
        Args:
            directory: 検索対象ディレクトリ
            pattern_type: パターンタイプ（detection_log, image, visualization等）
            start_date: 開始日付（Noneの場合は制限なし）
            end_date: 終了日付（Noneの場合は制限なし）
            
        Returns:
            マッチするファイル名のリスト
        """
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return []
        
        matching_files = []
        
        for file_path in directory_path.iterdir():
            if not file_path.is_file():
                continue
            
            filename = file_path.name
            file_type = cls.get_file_type_from_filename(filename)
            
            # パターンタイプでフィルタ
            if pattern_type != 'all' and file_type != pattern_type:
                continue
            
            # 日付範囲でフィルタ
            if start_date or end_date:
                file_date = cls.parse_filename_date(filename)
                if file_date:
                    if start_date and file_date < start_date:
                        continue
                    if end_date and file_date > end_date:
                        continue
            
            matching_files.append(filename)
        
        return sorted(matching_files)
    
    @classmethod
    def get_filename_info(cls, filename: str) -> Dict[str, Any]:
        """ファイル名からの情報抽出
        
        Args:
            filename: 解析対象ファイル名
            
        Returns:
            ファイル情報の辞書
        """
        info = {
            'original_filename': filename,
            'file_type': cls.get_file_type_from_filename(filename),
            'timestamp': cls.parse_filename_timestamp(filename),
            'date': cls.parse_filename_date(filename),
            'extension': Path(filename).suffix.lower(),
            'basename': Path(filename).stem
        }
        
        # シーケンス番号の抽出（画像ファイルの場合）
        if info['file_type'] in ['original_image', 'annotated_image', 'thumbnail_image']:
            sequence_match = re.search(r'_(\d{3})(?:_|\.)', filename)
            if sequence_match:
                info['sequence_number'] = int(sequence_match.group(1))
        
        # 週番号の抽出（週次バックアップの場合）
        if info['file_type'] == 'backup' and 'week_' in filename:
            week_match = re.search(r'week_(\d{2})', filename)
            if week_match:
                info['week_number'] = int(week_match.group(1))
        
        return info
    
    @classmethod
    def validate_filename(cls, filename: str, expected_type: str) -> Tuple[bool, List[str]]:
        """ファイル名の妥当性検証
        
        Args:
            filename: 検証対象ファイル名
            expected_type: 期待されるファイルタイプ
            
        Returns:
            (検証成功可否, エラーメッセージリスト)
        """
        errors = []
        
        # 基本的な文字チェック
        if not filename:
            errors.append("Filename is empty")
            return False, errors
        
        # 禁止文字チェック
        forbidden_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in filename for char in forbidden_chars):
            errors.append(f"Filename contains forbidden characters: {forbidden_chars}")
        
        # 長さチェック
        if len(filename) > 255:
            errors.append("Filename too long (max 255 characters)")
        
        # ファイルタイプ一致チェック
        actual_type = cls.get_file_type_from_filename(filename)
        if expected_type != 'any' and actual_type != expected_type:
            errors.append(f"Expected file type '{expected_type}', got '{actual_type}'")
        
        # タイムスタンプ妥当性チェック
        timestamp = cls.parse_filename_timestamp(filename)
        if timestamp and actual_type != 'unknown':
            # 未来の日付チェック
            if timestamp > datetime.now():
                errors.append("Timestamp is in the future")
            
            # 過去すぎる日付チェック
            if timestamp.year < 2025:
                errors.append("Timestamp is too old (before 2025)")
        
        return len(errors) == 0, errors