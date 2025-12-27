# Phase 7: CLI・ユーザーインターフェースモジュール処理説明書

**フェーズ番号**: Phase 7  
**フェーズ名**: CLI・ユーザーインターフェースモジュール  
**説明**: 拡張コマンドラインインターフェース、バッチ処理、自動スケジューリング機能を提供するモジュール群  
**作成日**: 2025-07-29  
**文書バージョン**: 1.0  

---

## 📋 フェーズ概要

### 目的
システムの操作性・運用性を向上させるため、直感的なコマンドラインインターフェース、包括的な管理機能、自動化されたバッチ処理・スケジューリング機能を提供し、効率的なシステム運用を実現する。

### 主要機能
- **高度なCLI**: Rich UIライブラリによる視覚的表示・対話的操作
- **包括的システム管理**: 検出・分析・診断・メンテナンス機能の統合
- **バッチ処理・自動化**: 定期実行・ジョブ管理・スケジューリング
- **リアルタイム監視**: システム状態・ハードウェア監視・パフォーマンス表示
- **設定管理**: 設定検証・適用・動的変更機能
- **外部連携**: cron・systemd統合・外部スケジューラ連携

---

## 📁 含まれるモジュール

### 1. cli.py - 拡張CLIインターフェースモジュール
**文書番号**: 12-003-PROC-012  
**概要**: Clickライブラリを使用した高度なコマンドラインインターフェース  

**主要クラス**: `CLIController`

**主要機能**:
- 複数実行モード（連続観察・単発検出・データ分析）
- リアルタイムシステム監視・ステータス表示
- 包括的システム診断・ハードウェアテスト
- 対話式CLI・設定管理
- データクリーンアップ・メンテナンス機能
- Rich UIライブラリによる視覚的表示

**コマンド群**:
- **run**: 連続観察モード実行
- **detect**: 単発検出実行
- **analyze**: データ分析実行
- **status**: システム状態表示
- **diagnose**: システム診断実行
- **cleanup**: データクリーンアップ
- **interactive**: 対話モード開始
- **config**: 設定ファイル管理

**表示機能**:
- Rich Table による美しいテーブル表示
- プログレスバー・スピナー表示
- リアルタイム監視・Live表示
- パネル・ボックス・色分け表示

### 2. batch_runner.py - バッチ処理・スケジューリングモジュール
**文書番号**: 12-003-PROC-013  
**概要**: cronやタスクスケジューラからの定期実行・バッチ処理サポート  

**主要クラス**: `BatchRunner`

**主要機能**:
- 定期実行スケジューリング（間隔・日次・週次実行）
- 複数ジョブの並列実行・ジョブキュー管理
- エラーハンドリング・リトライ・タイムアウト処理
- 実行ログ記録・結果追跡・通知機能
- CLI ベースのジョブ管理・設定変更
- cron統合・外部スケジューラ連携

**ジョブタイプ**:
- **interval**: 指定秒間隔での実行
- **daily**: 指定時刻での日次実行
- **weekly**: 指定曜日での週次実行

**デフォルトジョブ**:
- `hourly_detection`: 時間ごとの昆虫検出
- `daily_analysis`: 深夜の日次データ分析
- `weekly_cleanup`: 週次データクリーンアップ
- `daily_backup`: 日次バックアップ（設定により有効化）

**バッチ管理CLI**:
- `scheduler`: スケジューラー起動
- `run-job`: ジョブ即時実行
- `list`: ジョブ一覧表示
- `add/remove`: ジョブ追加・削除
- `enable/disable`: ジョブ有効・無効化
- `cron`: cronエントリ生成

---

## 🔄 処理フロー概要

### CLI実行フロー
```
CLI起動（click フレームワーク）
   ↓
メイングループ・コンテキスト設定
   ├─ ログレベル設定
   ├─ CLIController作成
   └─ 設定ファイル読み込み
   ↓
サブコマンド分岐処理
   ├─ run: 連続観察モード
   │   ├─ システム初期化
   │   ├─ メインループ実行
   │   ├─ キーボード中断処理
   │   └─ クリーンアップ
   ├─ detect: 単発検出
   │   ├─ プログレス表示
   │   ├─ 検出実行
   │   ├─ 結果テーブル表示
   │   └─ 画像保存処理
   ├─ status: システム状態表示
   │   ├─ 状態取得
   │   ├─ JSON/テーブル出力
   │   └─ リアルタイム監視
   ├─ diagnose: システム診断
   │   ├─ 診断項目実行
   │   ├─ 結果テーブル表示
   │   └─ レポート保存
   └─ interactive: 対話モード
       ├─ コマンドループ
       ├─ 動的コマンド実行
       └─ 対話的設定変更
```

