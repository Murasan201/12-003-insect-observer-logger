# Phase 4-5 モジュール関数一覧

**文書番号**: 12-002-FUNC-002  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: Phase 4-5 モジュール関数一覧  
**対象フェーズ**: Phase 4 (分析・可視化), Phase 5 (システム統合・制御)  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 文書概要

### 目的
Phase 4-5のモジュール（分析・可視化・システム統合制御）における全関数・メソッドの一覧と基本インターフェース情報を提供する。

### 対象モジュール
- **Phase 4**: activity_calculator.py, data_processor.py, visualization.py
- **Phase 5**: main.py, system_controller.py, scheduler.py

---

## 🔧 Phase 4: 分析・可視化モジュール

### activity_calculator.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `ActivityCalculator.__init__` | 活動量算出クラス初期化 | `config: SystemConfiguration` | `None` |
| `calculate_activity_metrics` | 活動量指標算出 | `detection_records: List[DetectionRecord]` | `ActivityMetrics` |
| `calculate_hourly_activity` | 時間別活動量算出 | `records: List[DetectionRecord], hour: int` | `float` |
| `calculate_daily_activity` | 日別活動量算出 | `records: List[DetectionRecord]` | `float` |
| `calculate_peak_activity_periods` | ピーク活動期間算出 | `records: List[DetectionRecord]` | `List[Dict[str, Any]]` |
| `calculate_activity_trends` | 活動トレンド算出 | `records: List[DetectionRecord]` | `Dict[str, Any]` |
| `generate_hourly_summaries` | 時間別サマリー生成 | `records: List[DetectionRecord]` | `List[HourlySummary]` |
| `generate_daily_summary` | 日別サマリー生成 | `records: List[DetectionRecord]` | `DailySummary` |
| `load_detection_data` | 検出データ読み込み | `date: str` | `List[DetectionRecord]` |
| `analyze_detection_patterns` | 検出パターン分析 | `records: List[DetectionRecord]` | `Dict[str, Any]` |
| `calculate_statistical_metrics` | 統計指標算出 | `values: List[float]` | `Dict[str, float]` |
| `detect_anomalies` | 異常検知 | `records: List[DetectionRecord]` | `List[Dict[str, Any]]` |
| `get_calculation_stats` | 算出統計取得 | なし | `ActivityCalculationStats` |
| `clear_cache` | キャッシュクリア | なし | `None` |
| `cleanup_calculator` | 算出器クリーンアップ | なし | `None` |

### data_processor.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `DataProcessor.__init__` | データ処理クラス初期化 | `config: SystemConfiguration` | `None` |
| `process_detection_data` | 検出データ処理 | `records: List[DetectionRecord]` | `List[DetectionRecord]` |
| `clean_data` | データクリーニング | `records: List[DetectionRecord]` | `List[DetectionRecord]` |
| `normalize_data` | データ正規化 | `records: List[DetectionRecord]` | `List[DetectionRecord]` |
| `filter_outliers` | 外れ値フィルタリング | `records: List[DetectionRecord]` | `List[DetectionRecord]` |
| `smooth_time_series` | 時系列データ平滑化 | `values: List[float], window_size: int` | `List[float]` |
| `interpolate_missing_data` | 欠損データ補間 | `records: List[DetectionRecord]` | `List[DetectionRecord]` |
| `aggregate_data` | データ集約 | `records: List[DetectionRecord], interval: str` | `List[Dict[str, Any]]` |
| `export_processed_data` | 処理済みデータエクスポート | `records: List[DetectionRecord], format: str` | `Path` |
| `import_external_data` | 外部データインポート | `file_path: Path, format: str` | `List[DetectionRecord]` |
| `validate_data_integrity` | データ整合性検証 | `records: List[DetectionRecord]` | `bool` |
| `merge_datasets` | データセット結合 | `datasets: List[List[DetectionRecord]]` | `List[DetectionRecord]` |
| `get_processing_summary` | 処理サマリー取得 | なし | `Dict[str, Any]` |
| `cleanup_processor` | 処理器クリーンアップ | なし | `None` |

