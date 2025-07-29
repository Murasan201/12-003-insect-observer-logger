"""
検出結果処理モジュール

昆虫検出結果の後処理・フィルタリング・分析を行う。
- 検出結果の品質評価・フィルタリング
- 重複検出の除去
- 検出データの統計分析
- CSVログ出力
- 検出履歴管理
"""

import logging
import csv
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import json

# プロジェクト内モジュール
from models.detection_models import DetectionResult, DetectionRecord
from models.activity_models import HourlyActivitySummary, DailyActivitySummary
from utils.data_validator import DataValidator
from utils.file_naming import generate_log_filename


@dataclass
class ProcessingSettings:
    """検出後処理設定"""
    min_confidence: float = 0.6
    max_confidence: float = 1.0
    min_size: Tuple[float, float] = (10.0, 10.0)  # width, height in pixels
    max_size: Tuple[float, float] = (500.0, 500.0)
    duplicate_threshold: float = 0.7  # IoU threshold for duplicate detection
    quality_threshold: float = 0.5
    enable_size_filter: bool = True
    enable_confidence_filter: bool = True
    enable_duplicate_filter: bool = True
    save_filtered_data: bool = True


@dataclass
class ProcessingStats:
    """処理統計情報"""
    total_processed: int = 0
    total_filtered_out: int = 0
    confidence_filtered: int = 0
    size_filtered: int = 0
    duplicate_filtered: int = 0
    quality_filtered: int = 0
    csv_records_written: int = 0
    processing_errors: int = 0
    last_processing_time: str = ""


