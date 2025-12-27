# 長時間ロギング セットアップガイド

本ガイドでは、Raspberry Piカメラを使用して昆虫の長時間観察とログ記録を行うためのセットアップ手順を説明します。

## 対象スクリプト

- `production/production_logging_left_half.py`

## 前提条件

- Raspberry Pi 5（Raspberry Pi OS Bookworm）
- Camera Module 3 または Camera Module 3 Wide
- 前章でトレーニングした学習済みモデル（best.pt）
- [リアルタイム検出テスト セットアップガイド](setup_realtime_detection.md)が完了していること

## セットアップ手順

### 1. プロジェクトディレクトリへ移動

```bash
cd ~/insect-observer
```

### 2. 学習済みモデルの配置

前章でトレーニングした学習済みモデル（best.pt）をweightsディレクトリにコピーします。

```bash
mkdir -p weights
cp /path/to/your/training/runs/detect/train/weights/best.pt ./weights/
```

※ リアルタイム検出テストで既にモデルを配置済みの場合、この手順はスキップできます。

### 3. 仮想環境の作成

Raspberry Pi OSのシステムパッケージ（picamera2、libcamera）を利用するため、`--system-site-packages`オプションを指定して仮想環境を作成します。

```bash
python3 -m venv --system-site-packages venv
```

※ リアルタイム検出テストで既に仮想環境を作成済みの場合、この手順はスキップできます。

### 4. 仮想環境の有効化

```bash
source venv/bin/activate
```

### 5. pipのアップグレード

```bash
pip install --upgrade pip
```

### 6. システム依存パッケージのインストール

一部のPythonパッケージをビルドするためにlibcap開発ヘッダーが必要です。

```bash
sudo apt-get update
sudo apt-get install -y libcap-dev
```

### 7. Pythonライブラリのインストール

ultralyticsパッケージをインストールします。

```bash
pip install ultralytics
```

### 8. インストールの確認

以下のコマンドでライブラリが正しくインポートできることを確認します。

```bash
python3 -c "
from picamera2 import Picamera2
from libcamera import controls
import cv2
import numpy as np
from ultralytics import YOLO
print('All imports successful!')
"
```

## スクリプトの実行

### 基本的な実行方法

```bash
cd production
python3 production_logging_left_half.py
```

デフォルトでは60秒間、10秒間隔で観測を行います。

### コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--model` | モデルファイルのパス | `../weights/best.pt` |
| `--conf` | 検出の信頼度閾値 | `0.3` |
| `--width` | カメラ解像度（幅） | `2304` |
| `--height` | カメラ解像度（高さ） | `1296` |
| `--distance` | ピント距離（cm） | `20.0` |
| `--auto-focus` | オートフォーカスモード | - |
| `--interval` | 観測間隔（秒） | `10` |
| `--duration` | 観測継続時間（秒、0で無制限） | `60` |
| `--save-images` | 検出時に画像を保存 | - |
| `--show-boundary` | 保存画像に境界線を描画 | - |
| `--output-dir` | ログ出力ディレクトリ | `insect_detection_logs/` |
| `--exposure` | 露出補正（-8.0〜8.0） | `-0.5` |
| `--contrast` | コントラスト（0.0〜32.0） | `2.0` |
| `--brightness` | 明るさ（-1.0〜1.0） | `0.0` |

### 実行例

1時間の長時間観測（30秒間隔）：

```bash
python3 production_logging_left_half.py --duration 3600 --interval 30
```

無制限の連続観測（Ctrl+Cで停止）：

```bash
python3 production_logging_left_half.py --duration 0 --interval 10
```

検出時に画像を保存：

```bash
python3 production_logging_left_half.py --save-images --duration 3600
```

オートフォーカスモードで実行：

```bash
python3 production_logging_left_half.py --auto-focus --duration 3600
```

### 操作方法

- `Ctrl+C`: プログラムを安全に終了（ログファイルは保存されます）

## 出力ファイル

### ログディレクトリ

ログファイルは `production/insect_detection_logs/` ディレクトリに保存されます。

### CSVファイル

`left_half_detection_log_YYYYMMDD_HHMMSS.csv` 形式で保存されます。

| カラム名 | 説明 |
|---------|------|
| timestamp | 観測日時（ISO形式） |
| observation_number | 観測番号 |
| detection_count | 検出数 |
| has_detection | 検出有無（True/False） |
| class_names | 検出クラス名（複数の場合は`;`区切り） |
| confidence_values | 信頼度スコア |
| bbox_coordinates | バウンディングボックス座標 |
| center_x, center_y | 検出中心座標 |
| bbox_width, bbox_height | バウンディングボックスサイズ |
| area | 検出エリア面積 |
| detection_area | 検出エリア（left_half） |
| processing_time_ms | 処理時間（ミリ秒） |
| image_saved | 画像保存有無 |
| image_filename | 保存画像ファイル名 |

### メタデータファイル

`left_half_metadata_YYYYMMDD_HHMMSS.json` 形式で保存されます。観測セッションの設定情報が記録されます。
