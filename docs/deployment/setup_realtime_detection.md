# リアルタイム検出テスト セットアップガイド

本ガイドでは、学習済みYOLOv8モデルを使用してRaspberry Piカメラでリアルタイム昆虫検出を行うためのセットアップ手順を説明します。

## 対象スクリプト

- `production/production_camera_left_half_realtime.py`

## 前提条件

- Raspberry Pi 5（Raspberry Pi OS Bookworm）
- Raspberry Pi カメラモジュール V3 NoIR（赤外線対応カメラ）
- IR LEDリングライト 850nm FRS5CS（夜間照明用）
- 前章でトレーニングした学習済みモデル（best.pt）

## セットアップ手順

### 1. プロジェクトディレクトリの作成

```bash
mkdir -p ~/insect-observer
cd ~/insect-observer
```

### 2. 学習済みモデルの配置

前章でトレーニングした学習済みモデル（best.pt）をweightsディレクトリにコピーします。

```bash
mkdir -p weights
cp /path/to/your/training/runs/detect/train/weights/best.pt ./weights/
```

※ `/path/to/your/training/` は実際のトレーニング結果の保存先に置き換えてください。

### 3. 仮想環境の作成

Raspberry Pi OSのシステムパッケージ（picamera2、libcamera）を利用するため、`--system-site-packages`オプションを指定して仮想環境を作成します。

```bash
python3 -m venv --system-site-packages venv
```

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

ultralyticsパッケージをインストールします。依存関係は自動的に解決されます。

```bash
pip install ultralytics
```

**重要**: numpy、opencv-python、picamera2、libcameraはRaspberry Pi OSにプリインストールされているシステムパッケージを使用します。仮想環境作成時に`--system-site-packages`オプションを指定することで、これらのパッケージにアクセスできます。

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

「All imports successful!」と表示されれば、セットアップは完了です。

## スクリプトの実行

### 基本的な実行方法

```bash
cd production
python3 production_camera_left_half_realtime.py
```

### コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--model` | モデルファイルのパス | `../weights/best.pt` |
| `--conf` | 検出の信頼度閾値 | `0.3` |
| `--width` | カメラ解像度（幅） | `2304` |
| `--height` | カメラ解像度（高さ） | `1296` |
| `--no-display` | ヘッドレスモード（画面表示なし） | - |
| `--distance` | ピント距離（cm） | `20.0` |
| `--auto-focus` | オートフォーカスモード | - |
| `--display-scale` | 表示ウィンドウのスケール | `0.5` |
| `--exposure` | 露出補正（-8.0〜8.0） | `-0.5` |
| `--contrast` | コントラスト（0.0〜32.0） | `2.0` |
| `--brightness` | 明るさ（-1.0〜1.0） | `0.0` |

### 実行例

オートフォーカスモードで実行：

```bash
python3 production_camera_left_half_realtime.py --auto-focus
```

信頼度閾値を変更して実行：

```bash
python3 production_camera_left_half_realtime.py --conf 0.5
```

ヘッドレスモード（SSH接続時など）で実行：

```bash
python3 production_camera_left_half_realtime.py --no-display
```

### 操作方法

- `q`キー: プログラムを終了
- `s`キー: 現在のフレームを画像として保存
- `Ctrl+C`: プログラムを強制終了