class DetectionProcessor:
    """
    検出結果処理クラス
    
    Features:
    - 検出品質フィルタリング
    - 重複検出除去
    - 統計分析・集計
    - CSV形式でのデータ出力
    - 時系列データ管理
    - 履歴データ分析
    """
    
    def __init__(self, 
                 settings: Optional[ProcessingSettings] = None,
                 output_dir: str = "./logs"):
        """
        処理器初期化
        
        Args:
            settings: 処理設定
            output_dir: 出力ディレクトリ
        """
        self.logger = logging.getLogger(__name__ + '.DetectionProcessor')
        
        # 設定
        self.settings = settings or ProcessingSettings()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 統計・状態管理
        self.stats = ProcessingStats()
        
        # データ検証器
        self.validator = DataValidator()
        
        # 履歴データキャッシュ
        self.detection_history: List[DetectionRecord] = []
        self.daily_summaries: Dict[str, DailyActivitySummary] = {}
        
        # CSV出力設定
        self.csv_headers = [
            'timestamp', 'detection_count', 'total_confidence', 'avg_confidence',
            'max_confidence', 'processing_time_ms', 'x_center', 'y_center',
            'width', 'height', 'confidence', 'class_id', 'quality_score'
        ]
        
        self.logger.info("Detection processor initialized")
    
    def process_detection_record(self, record: DetectionRecord) -> DetectionRecord:
        """
        検出記録の処理
        
        Args:
            record: 原始検出記録
            
        Returns:
            DetectionRecord: 処理済み検出記録
        """
        try:
            start_time = datetime.now()
            
            # 処理前検証
            if not self._validate_record(record):
                self.logger.warning("Invalid detection record received")
                self.stats.processing_errors += 1
                return record
            
            # 検出結果フィルタリング
            filtered_detections = self._filter_detections(record.detections)
            
            # 処理済み記録作成
            processed_record = DetectionRecord(
                timestamp=record.timestamp,
                image_path=record.image_path,
                detection_count=len(filtered_detections),
                detections=filtered_detections,
                processing_time_ms=record.processing_time_ms,
                confidence_threshold=record.confidence_threshold,
                model_version=record.model_version
            )
            
            # CSV出力
            self._write_to_csv(processed_record)
            
            # 履歴更新
            self._update_history(processed_record)
            
            # 統計更新
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_stats(record, processed_record, processing_time)
            
            self.logger.debug(f"Processed detection record: "
                            f"{record.detection_count} -> {processed_record.detection_count} detections")
            
            return processed_record
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            self.stats.processing_errors += 1
            return record
    
    def _validate_record(self, record: DetectionRecord) -> bool:
        """検出記録検証"""
        try:
            # 基本フィールド確認
            if not record.timestamp or not isinstance(record.detection_count, int):
                return False
            
            # タイムスタンプ検証
            try:
                datetime.fromisoformat(record.timestamp)
            except ValueError:
                self.logger.warning(f"Invalid timestamp format: {record.timestamp}")
                return False
            
            # 検出結果検証
            for detection in record.detections:
                if not self.validator.validate_detection_result(detection):
                    self.logger.warning(f"Invalid detection in record: {detection}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Record validation failed: {e}")
            return False
    
    def _filter_detections(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """検出結果フィルタリング"""
        filtered = detections.copy()
        
        # 1. 信頼度フィルタ
        if self.settings.enable_confidence_filter:
            before_count = len(filtered)
            filtered = self._filter_by_confidence(filtered)
            self.stats.confidence_filtered += before_count - len(filtered)
        
        # 2. サイズフィルタ
        if self.settings.enable_size_filter:
            before_count = len(filtered)
            filtered = self._filter_by_size(filtered)
            self.stats.size_filtered += before_count - len(filtered)
        
        # 3. 重複除去
        if self.settings.enable_duplicate_filter:
            before_count = len(filtered)
            filtered = self._remove_duplicates(filtered)
            self.stats.duplicate_filtered += before_count - len(filtered)
        
        # 4. 品質フィルタ
        before_count = len(filtered)
        filtered = self._filter_by_quality(filtered)
        self.stats.quality_filtered += before_count - len(filtered)
        
        return filtered
    
    def _filter_by_confidence(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """信頼度によるフィルタリング"""
        return [
            detection for detection in detections
            if self.settings.min_confidence <= detection.confidence <= self.settings.max_confidence
        ]
    
    def _filter_by_size(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """サイズによるフィルタリング"""
        min_w, min_h = self.settings.min_size
        max_w, max_h = self.settings.max_size
        
        return [
            detection for detection in detections
            if (min_w <= detection.width <= max_w and 
                min_h <= detection.height <= max_h)
        ]
    
    def _remove_duplicates(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """重複検出除去（IoU基準）"""
        if len(detections) <= 1:
            return detections
        
        # 信頼度でソート（高い順）
        sorted_detections = sorted(detections, key=lambda x: x.confidence, reverse=True)
        
        filtered = []
        for detection in sorted_detections:
            is_duplicate = False
            
            for existing in filtered:
                iou = self._calculate_iou(detection, existing)
                if iou > self.settings.duplicate_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(detection)
        
        return filtered
    
    def _calculate_iou(self, det1: DetectionResult, det2: DetectionResult) -> float:
        """IoU (Intersection over Union) 計算"""
        try:
            # バウンディングボックス変換
            x1_1 = det1.x_center - det1.width / 2
            y1_1 = det1.y_center - det1.height / 2
            x2_1 = det1.x_center + det1.width / 2
            y2_1 = det1.y_center + det1.height / 2
            
            x1_2 = det2.x_center - det2.width / 2
            y1_2 = det2.y_center - det2.height / 2
            x2_2 = det2.x_center + det2.width / 2
            y2_2 = det2.y_center + det2.height / 2
            
            # 交差領域計算
            x1_inter = max(x1_1, x1_2)
            y1_inter = max(y1_1, y1_2)
            x2_inter = min(x2_1, x2_2)
            y2_inter = min(y2_1, y2_2)
            
            if x2_inter <= x1_inter or y2_inter <= y1_inter:
                return 0.0
            
            intersection = (x2_inter - x1_inter) * (y2_inter - y1_inter)
            
            # 合算領域計算
            area1 = det1.width * det1.height
            area2 = det2.width * det2.height
            union = area1 + area2 - intersection
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"IoU calculation failed: {e}")
            return 0.0
    
    def _filter_by_quality(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """品質による追加フィルタリング"""
        filtered = []
        
        for detection in detections:
            quality_score = self._calculate_quality_score(detection)
            
            if quality_score >= self.settings.quality_threshold:
                filtered.append(detection)
        
        return filtered
    
    def _calculate_quality_score(self, detection: DetectionResult) -> float:
        """検出品質スコア計算"""
        try:
            # 基本スコアは信頼度
            score = detection.confidence
            
            # アスペクト比ペナルティ
            aspect_ratio = detection.width / detection.height if detection.height > 0 else 0
            if aspect_ratio < 0.5 or aspect_ratio > 3.0:  # 極端なアスペクト比
                score *= 0.8
            
            # サイズ正規化スコア
            size_score = min(1.0, (detection.width * detection.height) / 10000)  # 10000px^2を基準
            score *= (0.7 + 0.3 * size_score)
            
            # 境界近接ペナルティ（画像端の検出）
            # 注：実際の画像サイズが必要だが、ここでは簡易的に判定
            if (detection.x_center < 50 or detection.y_center < 50 or
                detection.x_center > 1870 or detection.y_center > 1030):  # 1920x1080想定
                score *= 0.9
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {e}")
            return detection.confidence
    
    def _write_to_csv(self, record: DetectionRecord) -> None:
        """CSV形式でデータ出力"""
        try:
            # ファイルパス生成
            date_str = datetime.fromisoformat(record.timestamp).strftime('%Y%m%d')
            csv_filename = f"detection_log_{date_str}.csv"
            csv_path = self.output_dir / csv_filename
            
            # ファイル存在確認とヘッダ書き込み
            file_exists = csv_path.exists()
            
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # ヘッダ書き込み（新規ファイルの場合）
                if not file_exists:
                    writer.writerow(self.csv_headers)
                
                # 検出がない場合も1行記録
                if len(record.detections) == 0:
                    writer.writerow([
                        record.timestamp, 0, 0.0, 0.0, 0.0, record.processing_time_ms,
                        '', '', '', '', '', '', 0.0
                    ])
                    self.stats.csv_records_written += 1
                else:
                    # 各検出結果を個別に記録
                    total_confidence = sum(d.confidence for d in record.detections)
                    avg_confidence = total_confidence / len(record.detections)
                    max_confidence = max(d.confidence for d in record.detections)
                    
                    for detection in record.detections:
                        quality_score = self._calculate_quality_score(detection)
                        
                        writer.writerow([
                            record.timestamp, record.detection_count, total_confidence,
                            avg_confidence, max_confidence, record.processing_time_ms,
                            detection.x_center, detection.y_center, detection.width,
                            detection.height, detection.confidence, detection.class_id,
                            quality_score
                        ])
                        
                        self.stats.csv_records_written += 1
            
            self.logger.debug(f"Data written to CSV: {csv_path}")
            
        except Exception as e:
            self.logger.error(f"CSV writing failed: {e}")
    
    def _update_history(self, record: DetectionRecord) -> None:
        """履歴データ更新"""
        try:
            # 履歴に追加
            self.detection_history.append(record)
            
            # 履歴サイズ制限（最大1000件）
            if len(self.detection_history) > 1000:
                self.detection_history = self.detection_history[-1000:]
            
            # 日次サマリー更新
            self._update_daily_summary(record)
            
        except Exception as e:
            self.logger.error(f"History update failed: {e}")
    
    def _update_daily_summary(self, record: DetectionRecord) -> None:
        """日次サマリー更新"""
        try:
            record_date = datetime.fromisoformat(record.timestamp).date()
            date_str = record_date.isoformat()
            
            if date_str not in self.daily_summaries:
                self.daily_summaries[date_str] = DailyActivitySummary(
                    date=date_str,
                    total_detections=0,
                    detection_sessions=0,
                    active_hours=[],
                    hourly_activity=[],
                    peak_activity_hour="",
                    activity_score=0.0,
                    movement_pattern="unknown",
                    notes=""
                )
            
            summary = self.daily_summaries[date_str]
            summary.total_detections += record.detection_count
            summary.detection_sessions += 1
            
            # 時間別活動更新
            hour = datetime.fromisoformat(record.timestamp).hour
            if hour not in summary.active_hours:
                summary.active_hours.append(hour)
            
        except Exception as e:
            self.logger.error(f"Daily summary update failed: {e}")
    
    def _update_stats(self, original: DetectionRecord, processed: DetectionRecord, 
                     processing_time: float) -> None:
        """統計情報更新"""
        try:
            self.stats.total_processed += 1
            self.stats.total_filtered_out += (original.detection_count - processed.detection_count)
            self.stats.last_processing_time = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Stats update failed: {e}")
    
    def get_daily_summary(self, date: str) -> Optional[DailyActivitySummary]:
        """
        日次サマリー取得
        
        Args:
            date: 日付 (YYYY-MM-DD)
            
        Returns:
            Optional[DailyActivitySummary]: 日次サマリー
        """
        return self.daily_summaries.get(date)
    
    def get_period_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        期間統計取得
        
        Args:
            start_date: 開始日 (YYYY-MM-DD)
            end_date: 終了日 (YYYY-MM-DD)
            
        Returns:
            Dict[str, Any]: 期間統計情報
        """
        try:
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()
            
            # 期間内データフィルタ
            period_records = [
                record for record in self.detection_history
                if start <= datetime.fromisoformat(record.timestamp).date() <= end
            ]
            
            if not period_records:
                return {"error": "No data found for the specified period"}
            
            # 統計計算
            total_detections = sum(record.detection_count for record in period_records)
            total_sessions = len(period_records)
            avg_detections_per_session = total_detections / total_sessions if total_sessions > 0 else 0
            
            # 時間別分布
            hourly_distribution = defaultdict(int)
            for record in period_records:
                hour = datetime.fromisoformat(record.timestamp).hour
                hourly_distribution[hour] += record.detection_count
            
            # 日別分布
            daily_distribution = defaultdict(int)
            for record in period_records:
                date = datetime.fromisoformat(record.timestamp).date().isoformat()
                daily_distribution[date] += record.detection_count
            
            return {
                "period": {"start": start_date, "end": end_date},
                "summary": {
                    "total_detections": total_detections,
                    "total_sessions": total_sessions,
                    "avg_detections_per_session": avg_detections_per_session,
                    "detection_days": len(daily_distribution),
                    "most_active_day": max(daily_distribution.items(), key=lambda x: x[1])[0] if daily_distribution else "",
                    "most_active_hour": max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else 0
                },
                "distributions": {
                    "hourly": dict(hourly_distribution),
                    "daily": dict(daily_distribution)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Period statistics calculation failed: {e}")
            return {"error": str(e)}
    
    def export_data(self, format: str = "csv", date_range: Optional[Tuple[str, str]] = None) -> str:
        """
        データエクスポート
        
        Args:
            format: エクスポート形式 ("csv", "json")
            date_range: 日付範囲 (start_date, end_date)
            
        Returns:
            str: エクスポートファイルパス
        """
        try:
            # データフィルタ
            if date_range:
                start_date, end_date = date_range
                start = datetime.fromisoformat(start_date).date()
                end = datetime.fromisoformat(end_date).date()
                
                export_data = [
                    record for record in self.detection_history
                    if start <= datetime.fromisoformat(record.timestamp).date() <= end
                ]
            else:
                export_data = self.detection_history
            
            # ファイルパス生成
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"detection_export_{timestamp}.{format}"
            filepath = self.output_dir / filename
            
            if format.lower() == "csv":
                self._export_to_csv(export_data, filepath)
            elif format.lower() == "json":
                self._export_to_json(export_data, filepath)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Data exported to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Data export failed: {e}")
            return ""
    
    def _export_to_csv(self, data: List[DetectionRecord], filepath: Path) -> None:
        """CSV形式でエクスポート"""
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # ヘッダ
            writer.writerow([
                'timestamp', 'image_path', 'detection_count', 'processing_time_ms',
                'confidence_threshold', 'model_version', 'detections_json'
            ])
            
            # データ
            for record in data:
                detections_json = json.dumps([asdict(d) for d in record.detections])
                writer.writerow([
                    record.timestamp, record.image_path, record.detection_count,
                    record.processing_time_ms, record.confidence_threshold,
                    record.model_version, detections_json
                ])
    
    def _export_to_json(self, data: List[DetectionRecord], filepath: Path) -> None:
        """JSON形式でエクスポート"""
        export_dict = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "record_count": len(data),
                "processor_stats": asdict(self.stats)
            },
            "records": [asdict(record) for record in data]
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_dict, jsonfile, indent=2, ensure_ascii=False)
    
    def get_processing_stats(self) -> ProcessingStats:
        """処理統計取得"""
        return self.stats
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            # 最終データ保存
            if self.detection_history:
                self.export_data("json")
            
            # キャッシュクリア
            self.detection_history.clear()
            self.daily_summaries.clear()
            
            self.logger.info("Detection processor cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Processor cleanup failed: {e}")


# 使用例・テスト関数
def test_detection_processor():
    """検出処理器のテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 処理設定
    settings = ProcessingSettings(
        min_confidence=0.6,
        enable_duplicate_filter=True
    )
    
    # 処理器作成
    processor = DetectionProcessor(settings)
    
    try:
        # テスト用検出結果作成
        test_detections = [
            DetectionResult(
                x_center=100.0, y_center=150.0, width=50.0, height=40.0,
                confidence=0.85, class_id=0, timestamp=datetime.now().isoformat()
            ),
            DetectionResult(
                x_center=200.0, y_center=250.0, width=60.0, height=45.0,
                confidence=0.75, class_id=0, timestamp=datetime.now().isoformat()
            )
        ]
        
        test_record = DetectionRecord(
            timestamp=datetime.now().isoformat(),
            image_path="test_image.jpg",
            detection_count=len(test_detections),
            detections=test_detections,
            processing_time_ms=150,
            confidence_threshold=0.5,
            model_version="YOLOv8"
        )
        
        # 処理実行
        logger.info("Testing detection processing...")
        processed_record = processor.process_detection_record(test_record)
        
        logger.info(f"Original detections: {test_record.detection_count}")
        logger.info(f"Processed detections: {processed_record.detection_count}")
        
        # 統計表示
        stats = processor.get_processing_stats()
        logger.info(f"Processing stats: {stats}")
        
        # 期間統計テスト
        today = datetime.now().date().isoformat()
        period_stats = processor.get_period_statistics(today, today)
        logger.info(f"Period statistics: {period_stats}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        processor.cleanup()


if __name__ == "__main__":
    test_detection_processor()