### バッチスケジューリングフロー
```
BatchRunner初期化
   ↓
設定ファイル読み込み・ジョブ登録
   ├─ 既存設定読み込み
   └─ デフォルト設定作成
   ↓
スケジューラー起動
   ├─ シグナルハンドラー設定
   ├─ 全ジョブスケジュール設定
   └─ スケジューラーループ開始
   ↓
定期実行・ジョブ管理
   ├─ schedule.run_pending()
   ├─ ジョブ実行判定
   ├─ subprocess実行
   ├─ 結果記録・エラー処理
   └─ 通知・リトライ処理
   ↓
CLI管理機能
   ├─ ジョブ追加・削除・変更
   ├─ 即時実行・状態確認
   ├─ cronエントリ生成
   └─ 設定保存・読み込み
```

### 統合運用フロー
```
システム運用開始
   ↓
CLI による初期設定・診断
   ├─ 設定ファイル検証・適用
   ├─ システム診断実行
   ├─ ハードウェアテスト
   └─ 運用準備確認
   ↓
バッチスケジューラー起動
   ├─ 定期検出ジョブ設定
   ├─ 日次分析ジョブ設定
   ├─ メンテナンスジョブ設定
   └─ スケジューラー常駐
   ↓
運用監視・メンテナンス
   ├─ CLI による状態監視
   ├─ リアルタイム表示
   ├─ アラート・エラー対応
   ├─ データクリーンアップ
   └─ 設定変更・調整
```

---

## 📊 データフロー

### 主要データ構造
- **CLIController**: CLI操作用コントローラー（システム・監視状態管理）
- **BatchJob**: バッチジョブ定義（名前・コマンド・スケジュール・状態）
- **BatchResult**: バッチ実行結果（時刻・状態・出力・エラー）
- **診断結果**: システム診断結果（ハードウェア・モデル・ストレージ・設定）

### モジュール間連携
```
CLI インターフェース
   ├─ main.py (InsectObserverSystem)
   │   ├─ システム初期化・実行制御
   │   ├─ 検出・分析処理実行
   │   └─ 状態取得・診断機能
   ├─ config.config_manager
   │   ├─ 設定読み込み・保存
   │   ├─ 設定検証・適用
   │   └─ 動的設定変更
   └─ 各Phase1-6モジュール
       ├─ ハードウェア制御・状態取得
       ├─ 検出・処理・分析機能
       ├─ エラーハンドリング・監視
       └─ データ管理・可視化

バッチ処理システム
   ├─ schedule ライブラリ
   │   ├─ 間隔・日次・週次スケジューリング
   │   ├─ ジョブ実行判定・管理
   │   └─ スケジュール動的変更
   ├─ subprocess モジュール
   │   ├─ 外部コマンド実行
   │   ├─ タイムアウト・エラー処理
   │   └─ 出力・エラーキャプチャ
   └─ 外部スケジューラ連携
       ├─ cron統合・エントリ生成
       ├─ systemd統合・サービス化
       └─ タスクスケジューラ連携
```

---

## 🎨 ユーザーインターフェース

### Rich UI 表示機能

#### テーブル表示
```python
# システム状態テーブル
table = Table(title="システム状態", box=box.ROUNDED)
table.add_column("項目", style="cyan")
table.add_column("値", style="green")
table.add_row("稼働状態", "稼働中")
table.add_row("稼働時間", "1234秒")
```

#### プログレス表示
```python
# 処理進捗表示
with Progress(SpinnerColumn(), TextColumn()) as progress:
    task = progress.add_task("検出処理中...", total=None)
    result = execute_detection()
    progress.update(task, completed=True)
```

#### リアルタイム監視
```python
# Live表示でのリアルタイム更新
with Live(console=console, refresh_per_second=1) as live:
    while monitoring:
        status_panel = create_status_panel()
        hardware_panel = create_hardware_panel()
        live.update(combined_layout)
```

#### パネル・ボックス表示
```python
# 情報パネル表示
panel = Panel.fit(
    "🐛 昆虫観察システム起動\n"
    "検出間隔: 60秒",
    title="システム起動",
    border_style="green"
)
```

### 対話式CLI
```
insect-observer> help
利用可能なコマンド:
  help     - このヘルプを表示
  status   - システム状態を表示
  detect   - 単発検出を実行
  analyze  - データ分析を実行
  config   - 現在の設定を表示
  exit     - 対話モードを終了

insect-observer> detect
検出画像を保存しますか？ [y/N]: y
✓ 検出完了: 3匹検出

insect-observer> status
🟢 稼働状態: 稼働中
⏱️  稼働時間: 3600秒
📸 処理画像: 120枚
🐛 総検出数: 45匹
```

---

## 🔧 設定・パラメータ

### CLI設定
- **ログレベル**: DEBUG/INFO/WARNING/ERROR
- **設定ファイルパス**: カスタム設定ファイル指定
- **出力ディレクトリ**: 検出画像・レポート出力先
- **表示オプション**: JSON出力・詳細表示・リアルタイム監視

### バッチ処理設定
- **ジョブ定義**: 名前・コマンド・スケジュール・有効性
- **実行制御**: タイムアウト時間・リトライ回数・エラー閾値
- **ログ設定**: 実行ログ・結果記録・通知設定
- **スケジューラー**: 監視間隔・並列実行数・リソース制限