### visualization.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `Visualizer.__init__` | 可視化クラス初期化 | `config: SystemConfiguration` | `None` |
| `create_activity_chart` | 活動量グラフ作成 | `metrics: ActivityMetrics, chart_type: str` | `Path` |
| `create_timeline_chart` | タイムライングラフ作成 | `records: List[DetectionRecord]` | `Path` |
| `create_heatmap` | ヒートマップ作成 | `data: Dict[str, Any], title: str` | `Path` |
| `create_distribution_chart` | 分布グラフ作成 | `values: List[float], title: str` | `Path` |
| `create_comparison_chart` | 比較グラフ作成 | `datasets: Dict[str, List[float]], title: str` | `Path` |
| `create_dashboard` | ダッシュボード作成 | `metrics: ActivityMetrics, records: List[DetectionRecord]` | `Path` |
| `generate_report_pdf` | PDFレポート生成 | `content: Dict[str, Any]` | `Path` |
| `export_visualization_report` | 可視化レポートエクスポート | `metrics: ActivityMetrics, records: List[DetectionRecord], summaries: List[HourlySummary]` | `Path` |
| `create_interactive_plot` | 対話的プロット作成 | `data: Dict[str, Any], plot_type: str` | `str` |
| `save_chart` | グラフ保存 | `figure: Any, filename: str, format: str` | `Path` |
| `customize_chart_style` | グラフスタイルカスタマイズ | `figure: Any, style_config: Dict[str, Any]` | `Any` |
| `get_visualization_stats` | 可視化統計取得 | なし | `Dict[str, Any]` |
| `cleanup_visualizer` | 可視化器クリーンアップ | なし | `None` |

---

## 🔧 Phase 5: システム統合・制御モジュール

### main.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `InsectObserverSystem.__init__` | システムメイン制御クラス初期化 | `config_path: str` | `None` |
| `initialize_system` | システム全体初期化 | なし | `bool` |
| `run_main_loop` | メインループ実行 | なし | `None` |
| `shutdown_system` | システム安全終了 | なし | `None` |
| `run_single_detection` | 単発検出実行 | なし | `Dict[str, Any]` |
| `run_analysis_for_date` | 指定日分析実行 | `date: str` | `bool` |
| `get_system_status` | システム状態取得 | なし | `Dict[str, Any]` |
| `_perform_detection_cycle` | 検出サイクル実行 | なし | `Dict[str, Any]` |
| `_perform_daily_analysis` | 日次分析実行 | なし | `None` |
| `_system_monitoring_loop` | システム監視ループ | なし | `None` |
| `_monitor_system_resources` | システムリソース監視 | なし | `None` |
| `_check_module_health` | モジュール健全性チェック | なし | `None` |
| `_update_system_status` | システム状態更新 | なし | `None` |
| `_check_config_updates` | 設定更新チェック | なし | `None` |
| `_signal_handler` | シグナルハンドラー | `signum: int, frame: Any` | `None` |
| `setup_logging` | ログ設定 | `level: str` | `None` |

### system_controller.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `SystemController.__init__` | システム統合管理クラス初期化 | `config: SystemConfiguration, hardware_controller: HardwareController, detector: InsectDetector, detection_processor: DetectionProcessor, activity_calculator: ActivityCalculator, visualizer: Visualizer` | `None` |
| `execute_detection_workflow` | 統合検出ワークフロー実行 | `use_ir_led: bool, save_results: bool` | `Optional[DetectionRecord]` |
| `execute_analysis_workflow` | 統合分析ワークフロー実行 | `date: str, generate_report: bool` | `Optional[ActivityMetrics]` |
| `perform_health_check` | システム健全性チェック実行 | なし | `Dict[str, Any]` |
| `get_performance_report` | パフォーマンスレポート取得 | なし | `Dict[str, Any]` |
| `perform_system_maintenance` | システムメンテナンス実行 | なし | `Dict[str, Any]` |
| `get_system_diagnostics` | システム診断情報取得 | なし | `Dict[str, Any]` |
| `cleanup` | リソース解放 | なし | `None` |
| `_prepare_hardware` | ハードウェア前処理 | なし | `bool` |
| `_cleanup_hardware` | ハードウェア後処理 | なし | `None` |
| `_update_performance_metrics` | パフォーマンス指標更新 | `record: DetectionRecord, workflow_time: float` | `None` |
| `_check_hardware_health` | ハードウェア健全性チェック | なし | `bool` |
| `_check_detector_health` | 検出器健全性チェック | なし | `bool` |
| `_check_processor_health` | 処理器健全性チェック | なし | `bool` |
| `_check_calculator_health` | 算出器健全性チェック | なし | `bool` |
| `_check_visualizer_health` | 可視化器健全性チェック | なし | `bool` |

