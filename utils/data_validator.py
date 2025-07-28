"""
昆虫自動観察システム - データ検証ユーティリティ

このモジュールはシステム内で使用されるデータの検証機能を提供します。

Classes:
    DataValidationRules: データ検証ルール定義クラス
    DataValidator: データ検証実行クラス
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union, Tuple
import logging

from models.detection_models import DetectionResult, DetectionRecord
from models.activity_models import DailyActivitySummary, HourlyActivitySummary


class DataValidationRules:
    """データ検証ルール定義クラス
    
    各種データタイプに対する検証ルールを定義します。
    """
    
    # 検出データ検証ルール
    DETECTION_RULES = {
        'timestamp': {
            'required': True,
            'type': 'datetime',
            'format': 'ISO8601',
            'range': {
                'min': datetime(2025, 1, 1),
                'max': datetime(2030, 12, 31)
            }
        },
        'insect_detected': {
            'required': True,
            'type': 'boolean'
        },
        'detection_count': {
            'required': True,
            'type': 'integer',
            'range': {'min': 0, 'max': 50}
        },
        'x_center': {
            'required_if': 'insect_detected == True',
            'type': 'float',
            'range': {'min': 0.0, 'max': 1920.0}
        },
        'y_center': {
            'required_if': 'insect_detected == True',
            'type': 'float',
            'range': {'min': 0.0, 'max': 1080.0}
        },
        'confidence': {
            'required_if': 'insect_detected == True',
            'type': 'float',
            'range': {'min': 0.0, 'max': 1.0}
        },
        'processing_time_ms': {
            'required': True,
            'type': 'float',
            'range': {'min': 0.0, 'max': 30000.0}  # 30秒以内
        }
    }
    
    # 統計データ検証ルール
    SUMMARY_RULES = {
        'summary_date': {
            'required': True,
            'type': 'date',
            'format': 'YYYY-MM-DD'
        },
        'total_detections': {
            'required': True,
            'type': 'integer',
            'range': {'min': 0, 'max': 2000}  # 1日最大2000検出
        },
        'total_movement_distance': {
            'required': True,
            'type': 'float',
            'range': {'min': 0.0, 'max': 100000.0}
        },
        'data_completeness_ratio': {
            'required': True,
            'type': 'float',
            'range': {'min': 0.0, 'max': 1.0}
        }
    }
    
    # 画像データ検証ルール
    IMAGE_RULES = {
        'min_width': 320,
        'min_height': 240,
        'max_width': 4096,
        'max_height': 3072,
        'supported_channels': [1, 3, 4],  # グレースケール、RGB、RGBA
        'supported_dtypes': [np.uint8, np.uint16, np.float32]
    }


class DataValidator:
    """データ検証実行クラス
    
    各種データタイプの検証を実行し、エラーや警告を報告します。
    """
    
    def __init__(self):
        """DataValidator初期化"""
        self.rules = DataValidationRules()
        self.validation_errors = []
        self.logger = logging.getLogger(__name__)
    
    def validate_image(self, image: np.ndarray) -> bool:
        """画像データの検証
        
        Args:
            image: 検証対象の画像データ
            
        Returns:
            検証成功可否
        """
        if image is None:
            self.logger.error("Image is None")
            return False
        
        if not isinstance(image, np.ndarray):
            self.logger.error(f"Image must be numpy.ndarray, got {type(image)}")
            return False
        
        # 次元数チェック
        if len(image.shape) not in [2, 3]:
            self.logger.error(f"Image must be 2D or 3D array, got {len(image.shape)}D")
            return False
        
        # 解像度チェック
        height, width = image.shape[:2]
        if width < self.rules.IMAGE_RULES['min_width'] or height < self.rules.IMAGE_RULES['min_height']:
            self.logger.error(f"Image resolution too small: {width}x{height}")
            return False
        
        if width > self.rules.IMAGE_RULES['max_width'] or height > self.rules.IMAGE_RULES['max_height']:
            self.logger.warning(f"Image resolution very large: {width}x{height}")
        
        # チャンネル数チェック（3次元の場合）
        if len(image.shape) == 3:
            channels = image.shape[2]
            if channels not in self.rules.IMAGE_RULES['supported_channels']:
                self.logger.error(f"Unsupported channel count: {channels}")
                return False
        
        # データ型チェック
        if image.dtype not in self.rules.IMAGE_RULES['supported_dtypes']:
            self.logger.warning(f"Unusual image dtype: {image.dtype}")
        
        return True
    
    def validate_detection_result(self, result: DetectionResult) -> bool:
        """検出結果の検証
        
        Args:
            result: 検証対象の検出結果
            
        Returns:
            検証成功可否
        """
        try:
            # DetectionResult自体の検証メソッドを使用
            result.validate()
            return True
        except ValueError as e:
            self.logger.error(f"DetectionResult validation failed: {e}")
            return False
    
    def validate_detection_record(self, record: DetectionRecord) -> List[str]:
        """検出レコードの検証
        
        Args:
            record: 検証対象レコード
            
        Returns:
            検証エラーメッセージのリスト
        """
        errors = []
        
        # 必須項目チェック
        if not record.timestamp:
            errors.append("timestamp is required")
        
        if record.insect_detected is None:
            errors.append("insect_detected is required")
        
        # 条件付き必須項目チェック
        if record.insect_detected and not record.x_center:
            errors.append("x_center is required when insect_detected is True")
        
        if record.insect_detected and not record.y_center:
            errors.append("y_center is required when insect_detected is True")
        
        if record.insect_detected and not record.confidence:
            errors.append("confidence is required when insect_detected is True")
        
        # 範囲チェック
        if record.confidence and (record.confidence < 0.0 or record.confidence > 1.0):
            errors.append(f"confidence out of range: {record.confidence}")
        
        if record.processing_time_ms and record.processing_time_ms > 30000.0:
            errors.append(f"processing_time_ms too high: {record.processing_time_ms}ms")
        
        if record.processing_time_ms < 0.0:
            errors.append(f"processing_time_ms cannot be negative: {record.processing_time_ms}")
        
        # 座標範囲チェック
        if record.x_center is not None and (record.x_center < 0 or record.x_center > 1920):
            errors.append(f"x_center out of range: {record.x_center}")
        
        if record.y_center is not None and (record.y_center < 0 or record.y_center > 1080):
            errors.append(f"y_center out of range: {record.y_center}")
        
        # データ整合性チェック
        if record.insect_detected and record.detection_count == 0:
            errors.append("detection_count should be > 0 when insect_detected is True")
        
        if not record.insect_detected and record.detection_count > 0:
            errors.append("detection_count should be 0 when insect_detected is False")
        
        # タイムスタンプ妥当性チェック
        if record.timestamp:
            now = datetime.now()
            if record.timestamp > now:
                errors.append(f"timestamp is in the future: {record.timestamp}")
            
            if record.timestamp.year < 2025:
                errors.append(f"timestamp too old: {record.timestamp}")
        
        return errors
    
    def validate_csv_file(self, filepath: str) -> Dict[str, Any]:
        """CSVファイルの検証
        
        Args:
            filepath: 検証対象ファイルパス
            
        Returns:
            検証結果サマリー
        """
        validation_result = {
            'filepath': filepath,
            'is_valid': True,
            'total_records': 0,
            'valid_records': 0,
            'error_records': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # CSVファイル読み込み
            df = pd.read_csv(filepath)
            validation_result['total_records'] = len(df)
            
            # 空ファイルチェック
            if len(df) == 0:
                validation_result['warnings'].append("CSV file is empty")
                return validation_result
            
            # 列存在チェック
            required_columns = ['timestamp', 'insect_detected', 'detection_count']
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                validation_result['errors'].append(
                    f"Missing required columns: {missing_columns}"
                )
                validation_result['is_valid'] = False
                return validation_result
            
            # データ型チェック
            type_errors = self._validate_dataframe_types(df)
            validation_result['errors'].extend(type_errors)
            
            # レコード単位検証
            for index, row in df.iterrows():
                try:
                    record_errors = self._validate_csv_row(row)
                    if record_errors:
                        validation_result['error_records'] += 1
                        validation_result['errors'].extend([
                            f"Row {index + 1}: {error}" for error in record_errors
                        ])
                    else:
                        validation_result['valid_records'] += 1
                except Exception as e:
                    validation_result['error_records'] += 1
                    validation_result['errors'].append(f"Row {index + 1}: Processing error: {e}")
            
            # 全体統計チェック
            self._validate_file_statistics(df, validation_result)
            
        except FileNotFoundError:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"File not found: {filepath}")
        except pd.errors.EmptyDataError:
            validation_result['warnings'].append("CSV file is empty")
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"File processing error: {str(e)}")
        
        if validation_result['errors']:
            validation_result['is_valid'] = False
        
        return validation_result
    
    def _validate_dataframe_types(self, df: pd.DataFrame) -> List[str]:
        """DataFrameのデータ型検証
        
        Args:
            df: 検証対象DataFrame
            
        Returns:
            型エラーメッセージのリスト
        """
        errors = []
        
        # 数値列の検証
        numeric_columns = ['x_center', 'y_center', 'confidence', 'processing_time_ms', 'detection_count']
        for column in numeric_columns:
            if column in df.columns:
                try:
                    pd.to_numeric(df[column], errors='coerce')
                except Exception as e:
                    errors.append(f"Column {column} is not numeric: {e}")
        
        # ブール列の検証
        boolean_columns = ['insect_detected']
        for column in boolean_columns:
            if column in df.columns:
                unique_values = df[column].dropna().unique()
                valid_bool_values = {True, False, 'true', 'false', 'True', 'False', 1, 0, '1', '0'}
                invalid_values = set(unique_values) - valid_bool_values
                if invalid_values:
                    errors.append(f"Column {column} contains invalid boolean values: {invalid_values}")
        
        return errors
    
    def _validate_csv_row(self, row: pd.Series) -> List[str]:
        """CSV行データの検証
        
        Args:
            row: 検証対象行
            
        Returns:
            行エラーメッセージのリスト
        """
        errors = []
        
        # タイムスタンプ検証
        if 'timestamp' in row:
            try:
                pd.to_datetime(row['timestamp'])
            except:
                errors.append("Invalid timestamp format")
        
        # 数値範囲検証
        numeric_validations = [
            ('confidence', 0.0, 1.0),
            ('x_center', 0.0, 1920.0),
            ('y_center', 0.0, 1080.0),
            ('processing_time_ms', 0.0, 30000.0),
            ('detection_count', 0, 50)
        ]
        
        for column, min_val, max_val in numeric_validations:
            if column in row and pd.notna(row[column]):
                try:
                    value = float(row[column]) if isinstance(min_val, float) else int(row[column])
                    if value < min_val or value > max_val:
                        errors.append(f"{column} out of range [{min_val}, {max_val}]: {value}")
                except (ValueError, TypeError):
                    errors.append(f"Invalid {column} value: {row[column]}")
        
        # 論理整合性検証
        if 'insect_detected' in row and 'detection_count' in row:
            try:
                detected = str(row['insect_detected']).lower() in ['true', '1', 1, True]
                count = int(row['detection_count']) if pd.notna(row['detection_count']) else 0
                
                if detected and count == 0:
                    errors.append("detection_count should be > 0 when insect detected")
                elif not detected and count > 0:
                    errors.append("detection_count should be 0 when no insect detected")
            except (ValueError, TypeError):
                errors.append("Cannot validate detection logic due to invalid data types")
        
        return errors
    
    def _validate_file_statistics(self, df: pd.DataFrame, result: Dict[str, Any]) -> None:
        """ファイル統計の検証
        
        Args:
            df: 検証対象DataFrame
            result: 検証結果辞書（更新される）
        """
        # 重複タイムスタンプチェック
        if 'timestamp' in df.columns:
            duplicate_timestamps = df['timestamp'].duplicated().sum()
            if duplicate_timestamps > 0:
                result['warnings'].append(
                    f"{duplicate_timestamps} duplicate timestamps found"
                )
        
        # 時系列順序チェック
        if 'timestamp' in df.columns:
            try:
                timestamps = pd.to_datetime(df['timestamp'])
                if not timestamps.is_monotonic_increasing:
                    result['warnings'].append("Timestamps are not in chronological order")
            except:
                result['warnings'].append("Cannot verify timestamp ordering due to invalid formats")
        
        # 検出率チェック
        if 'insect_detected' in df.columns:
            try:
                detection_series = df['insect_detected'].apply(
                    lambda x: str(x).lower() in ['true', '1'] if pd.notna(x) else False
                )
                detection_rate = detection_series.mean()
                
                if detection_rate > 0.5:  # 50%以上の検出は異常
                    result['warnings'].append(
                        f"High detection rate: {detection_rate:.1%} (may indicate false positives)"
                    )
                elif detection_rate == 0.0:
                    result['warnings'].append("No detections found in entire file")
            except Exception as e:
                result['warnings'].append(f"Cannot calculate detection rate: {e}")
        
        # データ完全性チェック
        missing_data_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if missing_data_ratio > 0.1:  # 10%以上の欠損
            result['warnings'].append(
                f"High missing data ratio: {missing_data_ratio:.1%}"
            )
    
    def sanitize_coordinates(self, x: float, y: float, 
                           img_shape: Tuple[int, int]) -> Tuple[float, float]:
        """座標の正規化・範囲内調整
        
        Args:
            x: X座標
            y: Y座標
            img_shape: 画像サイズ (height, width)
            
        Returns:
            正規化された (x, y) 座標
        """
        height, width = img_shape
        
        # 範囲内に制限
        x_sanitized = max(0.0, min(float(x), float(width - 1)))
        y_sanitized = max(0.0, min(float(y), float(height - 1)))
        
        return x_sanitized, y_sanitized
    
    def validate_activity_summary(self, summary: DailyActivitySummary) -> List[str]:
        """活動量統計の検証
        
        Args:
            summary: 検証対象の活動量統計
            
        Returns:
            検証エラーメッセージのリスト
        """
        errors = []
        
        # 基本範囲チェック
        if summary.total_detections < 0:
            errors.append(f"total_detections cannot be negative: {summary.total_detections}")
        
        if summary.total_movement_distance < 0.0:
            errors.append(f"total_movement_distance cannot be negative: {summary.total_movement_distance}")
        
        if summary.most_active_hour < 0 or summary.most_active_hour > 23:
            errors.append(f"most_active_hour must be 0-23: {summary.most_active_hour}")
        
        if summary.data_completeness_ratio < 0.0 or summary.data_completeness_ratio > 1.0:
            errors.append(f"data_completeness_ratio must be 0.0-1.0: {summary.data_completeness_ratio}")
        
        # 論理整合性チェック
        if summary.total_detections == 0:
            if summary.total_movement_distance > 0:
                errors.append("total_movement_distance should be 0 when no detections")
            if summary.first_detection_time or summary.last_detection_time:
                errors.append("detection times should be None when no detections")
        
        if summary.total_detections > 0:
            if summary.average_movement_per_detection < 0:
                errors.append("average_movement_per_detection cannot be negative when detections exist")
        
        # 時間整合性チェック
        if summary.first_detection_time and summary.last_detection_time:
            if summary.first_detection_time > summary.last_detection_time:
                errors.append("first_detection_time cannot be after last_detection_time")
        
        return errors
    
    def validate_hourly_summary(self, summary: HourlyActivitySummary) -> List[str]:
        """時間別統計の検証
        
        Args:
            summary: 検証対象の時間別統計
            
        Returns:
            検証エラーメッセージのリスト
        """
        errors = []
        
        # 基本範囲チェック
        if summary.hour < 0 or summary.hour > 23:
            errors.append(f"hour must be 0-23: {summary.hour}")
        
        if summary.detections_count < 0:
            errors.append(f"detections_count cannot be negative: {summary.detections_count}")
        
        if summary.movement_distance < 0.0:
            errors.append(f"movement_distance cannot be negative: {summary.movement_distance}")
        
        if summary.average_confidence < 0.0 or summary.average_confidence > 1.0:
            errors.append(f"average_confidence must be 0.0-1.0: {summary.average_confidence}")
        
        if summary.detection_frequency < 0.0:
            errors.append(f"detection_frequency cannot be negative: {summary.detection_frequency}")
        
        # 論理整合性チェック
        if summary.detections_count == 0:
            if summary.movement_distance > 0:
                errors.append("movement_distance should be 0 when no detections")
            if summary.average_confidence > 0:
                errors.append("average_confidence should be 0 when no detections")
            if summary.detection_frequency > 0:
                errors.append("detection_frequency should be 0 when no detections")
        
        return errors