### システム診断項目
- **ハードウェア診断**: カメラ・LED・CPU温度・GPU状態
- **モデル診断**: 検出モデル存在・読み込み可能性
- **ストレージ診断**: ディスク容量・書き込み権限
- **設定診断**: 設定ファイル存在・妥当性検証
- **機能テスト**: カメラキャプチャ・検出処理テスト

---

## 🛠️ 拡張機能

### CLI拡張
```python
# カスタムCLIコマンド追加
@cli.command()
@click.option('--custom-param', help='カスタムパラメータ')
@click.pass_obj
def custom_command(controller, custom_param):
    """カスタム機能実行"""
    # カスタム処理実装
    pass
```

### バッチジョブ拡張
```python
# カスタムバッチジョブ追加
custom_job = BatchJob(
    name="custom_analysis",
    command="python custom_analysis.py --param value",
    schedule_type="daily",
    schedule_time="04:00"
)
runner.add_job(custom_job)
```

### 外部通知連携
```python
def _notify_job_failure(self, job: BatchJob, result: BatchResult):
    """ジョブ失敗通知"""
    # Slack通知
    send_slack_alert(f"Job {job.name} failed: {result.error}")
    
    # メール通知
    send_email_alert(job.name, result.error)
    
    # webhook通知
    send_webhook_notification(job, result)
```

---

## 📈 運用・監視機能

### システム監視
- **リアルタイム状態表示**: CPU・メモリ・温度・稼働時間
- **ハードウェア監視**: カメラ状態・LED状態・ストレージ使用量
- **処理統計**: 検出数・処理時間・エラー率・成功率
- **アラート表示**: 異常状態・警告・エラー通知

### データ管理
- **自動クリーンアップ**: 古いログ・画像・一時ファイルの削除
- **バックアップ**: 重要データの定期バックアップ
- **アーカイブ**: 長期保存データの圧縮・移動
- **容量監視**: ディスク使用量監視・警告通知

### パフォーマンス分析
- **処理時間分析**: 検出・分析処理の性能評価
- **リソース使用率**: CPU・メモリ・ディスクI/O監視
- **スループット測定**: 時間あたり処理能力測定
- **ボトルネック特定**: 性能問題の原因特定・改善提案

---

## 🔗 外部システム連携

### cron統合
```bash
# 自動生成されるcronエントリ
0 2 * * * cd /path/to/project && python batch_runner.py run-job daily_analysis
*/60 * * * * cd /path/to/project && python batch_runner.py run-job hourly_detection
0 3 * * 0 cd /path/to/project && python batch_runner.py run-job weekly_cleanup
```

### systemd統合
```ini
# サービス定義ファイル
[Unit]
Description=Insect Observer System
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/batch_runner.py scheduler
Restart=always
RestartSec=10
User=observer
Group=observer

[Install]
WantedBy=multi-user.target
```

### Docker統合
```dockerfile
# コンテナ化対応
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# CLI エントリーポイント
ENTRYPOINT ["python", "cli.py"]

# バッチスケジューラー起動
CMD ["python", "batch_runner.py", "scheduler"]
```

---

## 📝 実装注意事項

### パフォーマンス
- Rich UI表示のオーバーヘッド最小化
- リアルタイム監視の更新頻度調整
- バッチ処理の并列実行制御・リソース競合回避
- 大量データ処理時のメモリ効率化

### ユーザビリティ
- 直感的なコマンド体系・オプション設計
- エラーメッセージの分かりやすさ・対処法提示
- プログレス表示・処理状況の可視化
- ヘルプ・ドキュメントの充実

### 運用性
- ログファイル管理・ローテーション
- 設定変更の動的反映・バリデーション
- バックアップ・復旧機能の整備
- 監視・アラート機能の実装

### セキュリティ
- 設定ファイル・ログファイルのアクセス権限制御
- 外部コマンド実行時のインジェクション対策
- 機密情報の適切な管理・表示制御
- ネットワーク通信の暗号化・認証

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成・Phase 7全体概要 |

---

## 📚 関連文書

- [基本設計書: システムアーキテクチャ設計](../../basic_design/system_architecture_design.md)
- [基本設計書: インターフェース設計](../../basic_design/interface_design.md)
- [Phase 1: 基盤モジュール処理説明書](../phase1/README.md)
- [Phase 2: ハードウェア制御モジュール処理説明書](../phase2/README.md)
- [Phase 3: 検出モジュール処理説明書](../phase3/README.md)
- [Phase 4: 分析・可視化モジュール処理説明書](../phase4/README.md)
- [Phase 5: システム統合・制御モジュール処理説明書](../phase5/README.md)
- [Phase 6: エラーハンドリング・監視モジュール処理説明書](../phase6/README.md)
- [要件定義書](../../../../requirements/12-003_昆虫自動観察＆ログ記録アプリ_要件定義書.md)
- [CLI使用ガイド](../../../../CLI_USAGE.md)