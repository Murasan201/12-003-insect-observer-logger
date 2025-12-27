# Phase 6-7 モジュール関数一覧

**文書番号**: 12-003-FUNC-003  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: Phase 6-7 モジュール関数一覧  
**対象フェーズ**: Phase 6 (エラーハンドリング・監視), Phase 7 (CLI・ユーザーインターフェース)  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 文書概要

### 目的
Phase 6-7のモジュール（エラーハンドリング・監視・CLI・ユーザーインターフェース）における全関数・メソッドの一覧と基本インターフェース情報を提供する。

### 対象モジュール
- **Phase 6**: error_handler.py, monitoring.py
- **Phase 7**: cli.py, batch_runner.py

---

## 🔧 Phase 6: エラーハンドリング・監視モジュール

### error_handler.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `ErrorHandler.__init__` | エラーハンドリングクラス初期化 | `config: SystemConfiguration` | `None` |
| `handle_detection_error` | 検出エラー処理 | `error: Exception, context: Dict[str, Any]` | `bool` |
| `handle_hardware_error` | ハードウェアエラー処理 | `error: Exception, device: str` | `bool` |
| `handle_system_error` | システムエラー処理 | `error: Exception, module: str` | `bool` |
| `log_error` | エラーログ記録 | `error: Exception, severity: str, context: Dict` | `None` |
| `create_error_report` | エラーレポート作成 | `error_data: Dict[str, Any]` | `Path` |
| `get_error_statistics` | エラー統計取得 | `date_range: Optional[Tuple[str, str]]` | `Dict[str, Any]` |
| `clear_old_error_logs` | 古いエラーログクリア | `days_to_keep: int` | `int` |
| `register_error_callback` | エラーコールバック登録 | `callback: Callable, error_type: str` | `None` |
| `unregister_error_callback` | エラーコールバック解除 | `callback_id: str` | `bool` |
| `send_error_notification` | エラー通知送信 | `error_data: Dict[str, Any], channels: List[str]` | `bool` |
| `recover_from_error` | エラー復旧処理 | `error_type: str, recovery_data: Dict` | `bool` |
| `validate_error_config` | エラー設定検証 | `config: Dict[str, Any]` | `Tuple[bool, List[str]]` |
| `cleanup_error_handler` | エラーハンドラークリーンアップ | なし | `None` |

### monitoring.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `SystemMonitor.__init__` | システム監視クラス初期化 | `config: SystemConfiguration` | `None` |
| `start_monitoring` | 監視開始 | なし | `bool` |
| `stop_monitoring` | 監視停止 | なし | `None` |
| `get_system_metrics` | システム指標取得 | なし | `Dict[str, Any]` |
| `monitor_hardware_status` | ハードウェア状態監視 | なし | `HardwareStatus` |
| `monitor_performance` | パフォーマンス監視 | なし | `Dict[str, float]` |
| `monitor_disk_usage` | ディスク使用量監視 | `paths: List[str]` | `Dict[str, float]` |
| `check_system_health` | システム健全性チェック | なし | `Dict[str, Any]` |
| `create_monitoring_report` | 監視レポート作成 | `period: str` | `Path` |
| `set_alert_threshold` | アラート閾値設定 | `metric: str, threshold: float` | `None` |
| `get_alert_history` | アラート履歴取得 | `hours: int` | `List[Dict[str, Any]]` |
| `send_alert` | アラート送信 | `alert_data: Dict[str, Any]` | `bool` |
| `archive_monitoring_data` | 監視データアーカイブ | `date: str` | `bool` |
| `cleanup_monitoring_data` | 監視データクリーンアップ | `days_to_keep: int` | `int` |
| `get_monitoring_stats` | 監視統計取得 | なし | `Dict[str, Any]` |
| `export_monitoring_data` | 監視データエクスポート | `start_date: str, end_date: str, format: str` | `Path` |

---

## 🔧 Phase 7: CLI・ユーザーインターフェースモジュール

### cli.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `CLIController.__init__` | CLIコントローラー初期化 | `config_path: str` | `None` |
| `initialize_system` | システム初期化 | なし | `bool` |
| `cleanup_system` | システムクリーンアップ | なし | `None` |
| `run_continuous_mode` | 連続観察モード実行 | `interval: int` | `None` |
| `run_single_detection` | 単発検出実行 | `save_image: bool` | `Dict[str, Any]` |
| `run_data_analysis` | データ分析実行 | `date: str, generate_report: bool` | `Dict[str, Any]` |
| `show_system_status` | システム状態表示 | `json_output: bool, watch: bool` | `None` |
| `run_system_diagnosis` | システム診断実行 | `save_report: bool` | `Dict[str, Any]` |
| `run_data_cleanup` | データクリーンアップ実行 | `older_than: int, dry_run: bool` | `Dict[str, Any]` |
| `start_interactive_mode` | 対話モード開始 | なし | `None` |
| `manage_config` | 設定管理 | `action: str, key: Optional[str], value: Optional[str]` | `None` |
| `create_status_table` | 状態テーブル作成 | `status_data: Dict[str, Any]` | `Table` |
| `create_diagnosis_table` | 診断テーブル作成 | `diagnosis_data: Dict[str, Any]` | `Table` |
| `show_progress` | プログレス表示 | `description: str, task_func: Callable` | `Any` |
| `display_detection_results` | 検出結果表示 | `results: Dict[str, Any]` | `None` |