### scheduler.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `SchedulerManager.__init__` | スケジューラー管理クラス初期化 | `detection_interval: int, analysis_time: str` | `None` |
| `schedule_detection` | 検出処理スケジューリング | `detection_function: Callable` | `str` |
| `schedule_daily_analysis` | 日次分析スケジューリング | `analysis_function: Callable` | `str` |
| `schedule_custom_task` | カスタムタスクスケジューリング | `task_id: str, name: str, function: Callable, interval_seconds: int, delay_seconds: int` | `bool` |
| `start` | スケジューラー開始 | なし | `bool` |
| `stop` | スケジューラー停止 | なし | `bool` |
| `pause_detection` | 検出処理一時停止 | `duration_seconds: int` | `None` |
| `update_detection_interval` | 検出間隔更新 | `new_interval: int` | `bool` |
| `get_scheduler_status` | スケジューラー状態取得 | なし | `Dict[str, Any]` |
| `enable_task` | タスク有効化 | `task_id: str` | `bool` |
| `disable_task` | タスク無効化 | `task_id: str` | `bool` |
| `remove_task` | タスク削除 | `task_id: str` | `bool` |
| `cleanup` | リソース解放 | なし | `None` |
| `_scheduler_loop` | メインスケジューラーループ | なし | `None` |
| `_check_and_execute_tasks` | 実行すべきタスクチェック・実行 | なし | `None` |
| `_execute_task` | 指定タスク実行開始 | `task: ScheduledTask` | `None` |
| `_task_runner` | タスク実行ランナー | `task: ScheduledTask` | `None` |
| `_wait_for_tasks_completion` | 実行中タスク完了待機 | `timeout: int` | `None` |
| `_update_stats` | 統計情報更新 | なし | `None` |
| `_calculate_next_daily_run` | 次回日次分析実行時刻計算 | なし | `datetime` |

---

## 📊 統計情報

### Phase 4-5 関数統計
- **Phase 4 分析・可視化モジュール**: 42関数
  - activity_calculator.py: 15関数
  - data_processor.py: 14関数
  - visualization.py: 13関数

- **Phase 5 システム統合・制御**: 42関数
  - main.py: 16関数
  - system_controller.py: 16関数
  - scheduler.py: 20関数

**Phase 4-5 総関数数**: 84関数

---

## 🔄 主要処理フロー関数

### データ処理パイプライン
```
load_detection_data → clean_data → normalize_data → 
filter_outliers → calculate_activity_metrics → 
create_activity_chart → export_visualization_report
```

### システム統合ワークフロー
```
initialize_system → run_main_loop → _perform_detection_cycle → 
execute_detection_workflow → _perform_daily_analysis → 
execute_analysis_workflow → shutdown_system
```

### スケジューリングサイクル
```
schedule_detection → schedule_daily_analysis → start → 
_scheduler_loop → _check_and_execute_tasks → 
_execute_task → _task_runner
```

---

## 📝 実装メモ

### 非同期処理
- スケジューラーは別スレッドで実行
- システム監視ループは並行実行
- タスク実行は独立スレッドで処理

### データフロー
- 検出データ → 処理 → 分析 → 可視化の一方向フロー
- キャッシュ機能による処理効率化
- バッチ処理対応による大量データ処理

### エラーハンドリング
- 各段階での適切な例外処理
- 部分的失敗時の継続処理
- リトライ機能による復旧処理

### 設定管理
- 動的設定変更対応
- 設定妥当性検証
- デフォルト値による安全な初期化

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成・Phase 4-5 関数一覧 |