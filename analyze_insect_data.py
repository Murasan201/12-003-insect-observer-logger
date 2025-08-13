#!/usr/bin/env python3
"""
昆虫検出データ分析ユーティリティ
test_insect_detection.pyで収集したデータを分析・可視化

機能:
- 検出ログの統計分析
- 活動パターンの可視化
- 検出密度の時系列グラフ
- 日次・時間別レポート生成
"""

import argparse
import sys
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np


def load_detection_data(log_dir="insect_detection_logs", date=None):
    """
    検出ログデータを読み込み
    
    Args:
        log_dir: ログディレクトリ
        date: 分析対象日付 (YYYY-MM-DD形式、Noneの場合は最新)
        
    Returns:
        pandas.DataFrame: 検出データ
    """
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"エラー: ログディレクトリが見つかりません: {log_path}")
        return None
    
    # 日付が指定されていない場合は最新のファイルを使用
    if date is None:
        csv_files = list(log_path.glob("insect_detection_*.csv"))
        if not csv_files:
            print(f"エラー: CSVログファイルが見つかりません")
            return None
        
        # 最新のファイルを選択
        latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
        print(f"最新のログファイル使用: {latest_file}")
    else:
        # 指定された日付のファイルを使用
        date_str = date.replace('-', '')
        csv_file = log_path / f"insect_detection_{date_str}.csv"
        if not csv_file.exists():
            print(f"エラー: 指定された日付のログファイルが見つかりません: {csv_file}")
            return None
        latest_file = csv_file
        print(f"指定日のログファイル使用: {latest_file}")
    
    try:
        # CSVデータを読み込み
        df = pd.read_csv(latest_file)
        
        # タイムスタンプを datetime 型に変換
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 時間関連の列を追加
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['date'] = df['timestamp'].dt.date
        
        print(f"✓ データ読み込み完了: {len(df)} レコード")
        return df
        
    except Exception as e:
        print(f"エラー: データの読み込みに失敗: {e}")
        return None


def analyze_detection_statistics(df):
    """検出統計の分析"""
    
    print("\n" + "=" * 60)
    print("📊 昆虫検出統計分析")
    print("=" * 60)
    
    # 基本統計
    total_frames = len(df)
    detection_frames = df['detected'].sum()
    total_beetles = df['beetle_count'].sum()
    detection_rate = (detection_frames / total_frames) * 100
    
    print(f"総フレーム数: {total_frames}")
    print(f"検出フレーム数: {detection_frames}")
    print(f"検出率: {detection_rate:.1f}%")
    print(f"総昆虫数: {total_beetles}")
    print(f"平均処理時間: {df['processing_time_ms'].mean():.1f}ms")
    
    # 信頼度統計
    detected_data = df[df['detected'] == 1]
    if len(detected_data) > 0:
        print(f"\n🎯 検出品質:")
        print(f"最高信頼度: {detected_data['confidence_max'].max():.3f}")
        print(f"平均信頼度: {detected_data['confidence_avg'].mean():.3f}")
        print(f"最低信頼度: {detected_data['confidence_max'].min():.3f}")
    
    # 時間別統計
    hourly_stats = df.groupby('hour').agg({
        'detected': 'sum',
        'beetle_count': 'sum',
        'processing_time_ms': 'mean'
    }).round(2)
    
    print(f"\n⏰ 時間別活動:")
    most_active_hour = hourly_stats['beetle_count'].idxmax()
    print(f"最も活発な時間: {most_active_hour}時 ({hourly_stats.loc[most_active_hour, 'beetle_count']} 匹)")
    
    return {
        'total_frames': total_frames,
        'detection_frames': detection_frames,
        'detection_rate': detection_rate,
        'total_beetles': total_beetles,
        'hourly_stats': hourly_stats
    }


def plot_activity_timeline(df, output_dir="analysis_output"):
    """活動タイムライン可視化"""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 図のセットアップ
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('昆虫活動分析レポート', fontsize=16, fontweight='bold')
    
    # 1. 時系列検出グラフ
    ax1.plot(df['timestamp'], df['beetle_count'], 'o-', markersize=3, linewidth=1)
    ax1.set_title('昆虫検出数の時系列変化')
    ax1.set_ylabel('検出数')
    ax1.grid(True, alpha=0.3)
    
    # 2. 時間別集計
    hourly_data = df.groupby('hour')['beetle_count'].sum()
    ax2.bar(hourly_data.index, hourly_data.values, alpha=0.7, color='orange')
    ax2.set_title('時間別昆虫検出数')
    ax2.set_xlabel('時刻')
    ax2.set_ylabel('総検出数')
    ax2.set_xticks(range(0, 24, 2))
    ax2.grid(True, alpha=0.3)
    
    # 3. 処理時間
    ax3.plot(df['timestamp'], df['processing_time_ms'], 'g-', alpha=0.6, linewidth=1)
    ax3.set_title('処理時間の推移')
    ax3.set_xlabel('時刻')
    ax3.set_ylabel('処理時間 (ms)')
    ax3.grid(True, alpha=0.3)
    
    # 時刻軸の書式設定
    for ax in [ax1, ax3]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    # ファイル保存
    output_file = output_path / f"insect_activity_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📈 活動分析グラフを保存: {output_file}")
    
    return output_file


