# 昆虫自動観察システム - CLI使用ガイド

## 概要

このシステムは3つのCLIインターフェースを提供します：

1. **`main.py`** - 基本的なシステム操作
2. **`cli.py`** - 高度なCLI機能（推奨）
3. **`batch_runner.py`** - バッチ処理・スケジューリング

## 基本操作（cli.py推奨）

### 1. 単発検出
```bash
# 基本的な検出
python cli.py detect

# 検出画像を保存
python cli.py detect --save-image

# 出力ディレクトリ指定
python cli.py detect --save-image --output-dir ./test_output
```

### 2. 連続観察モード
```bash
# 標準設定で連続観察
python cli.py run

# 30秒間隔で実行
python cli.py run --interval 30

# 24時間限定で実行
python cli.py run --duration 1440
```

### 3. データ分析
```bash
# 昨日のデータを分析
python cli.py analyze

# 特定日の分析
python cli.py analyze 2025-07-25

# グラフ付きHTML形式で出力
python cli.py analyze 2025-07-25 --output-format html --include-charts
```

### 4. システム状態確認
```bash
# 基本状態表示
python cli.py status

# 詳細情報付き
python cli.py status --detailed

# JSON形式で出力
python cli.py status --json

# リアルタイム監視
python cli.py status --watch
```

### 5. システム診断
```bash
# 基本診断
python cli.py diagnose

# 完全診断（時間がかかります）
python cli.py diagnose --full

# 結果をファイルに保存
python cli.py diagnose --full --output-file diagnosis_result.json
```

### 6. データクリーンアップ
```bash
# 30日より古いデータを削除（確認のみ）
python cli.py cleanup --dry-run

# 実際に削除実行
python cli.py cleanup

# 7日より古いデータを削除
python cli.py cleanup --older-than 7
```

### 7. 対話モード
```bash
# 対話モードを開始
python cli.py interactive
```

対話モードでは以下のコマンドが使用できます：
- `help` - コマンド一覧
- `status` - システム状態表示
- `detect` - 単発検出実行
- `analyze` - データ分析実行
- `config` - 設定表示
- `exit` / `quit` - 対話モード終了

## バッチ処理・スケジューリング（batch_runner.py）

### ジョブ管理

#### ジョブ一覧表示
```bash
python batch_runner.py list
```

#### ジョブ追加
```bash
# 毎時検出ジョブ追加
python batch_runner.py add hourly_detect "python cli.py detect" --type interval --time 3600

# 日次分析ジョブ追加（深夜2時）
python batch_runner.py add daily_analysis "python cli.py analyze" --type daily --time 02:00

# 週次クリーンアップ（日曜日）
python batch_runner.py add weekly_cleanup "python cli.py cleanup" --type weekly --time sunday
```

#### ジョブ削除
```bash
python batch_runner.py remove job_name
```

#### ジョブ有効化/無効化
```bash
python batch_runner.py enable job_name
python batch_runner.py disable job_name
```

### ジョブ実行

#### スケジューラー起動
```bash
# フォアグラウンドで実行
python batch_runner.py scheduler

# バックグラウンド実行（推奨）
nohup python batch_runner.py scheduler > scheduler.log 2>&1 &
```

#### ジョブ即時実行
```bash
python batch_runner.py run-job job_name
```

### cron連携

#### cronエントリ生成
```bash
python batch_runner.py cron job_name
```

生成された行をcrontabに追加：
```bash
crontab -e
```

## 設定管理

### 設定ファイル検証
```bash
python cli.py config /path/to/config.json --validate-only
```

### 設定ファイル適用
```bash
python cli.py config /path/to/config.json
```

## ログ・出力ファイル

### ログファイル
- システムログ: `./logs/system_YYYYMMDD.log`
- バッチログ: `./logs/batch/batch_YYYYMMDD.jsonl`

### 出力ファイル
- 検出画像: `./output/detections/`
- 分析レポート: `./output/reports/`
- 設定ファイル: `./config/`

## エラー処理・トラブルシューティング

### よくある問題

#### 1. カメラ初期化エラー
```bash
# 診断実行
python cli.py diagnose --full

# ハードウェア状態確認
python cli.py status --detailed
```

#### 2. モデルファイルが見つからない
```bash
# モデル状態確認
python -c "from model_manager import ModelManager; mm = ModelManager(); print(mm.check_model_status())"
```

#### 3. 設定ファイルエラー
```bash
# 設定検証
python cli.py config ./config/system_config.json --validate-only
```

### デバッグモード
```bash
# デバッグログ有効
python cli.py --log-level DEBUG <command>
```

## パフォーマンス最適化

### 推奨設定
- 検出間隔: 60秒以上（CPU負荷軽減）
- ログレベル: INFO（本番環境）
- 画像保存: 必要時のみ（ストレージ節約）

### リソース監視
```bash
# リアルタイムシステム監視
python cli.py status --watch
```

## 運用例

### 基本的な運用フロー
```bash
# 1. システム診断
python cli.py diagnose --full

# 2. 設定確認
python cli.py status --detailed

# 3. テスト検出
python cli.py detect --save-image

# 4. バッチジョブ設定
python batch_runner.py add detection_job "python cli.py detect" --type interval --time 1800

# 5. スケジューラー起動
nohup python batch_runner.py scheduler > scheduler.log 2>&1 &
```

### 定期メンテナンス
```bash
# 週次実行推奨
python cli.py cleanup --older-than 30
python cli.py diagnose --full --output-file weekly_diagnosis.json
```

## セキュリティ

### 推奨事項
- 設定ファイルのアクセス権限制限: `chmod 600 config/*.json`
- ログファイルの定期ローテーション
- 不要な出力ファイルの削除

### 注意事項
- APIキーや認証情報は設定ファイルに含めない
- リモートアクセス時はSSHトンネル使用
- システム権限での実行は避ける

## 付録：設定例

### バッチ設定例（config/batch_config.json）
```json
{
  "jobs": [
    {
      "name": "hourly_detection",
      "command": "python cli.py detect",
      "schedule_type": "interval",
      "schedule_time": "3600",
      "enabled": true
    },
    {
      "name": "daily_analysis",
      "command": "python cli.py analyze",
      "schedule_type": "daily",
      "schedule_time": "02:00",
      "enabled": true
    }
  ]
}
```

### systemd サービス例
```ini
[Unit]
Description=Insect Observer Batch Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/insect-observer-logger
ExecStart=/usr/bin/python3 batch_runner.py scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## サポート

問題が発生した場合：
1. `python cli.py diagnose --full` でシステム診断
2. ログファイル確認
3. 設定ファイル検証
4. GitHub Issues で報告