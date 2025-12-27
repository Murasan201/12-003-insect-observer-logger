# データ可視化 セットアップガイド

本ガイドでは、長時間ロギングで収集したCSVデータからグラフを生成するためのセットアップ手順を説明します。

## 対象スクリプト

- `production/visualize_detection_data.py`

## 前提条件

- Raspberry Pi 5（Raspberry Pi OS Bookworm）またはPC
- [長時間ロギング セットアップガイド](setup_logging.md)で収集したCSVファイル

## セットアップ手順

### 1. プロジェクトディレクトリへ移動

```bash
cd ~/insect-observer
```

### 2. 仮想環境の作成

Raspberry Pi OSのシステムパッケージを利用するため、`--system-site-packages`オプションを指定して仮想環境を作成します。

```bash
python3 -m venv --system-site-packages venv
```

※ 前のガイドで既に仮想環境を作成済みの場合、この手順はスキップできます。

### 3. 仮想環境の有効化

```bash
source venv/bin/activate
```

### 4. pipのアップグレード

```bash
pip install --upgrade pip
```

### 5. システム依存パッケージのインストール

```bash
sudo apt-get update
sudo apt-get install -y libcap-dev
```

### 6. Pythonライブラリのインストール

ultralyticsパッケージをインストールすると、pandas、matplotlib、numpyなど必要なライブラリが自動的にインストールされます。

```bash
pip install ultralytics
```

### 7. インストールの確認

以下のコマンドでライブラリが正しくインポートできることを確認します。

```bash
python3 -c "
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
print('All imports successful!')
print(f'pandas: {pd.__version__}')
print(f'matplotlib: {plt.matplotlib.__version__}')
"
```

## スクリプトの実行

### 基本的な実行方法

```bash
cd production
python3 visualize_detection_data.py insect_detection_logs/CSVファイル名.csv
```

### コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `csv_file` | 入力CSVファイルのパス（必須） | - |
| `-o`, `--output` | 出力画像ファイルのパス | CSVと同じディレクトリに`_graph.png`を追加 |
| `--no-display` | 画面表示なしで保存のみ | - |
| `--heatmap` | 活動ヒートマップも作成（複数日データ用） | - |
| `--stats-only` | 統計情報のみ表示（グラフ作成なし） | - |

### 実行例

統計情報のみ表示：

```bash
python3 visualize_detection_data.py insect_detection_logs/left_half_detection_log_20250904_210012.csv --stats-only
```

グラフを画像ファイルとして保存（画面表示なし）：

```bash
python3 visualize_detection_data.py insect_detection_logs/left_half_detection_log_20250904_210012.csv --no-display
```

出力ファイル名を指定：

```bash
python3 visualize_detection_data.py insect_detection_logs/left_half_detection_log_20250904_210012.csv -o result.png --no-display
```

ヒートマップも作成（複数日のデータがある場合）：

```bash
python3 visualize_detection_data.py insect_detection_logs/multi_day_log.csv --heatmap --no-display
```

## 出力内容

### 統計情報

コンソールに以下の統計情報が表示されます：

- Total observations: 観察回数の合計
- Total detections: 検出数の合計
- Observations with detections: 昆虫が検出された回数
- Detection rate: 検出率（%）
- Average detections per observation: 観察あたりの平均検出数
- Max detections in single observation: 1回の観察での最大検出数
- Observation period: 観察期間（開始・終了・継続時間）
- Most active hour: 最も活発だった時間帯

### グラフ（3つのサブプロット）

1. **検出数の時系列プロット**: 時間経過に伴う検出数の変化
2. **累積検出数**: 観察開始からの合計検出数の推移
3. **時間帯別活動量**: 1時間単位の棒グラフ（21:00〜06:00）

### ヒートマップ（オプション）

複数日のデータがある場合、日付×時間帯のヒートマップを作成できます。

## CSVファイルの形式

入力CSVファイルには以下のカラムが必要です：

| カラム名 | 必須 | 説明 |
|---------|------|------|
| timestamp | ○ | 観測日時（ISO形式） |
| detection_count | ○ | 検出数 |

その他のカラムは存在しても無視されます。