def generate_detection_heatmap(df, output_dir="analysis_output"):
    """検出密度ヒートマップ生成"""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 時間と分のグリッドでヒートマップデータを作成
    # 10分間隔で集計
    df['minute_bin'] = (df['minute'] // 10) * 10
    
    # ピボットテーブル作成
    heatmap_data = df.groupby(['hour', 'minute_bin'])['beetle_count'].sum().unstack(fill_value=0)
    
    # ヒートマップを描画
    fig, ax = plt.subplots(figsize=(12, 8))
    
    im = ax.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
    
    # 軸設定
    ax.set_xticks(range(len(heatmap_data.columns)))
    ax.set_xticklabels([f"{x:02d}" for x in heatmap_data.columns])
    ax.set_yticks(range(len(heatmap_data.index)))
    ax.set_yticklabels([f"{x:02d}:00" for x in heatmap_data.index])
    
    ax.set_xlabel('分 (10分間隔)')
    ax.set_ylabel('時刻')
    ax.set_title('昆虫検出密度ヒートマップ')
    
    # カラーバー
    cbar = plt.colorbar(im)
    cbar.set_label('検出数')
    
    # 数値を表示
    for i in range(len(heatmap_data.index)):
        for j in range(len(heatmap_data.columns)):
            value = heatmap_data.values[i, j]
            if value > 0:
                ax.text(j, i, str(int(value)), ha="center", va="center", color="black", fontweight='bold')
    
    plt.tight_layout()
    
    # ファイル保存
    output_file = output_path / f"insect_detection_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"🔥 検出密度ヒートマップを保存: {output_file}")
    
    return output_file


def generate_report(df, stats, output_dir="analysis_output"):
    """分析レポート生成"""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # レポートファイル
    report_file = output_path / f"insect_detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 昆虫検出分析レポート\n\n")
        f.write(f"**生成日時:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
        
        # 基本統計
        f.write("## 📊 基本統計\n\n")
        f.write(f"- **総フレーム数:** {stats['total_frames']}\n")
        f.write(f"- **検出フレーム数:** {stats['detection_frames']}\n")
        f.write(f"- **検出率:** {stats['detection_rate']:.1f}%\n")
        f.write(f"- **総昆虫数:** {stats['total_beetles']}\n\n")
        
        # 時間別統計
        f.write("## ⏰ 時間別活動統計\n\n")
        f.write("| 時刻 | 検出回数 | 昆虫数 | 平均処理時間(ms) |\n")
        f.write("|------|----------|--------|------------------|\n")
        
        for hour, row in stats['hourly_stats'].iterrows():
            f.write(f"| {hour:02d}:00 | {row['detected']} | {row['beetle_count']} | {row['processing_time_ms']:.1f} |\n")
        
        f.write("\n")
        
        # 詳細分析
        if stats['total_beetles'] > 0:
            detected_data = df[df['detected'] == 1]
            
            f.write("## 🎯 検出品質分析\n\n")
            f.write(f"- **最高信頼度:** {detected_data['confidence_max'].max():.3f}\n")
            f.write(f"- **平均信頼度:** {detected_data['confidence_avg'].mean():.3f}\n")
            f.write(f"- **最低信頼度:** {detected_data['confidence_max'].min():.3f}\n\n")
            
            # 活動パターン分析
            most_active_hour = stats['hourly_stats']['beetle_count'].idxmax()
            f.write("## 🪲 活動パターン\n\n")
            f.write(f"- **最も活発な時間帯:** {most_active_hour}:00時\n")
            f.write(f"- **ピーク時の検出数:** {stats['hourly_stats'].loc[most_active_hour, 'beetle_count']}\n")
        
        f.write("\n## 📈 生成ファイル\n\n")
        f.write("- 活動分析グラフ: `insect_activity_analysis_*.png`\n")
        f.write("- 検出密度ヒートマップ: `insect_detection_heatmap_*.png`\n")
        f.write("- このレポート: `insect_detection_report_*.md`\n")
    
    print(f"📋 分析レポートを保存: {report_file}")
    return report_file


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="昆虫検出データ分析ユーティリティ"
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        default='insect_detection_logs',
        help='ログディレクトリのパス'
    )
    
    parser.add_argument(
        '--date',
        type=str,
        help='分析対象日付 (YYYY-MM-DD形式、未指定の場合は最新)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='analysis_output',
        help='出力ディレクトリ'
    )
    
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='グラフ生成をスキップ'
    )
    
    args = parser.parse_args()
    
    # データ読み込み
    df = load_detection_data(args.log_dir, args.date)
    if df is None:
        sys.exit(1)
    
    # 統計分析
    stats = analyze_detection_statistics(df)
    
    # グラフ生成
    if not args.no_plots:
        try:
            plot_activity_timeline(df, args.output_dir)
            generate_detection_heatmap(df, args.output_dir)
        except Exception as e:
            print(f"警告: グラフ生成に失敗: {e}")
    
    # レポート生成
    generate_report(df, stats, args.output_dir)
    
    print(f"\n✅ 分析完了")


if __name__ == "__main__":
    main()