"""
可視化モジュール

昆虫活動データの可視化・グラフ・チャート生成を行う。
- 時系列グラフ・アクティビティチャート
- 移動軌跡・ヒートマップ
- 統計グラフ・分布図
- ダッシュボード・レポート生成
- インタラクティブ可視化
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
import json

# 可視化ライブラリ
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib/seaborn not available. Install with: pip install matplotlib seaborn")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logging.warning("plotly not available. Install with: pip install plotly")

# プロジェクト内モジュール
from models.activity_models import ActivityMetrics, HourlyActivitySummary, DailyActivitySummary


@dataclass
class VisualizationSettings:
    """可視化設定"""
    # 出力設定
    output_format: str = "png"  # png, jpg, svg, pdf, html
    output_dir: str = "./output/visualizations"
    dpi: int = 300
    figure_size: Tuple[int, int] = (12, 8)
    
    # スタイル設定
    style_theme: str = "seaborn"  # seaborn, ggplot, classic
    color_palette: str = "viridis"  # viridis, plasma, tab10, Set3
    font_family: str = "DejaVu Sans"
    font_size: int = 12
    
    # グラフ固有設定
    show_grid: bool = True
    show_legend: bool = True
    transparency: float = 0.7
    line_width: float = 2.0
    marker_size: float = 6.0
    
    # インタラクティブ設定
    interactive_mode: bool = True
    show_plotly_toolbar: bool = True
    plotly_theme: str = "plotly_white"


class Visualizer:
    """
    可視化クラス
    
    Features:
    - 時系列アクティビティグラフ
    - 移動軌跡・ヒートマップ
    - 統計分布・ボックスプロット
    - 日次・時間別サマリーチャート
    - インタラクティブダッシュボード
    - カスタムレポート生成
    """
    
    def __init__(self, settings: Optional[VisualizationSettings] = None):
        """
        可視化器初期化
        
        Args:
            settings: 可視化設定
        """
        self.logger = logging.getLogger(__name__ + '.Visualizer')
        
        # 設定
        self.settings = settings or VisualizationSettings()
        
        # 出力ディレクトリ作成
        self.output_dir = Path(self.settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 可用性チェック
        self.matplotlib_available = MATPLOTLIB_AVAILABLE
        self.plotly_available = PLOTLY_AVAILABLE
        
        if not (self.matplotlib_available or self.plotly_available):
            self.logger.error("No visualization libraries available")
            return
        
        # matplotlib設定
        if self.matplotlib_available:
            self._setup_matplotlib()
        
        # plotly設定
        if self.plotly_available:
            self._setup_plotly()
        
        self.logger.info("Visualizer initialized")
    
    def _setup_matplotlib(self) -> None:
        """matplotlib設定"""
        try:
            # スタイル設定
            if self.settings.style_theme in plt.style.available:
                plt.style.use(self.settings.style_theme)
            
            # フォント設定
            plt.rcParams['font.family'] = self.settings.font_family
            plt.rcParams['font.size'] = self.settings.font_size
            plt.rcParams['figure.figsize'] = self.settings.figure_size
            plt.rcParams['figure.dpi'] = self.settings.dpi
            
            # 日本語フォント対応 (必要に応じて)
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo']
            
            self.logger.debug("matplotlib configured")
            
        except Exception as e:
            self.logger.error(f"matplotlib setup failed: {e}")
    
    def _setup_plotly(self) -> None:
        """plotly設定"""
        try:
            # デフォルトテーマ設定
            pio.templates.default = self.settings.plotly_theme
            
            self.logger.debug("plotly configured")
            
        except Exception as e:
            self.logger.error(f"plotly setup failed: {e}")
    
    def create_activity_timeline(self, 
                               data: pd.DataFrame,
                               title: str = "昆虫活動タイムライン") -> Optional[str]:
        """
        活動タイムライングラフ作成
        
        Args:
            data: 時系列活動データ
            title: グラフタイトル
            
        Returns:
            Optional[str]: 保存ファイルパス
        """
        if not self.matplotlib_available:
            self.logger.error("matplotlib not available for timeline creation")
            return None
        
        try:
            fig, axes = plt.subplots(3, 1, figsize=self.settings.figure_size, sharex=True)
            
            # データ準備
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                x_data = data['timestamp']
            else:
                x_data = data.index
            
            # 1. 検出数の時系列
            if 'detection_count' in data.columns:
                axes[0].plot(x_data, data['detection_count'], 
                           linewidth=self.settings.line_width, 
                           alpha=self.settings.transparency,
                           color='blue', label='検出数')
                axes[0].fill_between(x_data, data['detection_count'], 
                                   alpha=0.3, color='blue')
                axes[0].set_ylabel('検出数')
                axes[0].set_title('昆虫検出数の推移')
                if self.settings.show_grid:
                    axes[0].grid(True, alpha=0.3)
            
            # 2. 信頼度の推移
            if 'confidence' in data.columns:
                axes[1].scatter(x_data, data['confidence'], 
                              s=self.settings.marker_size**2,
                              alpha=self.settings.transparency,
                              c=data['confidence'], cmap=self.settings.color_palette)
                axes[1].set_ylabel('信頼度')
                axes[1].set_title('検出信頼度の推移')
                axes[1].set_ylim(0, 1)
                if self.settings.show_grid:
                    axes[1].grid(True, alpha=0.3)
            
            # 3. 移動距離 (計算可能な場合)
            if 'x_center' in data.columns and 'y_center' in data.columns:
                movement_distances = self._calculate_movement_for_viz(data)
                if movement_distances:
                    axes[2].plot(x_data[1:], movement_distances, 
                               linewidth=self.settings.line_width,
                               alpha=self.settings.transparency,
                               color='red', label='移動距離')
                    axes[2].set_ylabel('移動距離 (pixels)')
                    axes[2].set_title('移動距離の推移')
                    if self.settings.show_grid:
                        axes[2].grid(True, alpha=0.3)
            
            # 共通設定
            axes[-1].set_xlabel('時刻')
            
            # 時刻軸フォーマット
            if isinstance(x_data.iloc[0], pd.Timestamp):
                axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=2))
                plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45)
            
            plt.suptitle(title, fontsize=self.settings.font_size + 2)
            plt.tight_layout()
            
            # 保存
            filename = f"activity_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.settings.output_format}"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=self.settings.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Activity timeline saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Activity timeline creation failed: {e}")
            return None
    
    def create_movement_heatmap(self, 
                              data: pd.DataFrame,
                              title: str = "昆虫移動ヒートマップ") -> Optional[str]:
        """
        移動軌跡ヒートマップ作成
        
        Args:
            data: 位置データ
            title: グラフタイトル
            
        Returns:
            Optional[str]: 保存ファイルパス
        """
        if not self.matplotlib_available:
            return None
        
        try:
            # 位置データ抽出
            if 'x_center' not in data.columns or 'y_center' not in data.columns:
                self.logger.error("Position data not found for heatmap")
                return None
            
            x_positions = data['x_center'].dropna()
            y_positions = data['y_center'].dropna()
            
            if len(x_positions) == 0:
                self.logger.error("No valid position data")
                return None
            
            # ヒートマップ作成
            fig, ax = plt.subplots(figsize=self.settings.figure_size)
            
            # 2Dヒストグラム
            heatmap, xedges, yedges = np.histogram2d(
                x_positions, y_positions, bins=50,
                range=[[0, 1920], [0, 1080]]  # Full HD resolution
            )
            
            # ヒートマップ表示
            im = ax.imshow(heatmap.T, origin='lower', 
                         extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
                         cmap=self.settings.color_palette, alpha=self.settings.transparency)
            
            # カラーバー
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('検出頻度')
            
            # 設定
            ax.set_xlabel('X座標 (pixels)')
            ax.set_ylabel('Y座標 (pixels)')
            ax.set_title(title)
            
            if self.settings.show_grid:
                ax.grid(True, alpha=0.3)
            
            # 画面境界表示
            screen_rect = Rectangle((0, 0), 1920, 1080, linewidth=2, 
                                  edgecolor='white', facecolor='none', linestyle='--')
            ax.add_patch(screen_rect)
            
            plt.tight_layout()
            
            # 保存
            filename = f"movement_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.settings.output_format}"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=self.settings.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Movement heatmap saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Movement heatmap creation failed: {e}")
            return None
    
    def create_hourly_activity_chart(self, 
                                   hourly_summaries: List[HourlyActivitySummary],
                                   title: str = "時間別活動量") -> Optional[str]:
        """
        時間別活動量チャート作成
        
        Args:
            hourly_summaries: 時間別サマリーリスト
            title: グラフタイトル
            
        Returns:
            Optional[str]: 保存ファイルパス
        """
        if not self.matplotlib_available or not hourly_summaries:
            return None
        
        try:
            # データ準備
            hours = [summary.hour for summary in hourly_summaries]
            detections = [summary.detection_count for summary in hourly_summaries]
            distances = [summary.movement_distance for summary in hourly_summaries]
            
            # グラフ作成
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.settings.figure_size, sharex=True)
            
            # 検出数の棒グラフ
            bars1 = ax1.bar(hours, detections, alpha=self.settings.transparency, 
                           color='skyblue', label='検出数')
            ax1.set_ylabel('検出数')
            ax1.set_title('時間別検出数')
            if self.settings.show_grid:
                ax1.grid(True, alpha=0.3, axis='y')
            
            # 移動距離の棒グラフ
            bars2 = ax2.bar(hours, distances, alpha=self.settings.transparency, 
                           color='lightcoral', label='移動距離')
            ax2.set_ylabel('移動距離 (pixels)')
            ax2.set_xlabel('時刻')
            ax2.set_title('時間別移動距離')
            if self.settings.show_grid:
                ax2.grid(True, alpha=0.3, axis='y')
            
            # X軸設定
            ax2.set_xticks(range(0, 24, 2))
            ax2.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)])
            
            plt.suptitle(title, fontsize=self.settings.font_size + 2)
            plt.tight_layout()
            
            # 保存
            filename = f"hourly_activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.settings.output_format}"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=self.settings.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Hourly activity chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Hourly activity chart creation failed: {e}")
            return None
    
    def create_activity_summary_dashboard(self, 
                                        metrics: ActivityMetrics,
                                        title: str = "活動サマリーダッシュボード") -> Optional[str]:
        """
        活動サマリーダッシュボード作成
        
        Args:
            metrics: 活動量指標
            title: ダッシュボードタイトル
            
        Returns:
            Optional[str]: 保存ファイルパス
        """
        if not self.matplotlib_available:
            return None
        
        try:
            # レイアウト設定
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
            
            # 1. 主要指標（左上）
            ax1 = fig.add_subplot(gs[0, 0])
            metrics_data = [
                metrics.total_detections,
                metrics.total_distance,
                metrics.activity_duration,
                metrics.activity_score * 100
            ]
            metrics_labels = ['検出数', '移動距離\n(pixels)', '活動時間\n(hours)', 'スコア\n(%)']
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            
            bars = ax1.bar(metrics_labels, metrics_data, color=colors, alpha=0.8)
            ax1.set_title('主要指標', fontweight='bold')
            
            # 値をバーに表示
            for bar, value in zip(bars, metrics_data):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.1f}', ha='center', va='bottom')
            
            # 2. 時間別分布（右上）
            ax2 = fig.add_subplot(gs[0, 1:])
            if metrics.temporal_distribution:
                hours = list(metrics.temporal_distribution.keys())
                counts = list(metrics.temporal_distribution.values())
                ax2.plot(hours, counts, marker='o', linewidth=2, markersize=6)
                ax2.fill_between(hours, counts, alpha=0.3)
                ax2.set_xlabel('時刻')
                ax2.set_ylabel('検出数')
                ax2.set_title('時間別検出分布', fontweight='bold')
                ax2.grid(True, alpha=0.3)
            
            # 3. 移動統計（左中）
            ax3 = fig.add_subplot(gs[1, 0])
            if metrics.movement_statistics:
                stats_data = [
                    metrics.movement_statistics.get('mean_distance', 0),
                    metrics.movement_statistics.get('std_distance', 0),
                    metrics.movement_statistics.get('max_distance', 0)
                ]
                stats_labels = ['平均', '標準偏差', '最大']
                
                ax3.bar(stats_labels, stats_data, color='lightblue', alpha=0.8)
                ax3.set_title('移動距離統計', fontweight='bold')
                ax3.set_ylabel('距離 (pixels)')
                
                # 値表示
                for i, (label, value) in enumerate(zip(stats_labels, stats_data)):
                    ax3.text(i, value, f'{value:.1f}', ha='center', va='bottom')
            
            # 4. 行動パターン（右中）
            ax4 = fig.add_subplot(gs[1, 1:])
            if metrics.movement_patterns:
                pattern_text = "\n".join([f"• {pattern.replace('_', ' ').title()}" 
                                        for pattern in metrics.movement_patterns])
                ax4.text(0.1, 0.9, "検出された行動パターン:", fontsize=12, fontweight='bold',
                        transform=ax4.transAxes, verticalalignment='top')
                ax4.text(0.1, 0.7, pattern_text, fontsize=10,
                        transform=ax4.transAxes, verticalalignment='top')
                ax4.set_xlim(0, 1)
                ax4.set_ylim(0, 1)
                ax4.axis('off')
            
            # 5. データ品質・詳細情報（下段）
            ax5 = fig.add_subplot(gs[2, :])
            info_text = f"""
