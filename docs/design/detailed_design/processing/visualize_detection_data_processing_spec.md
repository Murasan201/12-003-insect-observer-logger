# visualize_detection_data.py 処理説明書

**文書番号**: 12-002-PROC-010
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ
**文書名**: visualize_detection_data.py 処理説明書
**対象ファイル**: `production/visualize_detection_data.py`
**バージョン**: 1.0
**作成日**: 2025-12-25
**作成者**: 開発チーム

---

## 📋 ファイル概要

### 目的
本番環境で記録された昆虫検出ログデータ（CSV形式）を読み込み、時系列グラフや統計情報を生成する可視化スクリプト。長時間ロギングデータの分析・レポート作成に使用される。

### 主要機能
- CSVファイルからの検出データ読み込み
- 時系列検出数グラフ作成
- 累積検出数グラフ作成
- 時間帯別活動パターン棒グラフ作成
- 活動ヒートマップ作成（複数日データ用）
- 統計情報の算出・表示

### 本番環境での使用実績

本スクリプトは本番環境での長時間計測データの可視化に正式採用されています。

| 項目 | 内容 |
|------|------|
| **入力データ** | `production/insect_detection_logs/left_half_detection_log_20250904_210012.csv` |
| **出力グラフ** | `production/insect_detection_logs/left_half_detection_log_20250904_210012_graph.png` |
| **計測時間** | 約9時間（21:00〜翌06:00） |
| **データ件数** | 538レコード |

---

## 🔧 関数・メソッド仕様

### load_csv_data(csv_path)

**概要**: CSVファイルを読み込みDataFrameとして返す

**処理内容**:
1. pandasでCSVファイル読み込み
2. 読み込み件数をコンソール出力
3. エラー時はNoneを返却

**入力インターフェース**:
```python
def load_csv_data(csv_path):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| csv_path | str/Path | ○ | CSVファイルパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| df | DataFrame/None | 読み込んだデータ、エラー時はNone |

---

### process_detection_data(df)

**概要**: 検出データの前処理を行う

**処理内容**:
1. タイムスタンプをdatetime型に変換
2. detection_countを数値型に変換
3. NaN値を0で補完

**入力インターフェース**:
```python
def process_detection_data(df):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| df | DataFrame | ○ | 検出データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| df | DataFrame | 前処理済みデータ |

---

### create_detection_plot(df, output_path, show_plot)

**概要**: 3つのサブプロットからなる検出データグラフを作成

**処理内容**:
1. グラフスタイル設定（seaborn-v0_8-darkgrid）
2. サブプロット1: 検出数時系列グラフ作成
3. サブプロット2: 累積検出数グラフ作成
4. サブプロット3: 時間帯別活動パターン棒グラフ作成（21:00〜06:00）
5. 統計サマリーをタイトルに表示
6. PNG形式で保存（300 DPI）

**入力インターフェース**:
```python
def create_detection_plot(df, output_path=None, show_plot=True):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| df | DataFrame | ○ | 検出データ |
| output_path | str/Path | × | 出力ファイルパス |
| show_plot | bool | × | グラフ表示フラグ（デフォルト: True） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| fig | Figure | matplotlibのFigureオブジェクト |

**出力ファイル名規則**:
- デフォルト: `{CSVファイル名}_graph.png`
- 例: `left_half_detection_log_20250904_210012.csv` → `left_half_detection_log_20250904_210012_graph.png`

---

### create_activity_heatmap(df, output_path, show_plot)

**概要**: 複数日データ用の活動ヒートマップを作成

**処理内容**:
1. 日付×時間のピボットテーブル作成
2. ヒートマップ描画（YlOrRdカラーマップ）
3. カラーバー追加
4. PNG形式で保存

**入力インターフェース**:
```python
def create_activity_heatmap(df, output_path=None, show_plot=True):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| df | DataFrame | ○ | 検出データ |
| output_path | str/Path | × | 出力ファイルパス |
| show_plot | bool | × | グラフ表示フラグ（デフォルト: True） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| fig | Figure/None | Figureオブジェクト、データ不足時はNone |

**出力ファイル名規則**:
- `{ベース名}_heatmap.png`

---

### print_statistics(df)

**概要**: 検出データの統計情報をコンソールに表示

**処理内容**:
1. 総観測回数の算出
2. 総検出数の算出
3. 検出率の算出
4. 平均・最大検出数の算出
5. 観測期間の算出
6. 最も活発な時間帯の特定

