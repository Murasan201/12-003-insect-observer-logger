#!/usr/bin/env python3
"""
検出データ可視化スクリプト
CSVファイルから時間vs検出数のグラフを生成
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
import sys
import numpy as np

def load_csv_data(csv_path):
    """CSVファイルを読み込み"""
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} records from {csv_path}")
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def process_detection_data(df):
    """検出データを処理"""
    # タイムスタンプをdatetime型に変換
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 検出数が文字列の場合は数値に変換
    if df['detection_count'].dtype == 'object':
        df['detection_count'] = pd.to_numeric(df['detection_count'], errors='coerce')
    
    # NaNを0で埋める
    df['detection_count'] = df['detection_count'].fillna(0)
    
    return df

def create_detection_plot(df, output_path=None, show_plot=True):
    """検出数の時系列グラフを作成"""
    
    # 図の設定
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10))
    
    # 1. 検出数の時系列プロット
    ax1.plot(df['timestamp'], df['detection_count'], 
             marker='o', markersize=4, linewidth=1.5, 
             color='#2E86AB', label='Detection Count')
    ax1.fill_between(df['timestamp'], 0, df['detection_count'], 
                     alpha=0.3, color='#2E86AB')
    
    ax1.set_xlabel('Time', fontsize=12)
    ax1.set_ylabel('Detection Count', fontsize=12)
    ax1.set_title('Insect Detection Over Time', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')
    
    # X軸の時間フォーマット
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 2. 累積検出数
    df['cumulative_detections'] = df['detection_count'].cumsum()
    ax2.plot(df['timestamp'], df['cumulative_detections'], 
             linewidth=2, color='#A23B72', label='Cumulative Detections')
    ax2.fill_between(df['timestamp'], 0, df['cumulative_detections'], 
                     alpha=0.3, color='#A23B72')
    
    ax2.set_xlabel('Time', fontsize=12)
    ax2.set_ylabel('Cumulative Count', fontsize=12)
    ax2.set_title('Cumulative Detection Count', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left')
    
    # X軸の時間フォーマット
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 3. 時間帯別の活動量（1時間単位）
    df['hour'] = df['timestamp'].dt.hour
    hourly_activity = df.groupby('hour')['detection_count'].sum()
    
    # 24時間分のデータを準備（存在しない時間は0で埋める）
    all_hours = pd.Series(index=range(24), data=0)
    all_hours.update(hourly_activity)
    
    # 21:00スタート、06:00終了になるように時間軸を再配置
    # 21,22,23,0,1,2,3,4,5,6の順番に並び替え（9時間）
    start_hour = 21
    end_hour = 7  # 7時間目は含めない（0-6時まで）
    
    # 21,22,23,0,1,2,3,4,5,6の順番
    reordered_hours = list(range(start_hour, 24)) + list(range(0, end_hour))
    reordered_values = [all_hours[h] for h in reordered_hours]
    reordered_labels = [f'{h:02d}:00' for h in reordered_hours]
    
    # 9時間分のデータでグラフ作成
    bars = ax3.bar(range(len(reordered_hours)), reordered_values, 
                   color='#F18F01', edgecolor='#C73E1D', linewidth=1.5, alpha=0.7)
    
    # 最大値のバーを強調
    max_val = max(reordered_values)
    for i, val in enumerate(reordered_values):
        if val == max_val:
            bars[i].set_color('#C73E1D')
            break
    
    ax3.set_xlabel('Hour of Day', fontsize=12)
    ax3.set_ylabel('Total Detections', fontsize=12)
    ax3.set_title('Activity Pattern by Hour (21:00 - 06:00)', fontsize=14, fontweight='bold')
    ax3.set_xticks(range(len(reordered_hours)))
    ax3.set_xticklabels(reordered_labels, rotation=45, ha='right')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 平均値ラインを追加
    mean_val = np.mean(reordered_values)
    ax3.axhline(y=mean_val, color='red', linestyle='--', alpha=0.5, label=f'Average: {mean_val:.1f}')
    ax3.legend(loc='upper right')
    
    # レイアウト調整
    plt.tight_layout()
    
    # 統計情報を追加
    total_detections = df['detection_count'].sum()
    max_detections = df['detection_count'].max()
    avg_detections = df['detection_count'].mean()
    observation_duration = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
    
    fig.suptitle(f'Total: {total_detections:.0f} detections | Max: {max_detections:.0f} | '
                f'Avg: {avg_detections:.2f} | Duration: {observation_duration:.1f} hours',
                fontsize=11, y=1.02)
    
    # ファイル保存
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Graph saved to: {output_path}")
    
    # 表示
    if show_plot:
        plt.show()
    
    return fig

def create_activity_heatmap(df, output_path=None, show_plot=True):
    """活動ヒートマップを作成（オプション）"""
    
    # 日付と時間を分離
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    
    # 日付×時間のピボットテーブル作成
    pivot_data = df.pivot_table(values='detection_count', 
                                index='hour', 
                                columns='date', 
                                aggfunc='sum',
                                fill_value=0)
    
    if pivot_data.empty or pivot_data.shape[1] == 1:
        print("Not enough data for heatmap (need multiple days)")
        return None
    
    # ヒートマップ作成
    fig, ax = plt.subplots(figsize=(12, 8))
    
    im = ax.imshow(pivot_data.values, cmap='YlOrRd', aspect='auto')
    
    # 軸設定
    ax.set_xticks(range(pivot_data.shape[1]))
    ax.set_xticklabels([str(d) for d in pivot_data.columns], rotation=45, ha='right')
    ax.set_yticks(range(24))
    ax.set_yticklabels([f'{h:02d}:00' for h in range(24)])
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Hour of Day', fontsize=12)
    ax.set_title('Activity Heatmap', fontsize=14, fontweight='bold')
    
    # カラーバー追加
    plt.colorbar(im, ax=ax, label='Detection Count')
    
    plt.tight_layout()
    
    if output_path:
        heatmap_path = output_path.replace('.png', '_heatmap.png')
        plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
        print(f"Heatmap saved to: {heatmap_path}")
    
    if show_plot:
        plt.show()
    
    return fig

def print_statistics(df):
    """統計情報を表示"""
    print("\n" + "="*50)
    print("Detection Statistics")
    print("="*50)
    
    total_observations = len(df)
    total_detections = df['detection_count'].sum()
    detections_with_insects = (df['detection_count'] > 0).sum()
    detection_rate = (detections_with_insects / total_observations * 100) if total_observations > 0 else 0
    
    print(f"Total observations: {total_observations}")
    print(f"Total detections: {int(total_detections)}")
    print(f"Observations with detections: {detections_with_insects}")
    print(f"Detection rate: {detection_rate:.1f}%")
    print(f"Average detections per observation: {df['detection_count'].mean():.2f}")
    print(f"Max detections in single observation: {int(df['detection_count'].max())}")
    
    # 時間範囲
    if not df.empty:
        start_time = df['timestamp'].min()
        end_time = df['timestamp'].max()
        duration = (end_time - start_time).total_seconds() / 3600
        print(f"\nObservation period:")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")
        print(f"  Duration: {duration:.1f} hours")
    
    # 最も活発な時間帯
    if 'hour' not in df.columns:
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    
    hourly_activity = df.groupby('hour')['detection_count'].sum()
    if not hourly_activity.empty:
        most_active_hour = hourly_activity.idxmax()
        print(f"\nMost active hour: {most_active_hour:02d}:00-{(most_active_hour+1)%24:02d}:00")
        print(f"  Detections in this hour: {int(hourly_activity.max())}")
    
    print("="*50)

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Visualize insect detection data from CSV files"
    )
    
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('-o', '--output', default=None, 
                       help='Output image file path (PNG format)')
    parser.add_argument('--no-display', action='store_true',
                       help='Do not display the plot (only save)')
    parser.add_argument('--heatmap', action='store_true',
                       help='Also create activity heatmap (for multi-day data)')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only show statistics without plotting')
    
    args = parser.parse_args()
    
    # CSVファイル確認
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    # データ読み込み
    df = load_csv_data(csv_path)
    if df is None or df.empty:
        print("Error: No data to process")
        sys.exit(1)
    
    # データ処理
    df = process_detection_data(df)
    
    # 統計情報表示
    print_statistics(df)
    
    if args.stats_only:
        return
    
    # 出力パス設定
    if args.output:
        output_path = Path(args.output)
    else:
        # デフォルトの出力パス（CSVと同じディレクトリ）
        output_path = csv_path.parent / f"{csv_path.stem}_graph.png"
    
    # グラフ作成
    show_plot = not args.no_display
    create_detection_plot(df, output_path, show_plot)
    
    # ヒートマップ作成（オプション）
    if args.heatmap:
        create_activity_heatmap(df, output_path, show_plot)
    
    print("\nVisualization complete!")

if __name__ == "__main__":
    main()