データ品質スコア: {metrics.data_quality_score:.3f}
ピーク活動時間: {metrics.peak_activity_time}
平均時間別活動量: {metrics.avg_activity_per_hour:.1f}
分析日付: {metrics.date}
            """.strip()
            
            ax5.text(0.1, 0.8, "詳細情報", fontsize=12, fontweight='bold',
                    transform=ax5.transAxes)
            ax5.text(0.1, 0.5, info_text, fontsize=10,
                    transform=ax5.transAxes, verticalalignment='top')
            ax5.set_xlim(0, 1)
            ax5.set_ylim(0, 1)
            ax5.axis('off')
            
            # タイトル
            fig.suptitle(f"{title} - {metrics.date}", fontsize=16, fontweight='bold')
            
            # 保存
            filename = f"activity_dashboard_{metrics.date}_{datetime.now().strftime('%H%M%S')}.{self.settings.output_format}"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=self.settings.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Activity dashboard saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Activity dashboard creation failed: {e}")
            return None
    
    def create_interactive_timeline(self, 
                                  data: pd.DataFrame,
                                  title: str = "インタラクティブ活動タイムライン") -> Optional[str]:
        """
        インタラクティブタイムライン作成 (Plotly)
        
        Args:
            data: 時系列データ
            title: グラフタイトル
            
        Returns:
            Optional[str]: 保存ファイルパス
        """
        if not self.plotly_available:
            self.logger.error("plotly not available for interactive visualization")
            return None
        
        try:
            # データ準備
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                x_data = data['timestamp']
            else:
                x_data = data.index
            
            # サブプロット作成
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=('検出数', '信頼度', '移動距離'),
                shared_xaxes=True,
                vertical_spacing=0.1
            )
            
            # 検出数
            if 'detection_count' in data.columns:
                fig.add_trace(
                    go.Scatter(x=x_data, y=data['detection_count'],
                             mode='lines+markers', name='検出数',
                             line=dict(color='blue', width=2),
                             fill='tonexty', fillcolor='rgba(0,0,255,0.3)'),
                    row=1, col=1
                )
            
            # 信頼度
            if 'confidence' in data.columns:
                fig.add_trace(
                    go.Scatter(x=x_data, y=data['confidence'],
                             mode='markers', name='信頼度',
                             marker=dict(color=data['confidence'], 
                                       colorscale='viridis', size=8)),
                    row=2, col=1
                )
            
            # 移動距離
            if 'x_center' in data.columns and 'y_center' in data.columns:
                movement_distances = self._calculate_movement_for_viz(data)
                if movement_distances:
                    fig.add_trace(
                        go.Scatter(x=x_data[1:], y=movement_distances,
                                 mode='lines', name='移動距離',
                                 line=dict(color='red', width=2)),
                        row=3, col=1
                    )
            
            # レイアウト設定
            fig.update_layout(
                title=title,
                height=800,
                showlegend=True,
                template=self.settings.plotly_theme
            )
            
            # 軸ラベル
            fig.update_xaxes(title_text="時刻", row=3, col=1)
            fig.update_yaxes(title_text="検出数", row=1, col=1)
            fig.update_yaxes(title_text="信頼度", row=2, col=1)
            fig.update_yaxes(title_text="移動距離 (pixels)", row=3, col=1)
            
            # 保存
            filename = f"interactive_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            self.logger.info(f"Interactive timeline saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Interactive timeline creation failed: {e}")
            return None
    
    def _calculate_movement_for_viz(self, data: pd.DataFrame) -> List[float]:
        """可視化用移動距離計算"""
        try:
            movements = []
            for i in range(1, len(data)):
                dx = data['x_center'].iloc[i] - data['x_center'].iloc[i-1]
                dy = data['y_center'].iloc[i] - data['y_center'].iloc[i-1]
                distance = np.sqrt(dx**2 + dy**2)
                movements.append(distance)
            return movements
        except Exception as e:
            self.logger.error(f"Movement calculation for visualization failed: {e}")
            return []
    
    def export_visualization_report(self, 
                                  metrics: ActivityMetrics,
                                  data: pd.DataFrame,
                                  hourly_summaries: Optional[List[HourlyActivitySummary]] = None) -> Optional[str]:
        """
        包括的可視化レポート作成
        
        Args:
            metrics: 活動量指標
            data: 時系列データ
            hourly_summaries: 時間別サマリー
            
        Returns:
            Optional[str]: レポートディレクトリパス
        """
        try:
            # レポートディレクトリ作成
            report_dir = self.output_dir / f"report_{metrics.date}_{datetime.now().strftime('%H%M%S')}"
            report_dir.mkdir(exist_ok=True)
            
            generated_files = []
            
            # 1. タイムライン
            timeline_path = self.create_activity_timeline(data, f"活動タイムライン - {metrics.date}")
            if timeline_path:
                generated_files.append(timeline_path)
            
            # 2. ヒートマップ
            heatmap_path = self.create_movement_heatmap(data, f"移動ヒートマップ - {metrics.date}")
            if heatmap_path:
                generated_files.append(heatmap_path)
            
            # 3. ダッシュボード
            dashboard_path = self.create_activity_summary_dashboard(metrics, f"活動サマリー - {metrics.date}")
            if dashboard_path:
                generated_files.append(dashboard_path)
            
            # 4. 時間別チャート
            if hourly_summaries:
                hourly_path = self.create_hourly_activity_chart(hourly_summaries, f"時間別活動 - {metrics.date}")
                if hourly_path:
                    generated_files.append(hourly_path)
            
            # 5. インタラクティブ版
            if self.plotly_available:
                interactive_path = self.create_interactive_timeline(data, f"インタラクティブタイムライン - {metrics.date}")
                if interactive_path:
                    generated_files.append(interactive_path)
            
            # ファイルをレポートディレクトリに移動
            for file_path in generated_files:
                src_path = Path(file_path)
                if src_path.exists():
                    dst_path = report_dir / src_path.name
                    src_path.rename(dst_path)
            
            # レポートサマリー作成
            summary_path = report_dir / "report_summary.json"
            summary_data = {
                "report_date": datetime.now().isoformat(),
                "analysis_date": metrics.date,
                "generated_files": [f.name for f in report_dir.glob("*") if f.is_file()],
                "metrics_summary": {
                    "total_detections": metrics.total_detections,
                    "total_distance": metrics.total_distance,
                    "activity_score": metrics.activity_score,
                    "peak_activity_time": metrics.peak_activity_time
                }
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Visualization report created: {report_dir}")
            return str(report_dir)
            
        except Exception as e:
            self.logger.error(f"Visualization report creation failed: {e}")
            return None
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            # matplotlibキャッシュクリア
            if self.matplotlib_available:
                plt.close('all')
            
            self.logger.info("Visualizer cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Visualizer cleanup failed: {e}")


# 使用例・テスト関数
def test_visualizer():
    """可視化器のテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 可視化設定
    settings = VisualizationSettings(
        output_format="png",
        interactive_mode=True
    )
    
    # 可視化器作成
    visualizer = Visualizer(settings)
    
    try:
        # テストデータ作成
        dates = pd.date_range('2025-07-28 00:00:00', periods=100, freq='10T')
        test_data = pd.DataFrame({
            'timestamp': dates,
            'detection_count': np.random.poisson(3, 100),
            'x_center': np.random.normal(960, 200, 100),
            'y_center': np.random.normal(540, 150, 100),
            'confidence': np.random.uniform(0.6, 1.0, 100)
        })
        
        logger.info(f"Testing with {len(test_data)} data points")
        
        # タイムライン作成
        timeline_path = visualizer.create_activity_timeline(test_data)
        if timeline_path:
            logger.info(f"Timeline created: {timeline_path}")
        
        # ヒートマップ作成
        heatmap_path = visualizer.create_movement_heatmap(test_data)
        if heatmap_path:
            logger.info(f"Heatmap created: {heatmap_path}")
        
        # インタラクティブ版作成
        if visualizer.plotly_available:
            interactive_path = visualizer.create_interactive_timeline(test_data)
            if interactive_path:
                logger.info(f"Interactive timeline created: {interactive_path}")
        
        logger.info("Visualization test completed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        visualizer.cleanup()


if __name__ == "__main__":
    test_visualizer()