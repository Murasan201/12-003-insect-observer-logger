"""
データ処理モジュール

時系列検出データの分析・変換・集約処理を行う。
- 時系列データの前処理・クリーニング
- 統計的データ変換
- 異常値検出・補正
- データ集約・サンプリング
- 特徴量抽出
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import json
from scipy import signal, stats, interpolate
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# プロジェクト内モジュール
from models.detection_models import DetectionResult, DetectionRecord
from utils.data_validator import DataValidator


@dataclass
class ProcessingSettings:
    """データ処理設定"""
    # 時系列処理
    resampling_interval: str = "1T"  # 1分間隔
    interpolation_method: str = "linear"  # linear, cubic, nearest
    max_gap_minutes: int = 10  # 最大補間ギャップ（分）
    
    # 異常値処理
    outlier_detection_method: str = "zscore"  # zscore, iqr, isolation
    outlier_threshold: float = 3.0
    outlier_action: str = "interpolate"  # remove, interpolate, clip
    
    # フィルタリング
    apply_smoothing: bool = True
    smoothing_window: int = 5
    smoothing_method: str = "moving_average"  # moving_average, savgol, gaussian
    
    # 正規化
    normalization_method: str = "minmax"  # minmax, standard, robust
    feature_scaling: bool = True
    
    # 集約処理
    aggregation_functions: List[str] = None  # mean, std, min, max, count


@dataclass
class ProcessingStats:
    """処理統計情報"""
    total_records_processed: int = 0
    outliers_detected: int = 0
    outliers_corrected: int = 0
    missing_values_filled: int = 0
    data_points_smoothed: int = 0
    processing_time_seconds: float = 0.0
    data_quality_improvement: float = 0.0
    last_processing_time: str = ""


class DataProcessor:
    """
    データ処理クラス
    
    Features:
    - 時系列データの前処理・クリーニング
    - 異常値検出・補正 (Z-score, IQR, Isolation Forest)
    - データ平滑化・フィルタリング
    - 欠損値補間
    - 統計的特徴量抽出
    - データ正規化・標準化
    """
    
    def __init__(self, settings: Optional[ProcessingSettings] = None):
        """
        データ処理器初期化
        
        Args:
            settings: 処理設定
        """
        self.logger = logging.getLogger(__name__ + '.DataProcessor')
        
        # 設定
        self.settings = settings or ProcessingSettings()
        if self.settings.aggregation_functions is None:
            self.settings.aggregation_functions = ['mean', 'std', 'min', 'max', 'count']
        
        # 統計・状態管理
        self.stats = ProcessingStats()
        
        # データ検証器
        self.validator = DataValidator()
        
        # スケーラー (正規化用)
        self.scalers = {}
        
        # 機械学習ライブラリの可用性チェック
        try:
            from sklearn.ensemble import IsolationForest
            self.isolation_forest_available = True
        except ImportError:
            self.isolation_forest_available = False
            self.logger.warning("sklearn not available for advanced outlier detection")
        
        self.logger.info("Data processor initialized")
    
    def process_detection_data(self, 
                             data: pd.DataFrame,
                             target_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        検出データの包括的処理
        
        Args:
            data: 検出データ
            target_columns: 処理対象カラム（Noneの場合は自動選択）
            
        Returns:
            pd.DataFrame: 処理済みデータ
        """
        try:
            start_time = datetime.now()
            
            if len(data) == 0:
                self.logger.warning("Empty dataset provided")
                return data
            
            # 処理対象カラム決定
            if target_columns is None:
                target_columns = self._auto_select_columns(data)
            
            self.logger.info(f"Processing {len(data)} records with columns: {target_columns}")
            
            # データのコピー作成
            processed_data = data.copy()
            
            # 1. 時系列データ準備
            processed_data = self._prepare_timeseries(processed_data)
            
            # 2. 欠損値処理
            processed_data = self._handle_missing_values(processed_data, target_columns)
            
            # 3. 異常値検出・処理
            processed_data = self._handle_outliers(processed_data, target_columns)
            
            # 4. データ平滑化
            if self.settings.apply_smoothing:
                processed_data = self._apply_smoothing(processed_data, target_columns)
            
            # 5. データ正規化
            if self.settings.feature_scaling:
                processed_data = self._normalize_features(processed_data, target_columns)
            
            # 6. 特徴量計算
            processed_data = self._extract_features(processed_data, target_columns)
            
            # 統計更新
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(len(data), processing_time)
            
            self.logger.info(f"Data processing completed in {processing_time:.2f}s")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")
            return data
    
    def _auto_select_columns(self, data: pd.DataFrame) -> List[str]:
        """処理対象カラム自動選択"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # 検出データでよく使用される重要カラム
        priority_columns = ['x_center', 'y_center', 'width', 'height', 'confidence']
        
        # 優先カラムから存在するもの選択
        selected = [col for col in priority_columns if col in numeric_columns]
        
        # その他の数値カラムも追加
        for col in numeric_columns:
            if col not in selected and col not in ['detection_count', 'processing_time_ms']:
                selected.append(col)
        
        return selected
    
    def _prepare_timeseries(self, data: pd.DataFrame) -> pd.DataFrame:
        """時系列データ準備"""
        try:
            # タイムスタンプカラム確認・変換
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data.sort_values('timestamp').reset_index(drop=True)
                
                # 時系列インデックス設定
                data.set_index('timestamp', inplace=True)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Timeseries preparation failed: {e}")
            return data
    
    def _handle_missing_values(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """欠損値処理"""
        try:
            for column in columns:
                if column not in data.columns:
                    continue
                
                missing_count = data[column].isnull().sum()
                if missing_count == 0:
                    continue
                
                self.logger.debug(f"Handling {missing_count} missing values in {column}")
                
                # 補間方法選択
                if isinstance(data.index, pd.DatetimeIndex):
                    # 時系列データの場合
                    if self.settings.interpolation_method == "linear":
                        data[column] = data[column].interpolate(method='time')
                    else:
                        data[column] = data[column].interpolate(method=self.settings.interpolation_method)
                else:
                    # 通常のデータの場合
                    data[column] = data[column].interpolate(method=self.settings.interpolation_method)
                
                # 端点の欠損値は前後の値で埋める
                data[column] = data[column].fillna(method='bfill').fillna(method='ffill')
                
                self.stats.missing_values_filled += missing_count
            
            return data
            
        except Exception as e:
            self.logger.error(f"Missing value handling failed: {e}")
            return data
    
    def _handle_outliers(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """異常値処理"""
        try:
            for column in columns:
                if column not in data.columns:
                    continue
                
                # 異常値検出
                outlier_mask = self._detect_outliers(data[column])
                outlier_count = outlier_mask.sum()
                
                if outlier_count == 0:
                    continue
                
                self.logger.debug(f"Detected {outlier_count} outliers in {column}")
                self.stats.outliers_detected += outlier_count
                
                # 異常値処理
                if self.settings.outlier_action == "remove":
                    data = data[~outlier_mask]
                elif self.settings.outlier_action == "interpolate":
                    data.loc[outlier_mask, column] = np.nan
                    data[column] = data[column].interpolate()
                    self.stats.outliers_corrected += outlier_count
                elif self.settings.outlier_action == "clip":
                    # 上下限値でクリッピング
                    q01, q99 = data[column].quantile([0.01, 0.99])
                    data[column] = data[column].clip(lower=q01, upper=q99)
                    self.stats.outliers_corrected += outlier_count
            
            return data
            
        except Exception as e:
            self.logger.error(f"Outlier handling failed: {e}")
            return data
    
    def _detect_outliers(self, series: pd.Series) -> pd.Series:
        """異常値検出"""
        try:
            if self.settings.outlier_detection_method == "zscore":
                z_scores = np.abs(stats.zscore(series.dropna()))
                # NaN位置を考慮したマスク作成
                outlier_mask = pd.Series(False, index=series.index)
                valid_indices = series.dropna().index
                outlier_mask[valid_indices] = z_scores > self.settings.outlier_threshold
                return outlier_mask
                
            elif self.settings.outlier_detection_method == "iqr":
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                return (series < lower_bound) | (series > upper_bound)
                
            elif self.settings.outlier_detection_method == "isolation" and self.isolation_forest_available:
                from sklearn.ensemble import IsolationForest
                
                valid_data = series.dropna()
                if len(valid_data) < 10:  # データが少ない場合はZ-scoreを使用
                    return self._detect_outliers_zscore(series)
                
                clf = IsolationForest(contamination=0.1, random_state=42)
                outlier_labels = clf.fit_predict(valid_data.values.reshape(-1, 1))
                
                outlier_mask = pd.Series(False, index=series.index)
                outlier_mask[valid_data.index] = outlier_labels == -1
                return outlier_mask
            else:
                # デフォルトはZ-score
                return self._detect_outliers_zscore(series)
                
        except Exception as e:
            self.logger.error(f"Outlier detection failed: {e}")
            return pd.Series(False, index=series.index)
    
    def _detect_outliers_zscore(self, series: pd.Series) -> pd.Series:
        """Z-score法による異常値検出"""
        z_scores = np.abs(stats.zscore(series.dropna()))
        outlier_mask = pd.Series(False, index=series.index)
        valid_indices = series.dropna().index
        outlier_mask[valid_indices] = z_scores > self.settings.outlier_threshold
        return outlier_mask
    
    def _apply_smoothing(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """データ平滑化"""
        try:
            for column in columns:
                if column not in data.columns:
                    continue
                
                original_data = data[column].copy()
                
                if self.settings.smoothing_method == "moving_average":
                    data[column] = data[column].rolling(
                        window=self.settings.smoothing_window,
                        center=True,
                        min_periods=1
                    ).mean()
                    
                elif self.settings.smoothing_method == "savgol":
                    # Savitzky-Golay フィルタ
                    if len(data) >= self.settings.smoothing_window:
                        window_length = min(self.settings.smoothing_window, len(data))
                        if window_length % 2 == 0:
                            window_length -= 1  # 奇数にする
                        if window_length >= 3:
                            smoothed = signal.savgol_filter(
                                data[column].fillna(method='ffill').fillna(method='bfill'),
                                window_length, 2
                            )
                            data[column] = smoothed
                            
                elif self.settings.smoothing_method == "gaussian":
                    # ガウシアンフィルタ
                    sigma = self.settings.smoothing_window / 3.0
                    data[column] = data[column].rolling(
                        window=self.settings.smoothing_window,
                        center=True,
                        min_periods=1,
                        win_type='gaussian'
                    ).mean(std=sigma)
                
                # 平滑化されたデータポイント数をカウント
                smoothed_points = (~data[column].isnull()).sum() - (~original_data.isnull()).sum()
                self.stats.data_points_smoothed += max(0, smoothed_points)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Data smoothing failed: {e}")
            return data
    
    def _normalize_features(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """特徴量正規化"""
        try:
            for column in columns:
                if column not in data.columns:
                    continue
                
                # スケーラー選択・作成
                if self.settings.normalization_method == "minmax":
                    if column not in self.scalers:
                        self.scalers[column] = MinMaxScaler()
                elif self.settings.normalization_method == "standard":
                    if column not in self.scalers:
                        self.scalers[column] = StandardScaler()
                else:
                    continue
                
                # 正規化実行
                valid_data = data[column].dropna()
                if len(valid_data) > 1:
                    scaler = self.scalers[column]
                    scaled_values = scaler.fit_transform(valid_data.values.reshape(-1, 1)).flatten()
                    
                    # 正規化された値を元の位置に配置
                    data.loc[valid_data.index, f"{column}_normalized"] = scaled_values
            
            return data
            
        except Exception as e:
            self.logger.error(f"Feature normalization failed: {e}")
            return data
    
    def _extract_features(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """特徴量抽出"""
        try:
            # 時系列特徴量
            for column in columns:
                if column not in data.columns:
                    continue
                
                # 移動統計量
                data[f"{column}_rolling_mean"] = data[column].rolling(window=10, min_periods=1).mean()
                data[f"{column}_rolling_std"] = data[column].rolling(window=10, min_periods=1).std()
                
                # 差分特徴量
                data[f"{column}_diff"] = data[column].diff()
                data[f"{column}_diff_abs"] = data[column].diff().abs()
                
                # 累積統計量
                data[f"{column}_cumsum"] = data[column].cumsum()
                data[f"{column}_cummax"] = data[column].cummax()
                data[f"{column}_cummin"] = data[column].cummin()
            
            # 座標系特徴量 (x_center, y_centerが両方存在する場合)
            if 'x_center' in columns and 'y_center' in columns:
                if 'x_center' in data.columns and 'y_center' in data.columns:
                    # 中心からの距離
                    center_x, center_y = 960, 540  # 1920x1080の中心
                    data['distance_from_center'] = np.sqrt(
                        (data['x_center'] - center_x)**2 + (data['y_center'] - center_y)**2
                    )
                    
                    # 移動速度 (時系列の場合)
                    if isinstance(data.index, pd.DatetimeIndex):
                        data['movement_speed'] = np.sqrt(
                            data['x_center'].diff()**2 + data['y_center'].diff()**2
                        ) / data.index.to_series().diff().dt.total_seconds()
                        
                        # 移動方向 (角度)
                        data['movement_angle'] = np.arctan2(
                            data['y_center'].diff(), data['x_center'].diff()
                        ) * 180 / np.pi
            
            return data
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return data
    
    def aggregate_data(self, 
                      data: pd.DataFrame,
                      time_interval: str = "1H",
                      agg_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        データ集約処理
        
        Args:
            data: 集約対象データ
            time_interval: 集約間隔 ("1H", "30T", "1D" など)
            agg_columns: 集約対象カラム
            
        Returns:
            pd.DataFrame: 集約済みデータ
        """
        try:
            if not isinstance(data.index, pd.DatetimeIndex):
                self.logger.error("Aggregation requires datetime index")
                return data
            
            if agg_columns is None:
                agg_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            
            # 集約関数定義
            agg_dict = {}
            for column in agg_columns:
                if column in data.columns:
                    agg_dict[column] = self.settings.aggregation_functions
            
            # リサンプリング実行
            aggregated = data.resample(time_interval).agg(agg_dict)
            
            # カラム名をフラット化
            if isinstance(aggregated.columns, pd.MultiIndex):
                aggregated.columns = ['_'.join(col).strip() for col in aggregated.values]
            
            self.logger.info(f"Data aggregated to {len(aggregated)} intervals")
            return aggregated
            
        except Exception as e:
            self.logger.error(f"Data aggregation failed: {e}")
            return data
    
    def detect_patterns(self, data: pd.DataFrame, 
                       column: str,
                       pattern_type: str = "trend") -> Dict[str, Any]:
        """
        パターン検出
        
        Args:
            data: 分析対象データ
            column: 分析対象カラム
            pattern_type: パターンタイプ ("trend", "seasonality", "anomaly")
            
        Returns:
            Dict[str, Any]: 検出されたパターン情報
        """
        try:
            if column not in data.columns:
                return {"error": f"Column {column} not found"}
            
            series = data[column].dropna()
            if len(series) < 10:
                return {"error": "Insufficient data for pattern detection"}
            
            patterns = {}
            
            if pattern_type == "trend":
                # トレンド検出 (Mann-Kendall test)
                if len(series) >= 3:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(
                        range(len(series)), series.values
                    )
                    patterns.update({
                        "trend_slope": slope,
                        "trend_r_squared": r_value**2,
                        "trend_p_value": p_value,
                        "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
                    })
            
            elif pattern_type == "seasonality":
                # 周期性検出 (autocorrelation)
                if len(series) >= 20:
                    autocorr = []
                    for lag in range(1, min(len(series)//4, 50)):
                        corr = series.autocorr(lag=lag)
                        if not np.isnan(corr):
                            autocorr.append((lag, corr))
                    
                    if autocorr:
                        max_lag, max_corr = max(autocorr, key=lambda x: abs(x[1]))
                        patterns.update({
                            "max_autocorr_lag": max_lag,
                            "max_autocorr_value": max_corr,
                            "seasonality_detected": abs(max_corr) > 0.3
                        })
            
            elif pattern_type == "anomaly":
                # 異常検出
                outlier_mask = self._detect_outliers(series)
                anomaly_count = outlier_mask.sum()
                patterns.update({
                    "anomaly_count": anomaly_count,
                    "anomaly_ratio": anomaly_count / len(series),
                    "anomaly_indices": outlier_mask[outlier_mask].index.tolist()
                })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Pattern detection failed: {e}")
            return {"error": str(e)}
    
    def _update_stats(self, record_count: int, processing_time: float) -> None:
        """統計情報更新"""
        try:
            self.stats.total_records_processed += record_count
            self.stats.processing_time_seconds = processing_time
            self.stats.last_processing_time = datetime.now().isoformat()
            
            # データ品質改善スコア計算 (簡易)
            if self.stats.outliers_detected > 0:
                improvement = self.stats.outliers_corrected / self.stats.outliers_detected
                self.stats.data_quality_improvement = improvement
            
        except Exception as e:
            self.logger.error(f"Stats update failed: {e}")
    
    def get_processing_stats(self) -> ProcessingStats:
        """処理統計取得"""
        return self.stats
    
    def reset_scalers(self) -> None:
        """スケーラーリセット"""
        self.scalers.clear()
        self.logger.debug("Feature scalers reset")
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            self.reset_scalers()
            self.logger.info("Data processor cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Data processor cleanup failed: {e}")


# 使用例・テスト関数
def test_data_processor():
    """データ処理器のテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 処理設定
    settings = ProcessingSettings(
        outlier_detection_method="zscore",
        apply_smoothing=True,
        feature_scaling=True
    )
    
    # 処理器作成
    processor = DataProcessor(settings)
    
    try:
        # テストデータ作成
        dates = pd.date_range('2025-07-28 00:00:00', periods=100, freq='1T')
        test_data = pd.DataFrame({
            'timestamp': dates,
            'x_center': np.random.normal(320, 50, 100) + np.random.normal(0, 5, 100),  # ノイズ追加
            'y_center': np.random.normal(240, 30, 100) + np.random.normal(0, 3, 100),
            'confidence': np.random.uniform(0.5, 1.0, 100),
            'detection_count': np.random.poisson(2, 100)
        })
        
        # 人工的に異常値・欠損値を追加
        test_data.iloc[10, test_data.columns.get_loc('x_center')] = 1000  # 異常値
        test_data.iloc[20, test_data.columns.get_loc('y_center')] = np.nan  # 欠損値
        test_data.iloc[50, test_data.columns.get_loc('confidence')] = np.nan
        
        logger.info(f"Testing with {len(test_data)} data points")
        
        # データ処理実行
        processed_data = processor.process_detection_data(test_data)
        
        logger.info(f"Processing completed:")
        logger.info(f"  - Original columns: {len(test_data.columns)}")
        logger.info(f"  - Processed columns: {len(processed_data.columns)}")
        
        # 集約処理テスト
        if isinstance(processed_data.index, pd.DatetimeIndex):
            aggregated = processor.aggregate_data(processed_data, "10T")
            logger.info(f"Aggregated to {len(aggregated)} time intervals")
        
        # パターン検出テスト
        patterns = processor.detect_patterns(processed_data, 'x_center', 'trend')
        logger.info(f"Trend analysis: {patterns}")
        
        # 統計表示
        stats = processor.get_processing_stats()
        logger.info(f"Processing stats:")
        logger.info(f"  - Records processed: {stats.total_records_processed}")
        logger.info(f"  - Outliers detected: {stats.outliers_detected}")
        logger.info(f"  - Missing values filled: {stats.missing_values_filled}")
        logger.info(f"  - Processing time: {stats.processing_time_seconds:.2f}s")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        processor.cleanup()


if __name__ == "__main__":
    test_data_processor()