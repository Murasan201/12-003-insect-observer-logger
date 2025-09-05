# 12-002 Insect Observer & Logger

昆虫（カブトムシ）の活動を自動検出・記録するシステム

## Overview

Camera Module 3 Wide NoIRとYOLOv8を使用した昆虫観察システム。赤外線照明下で24時間の連続観察が可能。

## Features

- 🔍 リアルタイム昆虫検出
- 📊 長時間データロギング（最大9時間実証済み）
- 🌃 赤外線照明のみでの検出対応
- 📷 検出画像の自動保存
- 🎯 左半分検出エリア指定（誤検出削減）
- 📈 詳細な位置情報記録（CSV出力）

## System Requirements

### Hardware
- Raspberry Pi 4B/5 (4GB以上推奨)
- Camera Module 3 Wide NoIR
- 赤外線LEDライト
- microSDカード（32GB以上）

### Software
- Raspberry Pi OS (64-bit)
- Python 3.9+
- Picamera2
- YOLOv8 (Ultralytics)

## Installation

```bash
# Clone repository
git clone https://github.com/Murasan201/12-002-insect-observer-logger.git
cd 12-002-insect-observer-logger

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download beetle detection model
# Place best.pt in weights/ directory
```

## Production Usage (本番環境での使用)

### リアルタイム監視・調整用

カメラの映像をリアルタイムで確認しながら、検出パラメータを調整できます。

```bash
cd tests/

# デフォルト設定で実行（最適化済みパラメータ）
python3 test_camera_left_half_realtime.py --auto-focus

# パラメータを細かく調整する場合
python3 test_camera_left_half_realtime.py \
  --auto-focus \
  --conf 0.3 \
  --exposure -0.5 \
  --contrast 2 \
  --brightness -0.05
```

**操作方法:**
- `q`キー: 終了
- `s`キー: 現在の画面を保存
- 左半分のみが検出エリア（緑枠で表示）

### 長時間ロギング用（本番データ収集）

バックグラウンドで長時間の観察データを自動収集します。

```bash
cd tests/

# 9時間の本番ロギング（実証済み最適パラメータ）
nohup python3 test_logging_left_half.py \
  --auto-focus \
  --conf 0.4 \
  --exposure -0.5 \
  --contrast 2 \
  --brightness -0.05 \
  --interval 60 \
  --duration 32400 \
  --save-images > logging_9h.log 2>&1 &

# 1時間のテストロギング
python3 test_logging_left_half.py \
  --auto-focus \
  --conf 0.3 \
  --interval 30 \
  --duration 3600 \
  --save-images

# 10分間の短時間テスト
python3 test_logging_left_half.py \
  --auto-focus \
  --interval 10 \
  --duration 600 \
  --save-images
```

### プロセス管理

```bash
# 実行状況確認
ps aux | grep test_logging

# ログのリアルタイム監視
tail -f logging_9h.log

# CSVデータ確認
tail -10 tests/insect_detection_logs/*.csv

# プロセス停止
pkill -f test_logging_left_half.py
```

## Output Files

### ログファイル
```
tests/insect_detection_logs/
├── left_half_detection_log_YYYYMMDD_HHMMSS.csv  # 検出データ
└── left_half_metadata_YYYYMMDD_HHMMSS.json      # メタデータ
```

### 検出画像
```
tests/images/
└── left_half_detection_YYYYMMDD_HHMMSS_mmm.jpg  # 検出時の画像
```

## CSV Data Format

| Column | Description |
|--------|-------------|
| timestamp | 観測時刻 |
| observation_number | 観測番号 |
| detection_count | 検出数 |
| has_detection | 検出有無 |
| class_names | 検出クラス名 |
| confidence_values | 信頼度 |
| center_x, center_y | 中心座標 |
| bbox_width, bbox_height | バウンディングボックスサイズ |
| area | 面積 |
| detection_area | 検出エリア（left_half） |

## Optimal Parameters (最適パラメータ)

実証済みの最適設定（赤外線照明環境）:

- **信頼度閾値 (conf)**: 0.3-0.4
- **露出補正 (exposure)**: -0.5
- **コントラスト (contrast)**: 2.0
- **明度 (brightness)**: -0.05
- **観測間隔**: 60秒（1分）
- **解像度**: 2304x1296（最大広角）

## Troubleshooting

### カメラが検出されない
```bash
# カメラモジュールの確認
libcamera-hello --list-cameras
```

### 誤検出が多い
- conf値を上げる（0.4-0.5）
- 左半分検出モードを使用
- 白い背景を餌エリアに設置

### 検出されない
- conf値を下げる（0.2-0.3）
- 露出を調整（-1.0〜-0.3）
- コントラストを上げる（2.0-3.0）

## Documentation

詳細な技術仕様は以下を参照:

- [ソフトウェア設計書](docs/design/detailed_design/software/software_design.md)
- [要件定義書](docs/requirements/12-002_昆虫自動観察＆ログ記録アプリ_要件定義書.md)
- [トラブルシューティングガイド](docs/troubleshooting.md)

## License

MIT License (コードベース)
※学習済みモデルはAGPL-3.0（YOLOv8由来）

## Contact

- GitHub: https://github.com/Murasan201/12-002-insect-observer-logger
- Issues: https://github.com/Murasan201/12-002-insect-observer-logger/issues