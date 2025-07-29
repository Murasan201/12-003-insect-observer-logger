"""
活動量算出モジュール

昆虫の活動量・移動パターンの算出と可視化を行う。
- 検出データの時系列分析
- 移動距離・活動量の算出
- 統計的指標の計算
- 行動パターン分析
- データ品質評価
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import json
from scipy import stats
from scipy.spatial.distance import euclidean

# プロジェクト内モジュール
from models.activity_models import ActivityMetrics, HourlyActivitySummary, DailyActivitySummary
from models.detection_models import DetectionResult, DetectionRecord
from utils.data_validator import DataValidator


@dataclass
class CalculationSettings:
    """活動量算出設定"""
    movement_threshold: float = 5.0  # 最小移動距離 (pixels)
    time_window_minutes: int = 60    # 時間窓 (分)
    outlier_threshold: float = 3.0   # 外れ値除去閾値 (標準偏差)
    smoothing_window: int = 5        # 移動平均ウィンドウ
    min_detection_confidence: float = 0.6  # 最低信頼度
    max_movement_speed: float = 500.0  # 最大移動速度 (pixels/minute)
    enable_outlier_removal: bool = True
    enable_smoothing: bool = True
    screen_resolution: Tuple[int, int] = (1920, 1080)


@dataclass
class CalculationStats:
    """算出統計情報"""
    total_records_processed: int = 0
    valid_movements_calculated: int = 0
    outliers_removed: int = 0
    data_quality_score: float = 0.0
    processing_time_ms: float = 0.0
    last_calculation_time: str = ""
    calculation_errors: int = 0


class ActivityCalculator:
    """
    活動量算出クラス
    
    Features:
    - 時系列データからの移動距離算出
    - 統計的指標計算 (平均・分散・四分位)
    - 活動リズム分析
    - 移動パターン分類
    - 異常活動検出
    - データ品質評価
    """
    
    def __init__(self, 
                 settings: Optional[CalculationSettings] = None,
                 data_dir: str = "./logs"):
        """
        活動量算出器初期化
        
        Args:
            settings: 算出設定
            data_dir: データディレクトリ
        """
        self.logger = logging.getLogger(__name__ + '.ActivityCalculator')
        
        # 設定
        self.settings = settings or CalculationSettings()
        self.data_dir = Path(data_dir)
        
        # 統計・状態管理
        self.stats = CalculationStats()
        
        # データ検証器
        self.validator = DataValidator()
        
        # キャッシュ
        self.movement_cache: Dict[str, List[float]] = {}
        self.activity_cache: Dict[str, ActivityMetrics] = {}
        
        self.logger.info("Activity calculator initialized")
    
    def load_detection_data(self, date: str) -> Optional[pd.DataFrame]:
        """
        検出データ読み込み
        
        Args:
            date: 対象日付 (YYYY-MM-DD)
            
        Returns:
            Optional[pd.DataFrame]: 検出データ
        """
        try:
            # CSVファイルパス生成
            csv_filename = f"detection_log_{date.replace('-', '')}.csv"
            csv_path = self.data_dir / csv_filename
            
            if not csv_path.exists():
                self.logger.warning(f"Detection data not found: {csv_path}")
                return None
            
            # データ読み込み
            df = pd.read_csv(csv_path)
            
            # データ検証
            validation_errors = self.validator.validate_csv_data(df)
            if validation_errors:
                self.logger.warning(f"Data validation issues: {validation_errors}")
            
            # 基本前処理
            df = self._preprocess_data(df)
            
            self.logger.info(f"Loaded {len(df)} detection records for {date}")
            return df
            
        except Exception as e:
            self.logger.error(f"Data loading failed for {date}: {e}")
            return None
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """データ前処理"""
        try:
            # タイムスタンプ変換
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 信頼度フィルタリング
            if 'confidence' in df.columns:
                df = df[df['confidence'] >= self.settings.min_detection_confidence]
            
            # 検出データのみ抽出
            df = df[df['detection_count'] > 0].copy()
            
            # 座標データの存在確認
            required_columns = ['x_center', 'y_center']
            if all(col in df.columns for col in required_columns):
                # 無効座標の除去
                df = df.dropna(subset=required_columns)
                df = df[(df['x_center'] > 0) & (df['y_center'] > 0)]
            
            # 時系列ソート
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            self.logger.debug(f"Preprocessed data: {len(df)} valid records")
            return df
            
        except Exception as e:
            self.logger.error(f"Data preprocessing failed: {e}")
            return df
    
    def calculate_movement_distance(self, data: pd.DataFrame) -> List[float]:
        """
        移動距離算出
        
        Args:
            data: 時系列検出データ
            
        Returns:
            List[float]: 時間別移動距離
        """
        if len(data) < 2:
            return []
        
        try:
            # 前回位置を追加
            data = data.copy()
            data['prev_x'] = data['x_center'].shift(1)
            data['prev_y'] = data['y_center'].shift(1)
            data['time_diff'] = data['timestamp'].diff().dt.total_seconds() / 60.0  # 分単位
            
            # 移動距離計算 (ピタゴラスの定理)
            movements = []
            
            for i in range(1, len(data)):
                row = data.iloc[i]
                
                # 座標差分
                dx = row['x_center'] - row['prev_x']
                dy = row['y_center'] - row['prev_y']
                
                # ユークリッド距離
                distance = np.sqrt(dx**2 + dy**2)
                
                # 時間考慮 (移動速度チェック)
                if row['time_diff'] > 0:
                    speed = distance / row['time_diff']  # pixels/minute
                    if speed > self.settings.max_movement_speed:
                        distance = 0.0  # 異常な移動速度の場合は無効化
                
                # 最小移動距離閾値
                if distance < self.settings.movement_threshold:
                    distance = 0.0
                
                movements.append(distance)
            
            # 外れ値除去
            if self.settings.enable_outlier_removal and len(movements) > 5:
                movements = self._remove_outliers(movements)
            
            # 平滑化
            if self.settings.enable_smoothing and len(movements) > self.settings.smoothing_window:
                movements = self._smooth_data(movements)
            
            self.stats.valid_movements_calculated += len(movements)
            
            return movements
            
        except Exception as e:
            self.logger.error(f"Movement distance calculation failed: {e}")
            return []
    
    def _remove_outliers(self, data: List[float]) -> List[float]:
        """外れ値除去 (Z-score法)"""
        try:
            if len(data) < 3:
                return data
            
            data_array = np.array(data)
            z_scores = np.abs(stats.zscore(data_array))
            threshold = self.settings.outlier_threshold
            
            # 外れ値をNaNに置換
            cleaned_data = data_array.copy()
            outlier_mask = z_scores > threshold
            cleaned_data[outlier_mask] = np.nan
            
            # 線形補間で補完
            if np.any(outlier_mask):
                valid_indices = ~np.isnan(cleaned_data)
                if np.sum(valid_indices) >= 2:
                    cleaned_data = pd.Series(cleaned_data).interpolate().fillna(0).values
                
                outliers_count = np.sum(outlier_mask)
                self.stats.outliers_removed += outliers_count
                self.logger.debug(f"Removed {outliers_count} outliers")
            
            return cleaned_data.tolist()
            
        except Exception as e:
            self.logger.error(f"Outlier removal failed: {e}")
            return data
    
    def _smooth_data(self, data: List[float]) -> List[float]:
        """データ平滑化 (移動平均)"""
        try:
            if len(data) < self.settings.smoothing_window:
                return data
            
            data_series = pd.Series(data)
            smoothed = data_series.rolling(
                window=self.settings.smoothing_window,
                center=True,
                min_periods=1
            ).mean()
            
            return smoothed.tolist()
            
        except Exception as e:
            self.logger.error(f"Data smoothing failed: {e}")
            return data
    
    def calculate_activity_metrics(self, data: pd.DataFrame) -> Optional[ActivityMetrics]:
        """
        活動量指標算出
        
        Args:
            data: 検出データ
            
        Returns:
            Optional[ActivityMetrics]: 活動量指標
        """
        try:
            start_time = datetime.now()
            
            if len(data) == 0:
                return self._create_empty_metrics()
            
            # 移動距離算出
            movements = self.calculate_movement_distance(data)
            
            # 基本統計
            total_detections = len(data)
            total_distance = sum(movements) if movements else 0.0
            
            # 時間解析
            time_analysis = self._analyze_temporal_patterns(data)
            
            # 活動継続時間算出
            activity_duration = self._calculate_activity_duration(data)
            
            # 移動パターン分析
            movement_patterns = self._analyze_movement_patterns(data, movements)
            
            # 活動スコア算出
            activity_score = self._calculate_activity_score(
                total_detections, total_distance, activity_duration, len(movements)
            )
            
            # データ品質評価
            data_quality = self._assess_data_quality(data, movements)
            
            # ActivityMetrics作成
            metrics = ActivityMetrics(
                date=data['timestamp'].dt.date.iloc[0].isoformat(),
                total_detections=total_detections,
                total_distance=round(total_distance, 2),
                avg_activity_per_hour=round(time_analysis['avg_per_hour'], 2),
                peak_activity_time=time_analysis['peak_hour'],
                activity_duration=round(activity_duration, 2),
                movement_patterns=movement_patterns,
                activity_score=round(activity_score, 3),
                movement_statistics={
                    'mean_distance': round(np.mean(movements), 2) if movements else 0.0,
                    'std_distance': round(np.std(movements), 2) if movements else 0.0,
                    'max_distance': round(max(movements), 2) if movements else 0.0,
                    'total_movements': len([m for m in movements if m > 0])
                },
                temporal_distribution=time_analysis['hourly_distribution'],
                data_quality_score=round(data_quality, 3)
            )
            
            # 統計更新
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_stats(processing_time)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Activity metrics calculation failed: {e}")
            self.stats.calculation_errors += 1
            return None
    
    def _create_empty_metrics(self) -> ActivityMetrics:
        """空の活動量指標作成"""
        return ActivityMetrics(
            date=datetime.now().date().isoformat(),
            total_detections=0,
            total_distance=0.0,
            avg_activity_per_hour=0.0,
            peak_activity_time="",
            activity_duration=0.0,
            movement_patterns=["no_activity"],
            activity_score=0.0,
            movement_statistics={},
            temporal_distribution={},
            data_quality_score=0.0
        )
    
    def _analyze_temporal_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """時間パターン解析"""
        try:
            # 時間別集計
            data['hour'] = data['timestamp'].dt.hour
            hourly_counts = data.groupby('hour').size().to_dict()
            
            # 統計値
            total_hours = len(hourly_counts)
            avg_per_hour = len(data) / 24.0  # 24時間での平均
            
            # ピーク時間
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else 0
            peak_hour_str = f"{peak_hour:02d}:00"
            
            return {
                'hourly_distribution': hourly_counts,
                'avg_per_hour': avg_per_hour,
                'peak_hour': peak_hour_str,
                'active_hours': total_hours
            }
            
        except Exception as e:
            self.logger.error(f"Temporal pattern analysis failed: {e}")
            return {
                'hourly_distribution': {},
                'avg_per_hour': 0.0,
                'peak_hour': "",
                'active_hours': 0
            }
    
    def _calculate_activity_duration(self, data: pd.DataFrame) -> float:
        """活動継続時間算出 (時間)"""
        try:
            if len(data) < 2:
                return 0.0
            
            # 時系列でソート
            sorted_data = data.sort_values('timestamp')
            
            # 活動期間の開始・終了
            start_time = sorted_data['timestamp'].iloc[0]
            end_time = sorted_data['timestamp'].iloc[-1]
            
            # 継続時間 (時間単位)
            duration = (end_time - start_time).total_seconds() / 3600.0
            
            return max(0.0, duration)
            
        except Exception as e:
            self.logger.error(f"Activity duration calculation failed: {e}")
            return 0.0
    
    def _analyze_movement_patterns(self, data: pd.DataFrame, movements: List[float]) -> List[str]:
        """移動パターン分析"""
        try:
            patterns = []
            
            if not movements or len(movements) < 5:
                return ["insufficient_data"]
            
            movement_array = np.array(movements)
            
            # 基本統計
            mean_movement = np.mean(movement_array)
            std_movement = np.std(movement_array)
            
            # パターン分類
            if mean_movement < 10:
                patterns.append("low_mobility")
            elif mean_movement > 50:
                patterns.append("high_mobility")
            else:
                patterns.append("moderate_mobility")
            
            # 変動性
            if std_movement < mean_movement * 0.3:
                patterns.append("consistent_movement")
            elif std_movement > mean_movement * 0.8:
                patterns.append("erratic_movement")
            else:
                patterns.append("variable_movement")
            
            # 移動の集中度
            non_zero_movements = movement_array[movement_array > 0]
            if len(non_zero_movements) > 0:
                activity_ratio = len(non_zero_movements) / len(movement_array)
                if activity_ratio > 0.7:
                    patterns.append("continuous_activity")
                elif activity_ratio < 0.3:
                    patterns.append("sporadic_activity")
                else:
                    patterns.append("intermittent_activity")
            
            # 時間的パターン (昼夜の判定)
            data_with_hour = data.copy()
            data_with_hour['hour'] = data_with_hour['timestamp'].dt.hour
            day_activity = len(data_with_hour[(data_with_hour['hour'] >= 6) & (data_with_hour['hour'] < 18)])
            night_activity = len(data_with_hour) - day_activity
            
            if night_activity > day_activity * 1.5:
                patterns.append("nocturnal")
            elif day_activity > night_activity * 1.5:
                patterns.append("diurnal")
            else:
                patterns.append("crepuscular")
            
            return patterns if patterns else ["unknown"]
            
        except Exception as e:
            self.logger.error(f"Movement pattern analysis failed: {e}")
            return ["analysis_error"]
    
    def _calculate_activity_score(self, 
                                detections: int, 
                                distance: float, 
                                duration: float, 
                                movements: int) -> float:
        """
        活動スコア算出 (0-1の正規化値)
        
        Args:
            detections: 総検出数
            distance: 総移動距離
            duration: 活動継続時間
            movements: 有効移動回数
            
        Returns:
            float: 活動スコア
        """
        try:
            # 各指標の正規化 (最大値での除算)
            detection_score = min(1.0, detections / 100.0)  # 100検出を最大として正規化
            distance_score = min(1.0, distance / 1000.0)    # 1000ピクセルを最大として正規化
            duration_score = min(1.0, duration / 12.0)      # 12時間を最大として正規化
            movement_score = min(1.0, movements / 50.0)     # 50移動を最大として正規化
            
            # 重み付き平均
            weights = [0.3, 0.3, 0.2, 0.2]  # [検出数, 移動距離, 継続時間, 移動回数]
            scores = [detection_score, distance_score, duration_score, movement_score]
            
            activity_score = sum(w * s for w, s in zip(weights, scores))
            
            return max(0.0, min(1.0, activity_score))
            
        except Exception as e:
            self.logger.error(f"Activity score calculation failed: {e}")
            return 0.0
    
    def _assess_data_quality(self, data: pd.DataFrame, movements: List[float]) -> float:
        """
        データ品質評価 (0-1)
        
        Args:
            data: 検出データ
            movements: 移動距離データ
            
        Returns:
            float: 品質スコア
        """
        try:
            quality_factors = []
            
            # 1. データ完整性
            required_columns = ['timestamp', 'x_center', 'y_center', 'confidence']
            completeness = sum(1 for col in required_columns if col in data.columns) / len(required_columns)
            quality_factors.append(completeness)
            
            # 2. 時間的均等性 (データポイントの時間分布)
            if len(data) > 1:
                time_intervals = data['timestamp'].diff().dt.total_seconds().dropna()
                time_consistency = 1.0 - (np.std(time_intervals) / np.mean(time_intervals)) if np.mean(time_intervals) > 0 else 0.0
                quality_factors.append(max(0.0, min(1.0, time_consistency)))
            else:
                quality_factors.append(0.0)
            
            # 3. 信頼度分布
            if 'confidence' in data.columns:
                mean_confidence = data['confidence'].mean()
                quality_factors.append(mean_confidence)
            else:
                quality_factors.append(0.5)
            
            # 4. 移動データの妥当性
            if movements:
                valid_movements = len([m for m in movements if 0 < m < 200])  # 妥当な範囲
                movement_quality = valid_movements / len(movements)
                quality_factors.append(movement_quality)
            else:
                quality_factors.append(0.0)
            
            # 5. 外れ値の少なさ
            outlier_penalty = self.stats.outliers_removed / max(1, len(movements)) if movements else 0
            outlier_quality = max(0.0, 1.0 - outlier_penalty)
            quality_factors.append(outlier_quality)
            
            # 総合品質スコア
            overall_quality = np.mean(quality_factors)
            
            return max(0.0, min(1.0, overall_quality))
            
        except Exception as e:
            self.logger.error(f"Data quality assessment failed: {e}")
            return 0.0
    
    def generate_hourly_summaries(self, data: pd.DataFrame) -> List[HourlyActivitySummary]:
        """時間別サマリー生成"""
        try:
            summaries = []
            
            # 時間別グループ化
            data['hour'] = data['timestamp'].dt.hour
            grouped = data.groupby('hour')
            
            for hour, hour_data in grouped:
                # 移動距離算出
                movements = self.calculate_movement_distance(hour_data)
                
                # サマリー作成
                summary = HourlyActivitySummary(
                    hour=hour,
                    detection_count=len(hour_data),
                    movement_distance=sum(movements) if movements else 0.0,
                    avg_confidence=hour_data['confidence'].mean() if 'confidence' in hour_data.columns else 0.0,
                    activity_level=self._classify_activity_level(len(hour_data), sum(movements) if movements else 0.0)
                )
                
                summaries.append(summary)
            
            return sorted(summaries, key=lambda x: x.hour)
            
        except Exception as e:
            self.logger.error(f"Hourly summary generation failed: {e}")
            return []
    
    def _classify_activity_level(self, detections: int, distance: float) -> str:
        """活動レベル分類"""
        # 簡易分類ロジック
        if detections == 0:
            return "none"
        elif detections < 5 and distance < 50:
            return "low"
        elif detections < 15 and distance < 200:
            return "medium"
        else:
            return "high"
    
    def _update_stats(self, processing_time: float) -> None:
        """統計情報更新"""
        try:
            self.stats.total_records_processed += 1
            self.stats.processing_time_ms = processing_time
            self.stats.last_calculation_time = datetime.now().isoformat()
            
            # データ品質スコア更新 (移動平均)
            if hasattr(self, '_recent_quality_scores'):
                self._recent_quality_scores.append(self.stats.data_quality_score)
                if len(self._recent_quality_scores) > 10:
                    self._recent_quality_scores = self._recent_quality_scores[-10:]
                self.stats.data_quality_score = np.mean(self._recent_quality_scores)
            else:
                self._recent_quality_scores = [self.stats.data_quality_score]
            
        except Exception as e:
            self.logger.error(f"Stats update failed: {e}")
    
    def get_calculation_stats(self) -> CalculationStats:
        """算出統計取得"""
        return self.stats
    
    def clear_cache(self) -> None:
        """キャッシュクリア"""
        self.movement_cache.clear()
        self.activity_cache.clear()
        self.logger.debug("Activity calculator cache cleared")
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            self.clear_cache()
            self.logger.info("Activity calculator cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Activity calculator cleanup failed: {e}")


# 使用例・テスト関数
def test_activity_calculator():
    """活動量算出器のテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 算出設定
    settings = CalculationSettings(
        movement_threshold=5.0,
        outlier_threshold=3.0,
        enable_outlier_removal=True
    )
    
    # 算出器作成
    calculator = ActivityCalculator(settings)
    
    try:
        # テストデータ作成
        test_data = pd.DataFrame({
            'timestamp': pd.date_range('2025-07-28 00:00:00', periods=24, freq='H'),
            'detection_count': [1] * 24,
            'x_center': np.random.normal(320, 50, 24),
            'y_center': np.random.normal(240, 30, 24),
            'confidence': np.random.uniform(0.6, 1.0, 24)
        })
        
        logger.info(f"Testing with {len(test_data)} data points")
        
        # 移動距離算出テスト
        movements = calculator.calculate_movement_distance(test_data)
        logger.info(f"Calculated {len(movements)} movements")
        logger.info(f"Total distance: {sum(movements):.2f} pixels")
        
        # 活動量指標算出テスト
        metrics = calculator.calculate_activity_metrics(test_data)
        if metrics:
            logger.info(f"Activity metrics calculated:")
            logger.info(f"  - Total detections: {metrics.total_detections}")
            logger.info(f"  - Total distance: {metrics.total_distance}")
            logger.info(f"  - Activity score: {metrics.activity_score}")
            logger.info(f"  - Movement patterns: {metrics.movement_patterns}")
            logger.info(f"  - Peak activity: {metrics.peak_activity_time}")
        
        # 時間別サマリーテスト
        hourly_summaries = calculator.generate_hourly_summaries(test_data)
        logger.info(f"Generated {len(hourly_summaries)} hourly summaries")
        
        # 統計表示
        stats = calculator.get_calculation_stats()
        logger.info(f"Calculation stats: processed={stats.total_records_processed}, "
                   f"movements={stats.valid_movements_calculated}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        calculator.cleanup()


if __name__ == "__main__":
    test_activity_calculator()