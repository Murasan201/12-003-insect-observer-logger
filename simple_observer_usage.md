# Simple Observer - 使用ガイド

## 概要
`simple_observer.py`は既存の`insect_detector.py`を利用して、継続的な昆虫観測を行うシンプルなアプリケーションです。

## 特徴
- 既存ファイル（`main.py`、`insect_detector.py`）を一切変更しない
- シンプルな設定と操作
- CSV形式での観測データ保存
- リアルタイムログ出力
- Ctrl+Cでの安全な停止

## 使用方法

### 基本実行
```bash
# デフォルト設定（60秒間隔、無制限実行）
python simple_observer.py

# カスタム間隔（30秒間隔）
python simple_observer.py --interval 30

# 時間制限付き実行（1時間 = 3600秒）
python simple_observer.py --interval 60 --duration 3600

# 出力ディレクトリ指定
python simple_observer.py --interval 30 --output-dir ./my_observations
```

### コマンドライン引数
| 引数 | 説明 | デフォルト値 |
|------|------|-------------|
| `--interval` | 観測間隔（秒） | 60 |
| `--duration` | 観測時間（秒）| 無制限 |
| `--output-dir` | 出力ディレクトリ | `./simple_logs` |

## 出力ファイル

### CSV データファイル
**ファイル名**: `observations_YYYYMMDD_HHMMSS.csv`

**列構成**:
| 列名 | 説明 |
|------|------|
| `timestamp` | 観測時刻 |
| `detection_count` | 検出された昆虫数 |
| `has_detection` | 検出有無（True/False） |
| `confidence_avg` | 平均信頼度 |
| `x_center_avg` | X座標平均値 |
| `y_center_avg` | Y座標平均値 |
| `processing_time_ms` | 処理時間（ミリ秒） |
| `observation_number` | 観測回数 |

### ログファイル
**ファイル名**: `observer_YYYYMMDD_HHMMSS.log`

リアルタイムの観測状況とエラー情報を記録

## 実行例

### 1時間の連続観測（2分間隔）
```bash
python simple_observer.py --interval 120 --duration 3600
```

### 夜間観測（8時間）
```bash
python simple_observer.py --interval 300 --duration 28800
```

### 短時間テスト（10分間、30秒間隔）
```bash
python simple_observer.py --interval 30 --duration 600
```

## 出力例

### コンソール出力
```
2025-07-29 20:30:00,123 - INFO - === Starting Simple Insect Observation ===
2025-07-29 20:30:00,124 - INFO - Start time: 2025-07-29 20:30:00.124000
2025-07-29 20:30:05,456 - INFO - #1: 2 insects detected (confidence: 0.785, time: 1205.3ms)
2025-07-29 20:31:05,789 - INFO - #2: No insects detected (time: 890.1ms)
```

### CSV出力サンプル
```csv
timestamp,detection_count,has_detection,confidence_avg,x_center_avg,y_center_avg,processing_time_ms,observation_number
2025-07-29T20:30:05,2,True,0.785,425.3,320.8,1205.3,1
2025-07-29T20:31:05,0,False,0.0,0.0,0.0,890.1,2
```

## 停止方法

### 正常停止
- **Ctrl+C**: 安全な停止（現在の観測完了後）
- **自動停止**: `--duration`指定時の時間経過

### 強制停止
- **Ctrl+C 連続**: 緊急停止

## トラブルシューティング

### よくある問題

**1. モデルファイルが見つからない**
```
ERROR - Model file not found: ./weights/beetle_detection.pt
```
→ Hugging Faceからモデルをダウンロードしてください

**2. カメラが初期化できない**
```
ERROR - Failed to initialize detector
```
→ カメラが接続されているか確認してください

**3. 権限エラー**
```
ERROR - Permission denied: ./simple_logs
```
→ 出力ディレクトリの権限を確認してください

### ログ確認
詳細なエラー情報は`observer_*.log`ファイルを確認してください。

## システム要件
- Python 3.9+
- 既存の`insect_detector.py`とその依存関係
- カメラ（Raspberry Pi Camera V3 NoIR）
- IR LEDリング（850nm FRS5CS）

## 注意事項
- 長時間実行時はディスク容量を監視してください
- IR LEDの発熱に注意してください
- ネットワーク接続は不要です（完全ローカル動作）