### batch_runner.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `BatchRunner.__init__` | バッチランナー初期化 | `config_path: str` | `None` |
| `_load_job_config` | ジョブ設定読み込み | なし | `None` |
| `_create_default_config` | デフォルト設定作成 | なし | `None` |
| `save_job_config` | ジョブ設定保存 | なし | `None` |
| `add_job` | ジョブ追加 | `job: BatchJob` | `None` |
| `remove_job` | ジョブ削除 | `job_name: str` | `bool` |
| `enable_job` | ジョブ有効/無効化 | `job_name: str, enabled: bool` | `bool` |
| `_setup_job_schedule` | ジョブスケジュール設定 | `job: BatchJob` | `None` |
| `_run_job` | ジョブ実行 | `job: BatchJob` | `BatchResult` |
| `_save_job_result` | ジョブ実行結果保存 | `result: BatchResult` | `None` |
| `_notify_job_failure` | ジョブ失敗通知 | `job: BatchJob, result: BatchResult` | `None` |
| `run_scheduler` | スケジューラー実行 | なし | `None` |
| `run_job_immediately` | ジョブ即時実行 | `job_name: str` | `Optional[BatchResult]` |
| `get_job_status` | 全ジョブ状態取得 | なし | `List[Dict[str, Any]]` |
| `_signal_handler` | シグナルハンドラー | `signum: int, frame: Any` | `None` |
| `create_cron_entry` | cronエントリ生成 | `job_name: str, schedule_time: str, python_path: str` | `str` |
| `main` | メイン関数・CLIエントリーポイント | なし | `int` |

---

## 📊 統計情報

### Phase 6-7 関数統計
- **Phase 6 エラーハンドリング・監視モジュール**: 30関数
  - error_handler.py: 14関数
  - monitoring.py: 16関数

- **Phase 7 CLI・ユーザーインターフェース**: 32関数
  - cli.py: 15関数
  - batch_runner.py: 17関数

**Phase 6-7 総関数数**: 62関数

---

## 🔄 主要処理フロー関数

### エラー処理・監視フロー
```
handle_detection_error → log_error → create_error_report → 
send_error_notification → recover_from_error
```

### システム監視フロー
```
start_monitoring → get_system_metrics → monitor_hardware_status → 
check_system_health → set_alert_threshold → send_alert
```

### CLI操作フロー
```
initialize_system → run_continuous_mode/run_single_detection → 
show_system_status → run_system_diagnosis → cleanup_system
```

### バッチ処理フロー
```
_load_job_config → _setup_job_schedule → run_scheduler → 
_run_job → _save_job_result → _notify_job_failure
```

---

## 🎨 CLI表示機能

### Rich UI 表示関数
- `create_status_table`: システム状態のテーブル表示
- `create_diagnosis_table`: 診断結果のテーブル表示
- `show_progress`: プログレスバー・スピナー表示
- `display_detection_results`: 検出結果の視覚的表示

### 対話機能
- `start_interactive_mode`: 対話的コマンドループ
- `manage_config`: 動的設定変更
- `run_continuous_mode`: リアルタイム監視表示

---

## 📈 データ構造・インターフェース

### エラーハンドリング
- **エラー分類**: 検出エラー・ハードウェアエラー・システムエラー
- **エラー重要度**: INFO・WARNING・ERROR・CRITICAL
- **復旧処理**: 自動復旧・手動復旧・通知のみ

### 監視機能
- **監視対象**: CPU・メモリ・ディスク・温度・ハードウェア状態
- **アラート条件**: 閾値超過・異常値検出・連続エラー
- **データ保存**: 時系列データ・統計サマリー・アラート履歴

### バッチ処理
- **ジョブタイプ**: interval（間隔）・daily（日次）・weekly（週次）
- **実行状態**: running・success・error・timeout
- **管理機能**: 追加・削除・有効化・無効化・即時実行

---

## 🔧 外部連携・拡張機能

### CLI拡張
```python
# カスタムコマンド追加例
@cli.command()
@click.option('--param', help='カスタムパラメータ')
def custom_command(param):
    """カスタム機能実行"""
    controller.run_custom_function(param)
```

### バッチジョブ拡張
```python
# カスタムジョブ定義例
custom_job = BatchJob(
    name="maintenance_check",
    command="python maintenance.py --full-check",
    schedule_type="weekly",
    schedule_time="sunday"
)
```

### 監視アラート拡張
```python
# カスタムアラート処理
def custom_alert_handler(alert_data):
    """カスタムアラート処理"""
    send_webhook_notification(alert_data)
    update_dashboard_status(alert_data)
```

---

## 📝 実装メモ

### CLI設計
- Click フレームワークによる構造化コマンド
- Rich ライブラリによる視覚的表示
- 対話的操作とバッチ操作の両対応
- エラーハンドリングと適切な終了コード

### バッチ処理設計
- schedule ライブラリによる柔軟なスケジューリング
- subprocess による安全なコマンド実行
- JSONL形式による実行ログ記録
- シグナルハンドリングによる適切な終了処理

### 監視・エラー処理設計
- 多層的エラーハンドリング（検出・ハードウェア・システム）
- 閾値ベースアラートシステム
- 自動復旧機能と通知機能
- データアーカイブ・クリーンアップ機能

### 外部システム連携
- cron統合による定期実行
- systemd統合によるサービス化
- ログローテーション・監視ツール連携
- メール・Slack・webhook通知対応

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成・Phase 6-7 関数一覧 |