**入力インターフェース**:
```python
def print_statistics(df):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| df | DataFrame | ○ | 検出データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | コンソール出力のみ |

---

### main()

**概要**: コマンドライン引数を解析しメイン処理を実行

**処理内容**:
1. コマンドライン引数解析
2. CSVファイル存在確認
3. データ読み込み・前処理
4. 統計情報表示
5. グラフ作成・保存
6. ヒートマップ作成（オプション）

---

## 📥 入力仕様

### CSVファイルフォーマット

| カラム名 | 型 | 必須 | 説明 |
|----------|---|------|------|
| timestamp | str | ○ | ISO 8601形式のタイムスタンプ |
| detection_count | int | ○ | 検出数 |
| detected | int | × | 検出フラグ（0/1） |
| confidence_max | float | × | 最大信頼度 |
| confidence_avg | float | × | 平均信頼度 |
| processing_time_ms | float | × | 処理時間（ミリ秒） |

**入力データ例**:
```csv
timestamp,detected,detection_count,confidence_max,confidence_avg,processing_time_ms
2025-09-04T21:00:12.123456,1,2,0.85,0.78,156.3
2025-09-04T21:01:14.234567,0,0,0.00,0.00,142.1
```

---

## 📤 出力仕様

### グラフ出力

| 項目 | 仕様 |
|------|------|
| フォーマット | PNG |
| 解像度 | 300 DPI |
| サイズ | 14 x 10 インチ |
| ファイル名 | `{入力CSVファイル名}_graph.png` |

### グラフ構成

1. **サブプロット1**: 検出数時系列グラフ
   - X軸: 時刻（HH:MM形式、1時間間隔）
   - Y軸: 検出数
   - スタイル: 折れ線グラフ + 塗りつぶし

2. **サブプロット2**: 累積検出数グラフ
   - X軸: 時刻
   - Y軸: 累積検出数
   - スタイル: 折れ線グラフ + 塗りつぶし

3. **サブプロット3**: 時間帯別活動パターン
   - X軸: 時間帯（21:00〜06:00）
   - Y軸: 検出数合計
   - スタイル: 棒グラフ（最大値を強調表示）
   - 平均値ライン付き

### 統計サマリー（グラフタイトル）
- 総検出数
- 最大検出数
- 平均検出数
- 観測時間

---

## 💻 コマンドライン使用方法

### 基本構文
```bash
python production/visualize_detection_data.py <csv_file> [options]
```

### 引数

| 引数 | 必須 | 説明 |
|------|------|------|
| csv_file | ○ | 入力CSVファイルパス |
| -o, --output | × | 出力画像ファイルパス |
| --no-display | × | グラフを画面表示しない |
| --heatmap | × | ヒートマップも作成 |
| --stats-only | × | 統計情報のみ表示 |

### 使用例

```bash
# 基本的な使用（グラフ表示＋自動保存）
python production/visualize_detection_data.py production/insect_detection_logs/left_half_detection_log_20250904_210012.csv

# 出力ファイル名を指定
python production/visualize_detection_data.py input.csv -o output_graph.png

# 画面表示なしで保存のみ
python production/visualize_detection_data.py input.csv --no-display

# 統計情報のみ表示
python production/visualize_detection_data.py input.csv --stats-only

# ヒートマップも生成
python production/visualize_detection_data.py input.csv --heatmap
```

---

## 📊 本番環境計測データ

### 計測ログファイル

| ファイル | 期間 | レコード数 |
|----------|------|-----------|
| `left_half_detection_log_20250902_220517.csv` | 約8時間 | 478件 |
| `left_half_detection_log_20250903_204658.csv` | 約9時間 | 538件 |
| `left_half_detection_log_20250904_210012.csv` | 約9時間 | 538件 |

### 可視化出力ファイル

| 入力ファイル | 出力ファイル |
|-------------|-------------|
| `left_half_detection_log_20250904_210012.csv` | `left_half_detection_log_20250904_210012_graph.png` |

### データ格納場所
- **ログファイル**: `production/insect_detection_logs/`
- **可視化出力**: `production/insect_detection_logs/`

---

## 🔗 依存関係

### 必須ライブラリ
- pandas
- matplotlib
- numpy

### インポート
```python
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
import sys
import numpy as np
```

---

## 📝 更新履歴

| バージョン | 日付 | 更新内容 |
|-----------|------|---------|
| 1.0 | 2025-12-25 | 初版作成 |

---

*文書番号: 12-002-PROC-010*
*最終更新日: 2025-12-25*
