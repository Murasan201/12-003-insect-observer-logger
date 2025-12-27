# Phase 1-3 モジュール関数一覧

**文書番号**: 12-003-FUNC-001  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: Phase 1-3 モジュール関数一覧  
**対象フェーズ**: Phase 1 (基盤), Phase 2 (ハードウェア制御), Phase 3 (検出)  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 文書概要

### 目的
Phase 1-3のモジュール（基盤・ハードウェア制御・検出）における全関数・メソッドの一覧と基本インターフェース情報を提供する。

### 対象モジュール
- **Phase 1**: config_manager.py, detection_models.py, activity_models.py, system_models.py, data_validator.py, file_naming.py
- **Phase 2**: hardware_controller.py
- **Phase 3**: model_manager.py, insect_detector.py, detection_processor.py

---

## 🔧 Phase 1: 基盤モジュール

### config/config_manager.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `ConfigManager.__init__` | 設定管理クラス初期化 | `config_path: str` | `None` |
| `load_config` | 設定ファイル読み込み・解析 | なし | `bool` |
| `save_config` | 設定ファイル保存 | なし | `bool` |
| `get_setting` | 指定キーの設定値取得 | `key: str, default: Any = None` | `Any` |
| `set_setting` | 設定値更新・保存 | `key: str, value: Any` | `bool` |
| `get_all_settings` | 全設定取得 | なし | `Dict[str, Any]` |
| `validate_config` | 設定妥当性検証 | なし | `Tuple[bool, List[str]]` |
| `reload_config` | 設定リロード | なし | `bool` |
| `backup_config` | 設定バックアップ作成 | `backup_path: Optional[str] = None` | `bool` |
| `restore_config` | 設定復元 | `backup_path: str` | `bool` |
| `get_config_schema` | 設定スキーマ取得 | なし | `Dict[str, Any]` |
| `_create_default_config` | デフォルト設定作成 | なし | `Dict[str, Any]` |
| `_validate_section` | セクション妥当性検証 | `section_name: str, section_data: Dict` | `List[str]` |

### models/detection_models.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `DetectionResult.__init__` | 検出結果データクラス初期化 | 各属性値 | `None` |
| `DetectionResult.to_dict` | 辞書形式変換 | なし | `Dict[str, Any]` |
| `DetectionResult.from_dict` | 辞書から復元 | `data: Dict[str, Any]` | `DetectionResult` |
| `DetectionResult.get_confidence_summary` | 信頼度サマリー取得 | なし | `Dict[str, float]` |
| `DetectionRecord.__init__` | 検出記録データクラス初期化 | 各属性値 | `None` |
| `DetectionRecord.to_dict` | 辞書形式変換 | なし | `Dict[str, Any]` |
| `DetectionRecord.from_dict` | 辞書から復元 | `data: Dict[str, Any]` | `DetectionRecord` |
| `DetectionRecord.save_to_file` | ファイル保存 | `file_path: Path` | `bool` |
| `DetectionRecord.load_from_file` | ファイル読み込み | `file_path: Path` | `Optional[DetectionRecord]` |
| `DetectionRecord.get_detection_summary` | 検出サマリー取得 | なし | `Dict[str, Any]` |
| `DetectionStats.__init__` | 統計データクラス初期化 | 各属性値 | `None` |
| `DetectionStats.update_stats` | 統計更新 | `record: DetectionRecord` | `None` |
| `DetectionStats.get_summary` | 統計サマリー取得 | なし | `Dict[str, Any]` |

### models/activity_models.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `ActivityMetrics.__init__` | 活動量指標データクラス初期化 | 各属性値 | `None` |
| `ActivityMetrics.to_dict` | 辞書形式変換 | なし | `Dict[str, Any]` |
| `ActivityMetrics.from_dict` | 辞書から復元 | `data: Dict[str, Any]` | `ActivityMetrics` |
| `ActivityMetrics.calculate_activity_score` | 活動スコア算出 | なし | `float` |
| `HourlySummary.__init__` | 時間別サマリーデータクラス初期化 | 各属性値 | `None` |
| `HourlySummary.to_dict` | 辞書形式変換 | なし | `Dict[str, Any]` |
| `HourlySummary.from_dict` | 辞書から復元 | `data: Dict[str, Any]` | `HourlySummary` |
| `DailySummary.__init__` | 日別サマリーデータクラス初期化 | 各属性値 | `None` |
| `DailySummary.to_dict` | 辞書形式変換 | なし | `Dict[str, Any]` |
| `DailySummary.from_dict` | 辞書から復元 | `data: Dict[str, Any]` | `DailySummary` |
| `DailySummary.add_hourly_data` | 時間別データ追加 | `hourly: HourlySummary` | `None` |
| `DailySummary.calculate_daily_metrics` | 日次指標算出 | なし | `ActivityMetrics` |
| `ActivityCalculationStats.__init__` | 算出統計データクラス初期化 | 各属性値 | `None` |

### models/system_models.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `SystemConfiguration.__init__` | システム設定データクラス初期化 | 各属性値 | `None` |
| `SystemConfiguration.to_dict` | 辞書形式変換 | なし | `Dict[str, Any]` |
| `SystemConfiguration.from_dict` | 辞書から復元 | `data: Dict[str, Any]` | `SystemConfiguration` |
| `SystemConfiguration.validate` | 設定妥当性検証 | なし | `Tuple[bool, List[str]]` |
| `HardwareStatus.__init__` | ハードウェア状態データクラス初期化 | 各属性値 | `None` |
| `HardwareStatus.to_dict` | 辞書形式変換 | なし | `Dict[str, Any]` |
| `HardwareStatus.is_healthy` | 健全性判定 | なし | `bool` |
| `HardwareStatus.get_status_summary` | 状態サマリー取得 | なし | `Dict[str, Any]` |
| `SystemStatus.__init__` | システム状態データクラス初期化 | 各属性値 | `None` |
| `SystemStatus.to_dict` | 辞書形式変換 | なし | `Dict[str, Any]` |
| `SystemStatus.update_uptime` | 稼働時間更新 | なし | `None` |
| `SystemStatus.get_status_summary` | 状態サマリー取得 | なし | `Dict[str, Any]` |

### utils/data_validator.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `DataValidator.__init__` | データ検証クラス初期化 | なし | `None` |
| `validate_detection_record` | 検出記録検証 | `record: DetectionRecord` | `ValidationResult` |
| `validate_image_file` | 画像ファイル検証 | `file_path: Path` | `ValidationResult` |
| `validate_config_data` | 設定データ検証 | `config_data: Dict[str, Any]` | `ValidationResult` |
| `validate_date_format` | 日付形式検証 | `date_string: str` | `ValidationResult` |
| `validate_numeric_range` | 数値範囲検証 | `value: float, min_val: float, max_val: float` | `ValidationResult` |
| `validate_file_permissions` | ファイル権限検証 | `file_path: Path, required_perms: str` | `ValidationResult` |
| `validate_directory_structure` | ディレクトリ構造検証 | `base_path: Path` | `ValidationResult` |
| `_check_image_integrity` | 画像整合性チェック | `file_path: Path` | `bool` |
| `_validate_required_fields` | 必須フィールド検証 | `data: Dict, required: List[str]` | `List[str]` |

### utils/file_naming.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `FileNamingManager.__init__` | ファイル命名管理クラス初期化 | `config: Dict[str, Any]` | `None` |
| `generate_detection_filename` | 検出ファイル名生成 | `timestamp: datetime, detection_count: int` | `str` |
| `generate_analysis_filename` | 分析ファイル名生成 | `date: str, analysis_type: str` | `str` |
| `generate_log_filename` | ログファイル名生成 | `log_type: str, timestamp: datetime` | `str` |
| `generate_backup_filename` | バックアップファイル名生成 | `original_name: str, timestamp: datetime` | `str` |
| `parse_filename` | ファイル名解析 | `filename: str` | `Dict[str, Any]` |
| `validate_filename` | ファイル名妥当性検証 | `filename: str` | `bool` |
| `get_file_category` | ファイルカテゴリ取得 | `filename: str` | `str` |
| `clean_filename` | ファイル名サニタイズ | `filename: str` | `str` |
| `ensure_unique_filename` | 一意ファイル名確保 | `base_path: Path, filename: str` | `str` |

---

## 🔧 Phase 2: ハードウェア制御モジュール

### hardware_controller.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `HardwareController.__init__` | ハードウェア制御クラス初期化 | `config: SystemConfiguration` | `None` |
| `initialize_hardware` | ハードウェア初期化 | なし | `bool` |
| `cleanup_hardware` | ハードウェアクリーンアップ | なし | `None` |
| `initialize_camera` | カメラ初期化 | なし | `bool` |
| `cleanup_camera` | カメラクリーンアップ | なし | `None` |
| `capture_image` | 画像キャプチャ | `use_led: bool = True` | `Optional[np.ndarray]` |
| `save_image` | 画像保存 | `image: np.ndarray, filepath: Path` | `bool` |
| `initialize_led` | LED初期化 | なし | `bool` |
| `control_ir_led` | IR LED制御 | `brightness: float` | `bool` |
| `cleanup_led` | LEDクリーンアップ | なし | `None` |
| `get_system_status` | システム状態取得 | なし | `HardwareStatus` |
| `get_detailed_status` | 詳細状態取得 | なし | `Dict[str, Any]` |
| `perform_hardware_test` | ハードウェアテスト実行 | なし | `Dict[str, Any]` |
| `_get_cpu_temperature` | CPU温度取得 | なし | `float` |
| `_test_camera_capture` | カメラキャプチャテスト | なし | `bool` |
| `_test_led_control` | LED制御テスト | なし | `bool` |

---

## 🔧 Phase 3: 検出モジュール

### model_manager.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `ModelManager.__init__` | モデル管理クラス初期化 | `config: SystemConfiguration` | `None` |
| `setup_model` | モデルセットアップ | なし | `bool` |
| `download_model` | モデルダウンロード | `force_download: bool = False` | `bool` |
| `load_model` | モデル読み込み | なし | `bool` |
| `check_model_status` | モデル状態確認 | なし | `Dict[str, Any]` |
| `get_model_info` | モデル情報取得 | なし | `Dict[str, Any]` |
| `validate_model` | モデル妥当性検証 | なし | `bool` |
| `cleanup_model` | モデルクリーンアップ | なし | `None` |
| `_download_from_huggingface` | HuggingFaceからダウンロード | なし | `bool` |
| `_verify_model_file` | モデルファイル検証 | `model_path: Path` | `bool` |
| `_get_model_metadata` | モデルメタデータ取得 | なし | `Dict[str, Any]` |

### insect_detector.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `InsectDetector.__init__` | 昆虫検出クラス初期化 | `config: SystemConfiguration, model_manager: ModelManager, hardware_controller: HardwareController` | `None` |
| `initialize_detector` | 検出器初期化 | なし | `bool` |
| `detect_single_image` | 単発画像検出 | `use_ir_led: bool = True, save_result: bool = True` | `Optional[DetectionRecord]` |
| `detect_from_file` | ファイルから検出 | `image_path: Path, save_result: bool = True` | `Optional[DetectionRecord]` |
| `detect_batch_images` | バッチ画像検出 | `image_paths: List[Path], save_results: bool = True` | `List[DetectionRecord]` |
| `get_detector_status` | 検出器状態取得 | なし | `Dict[str, Any]` |
| `get_detailed_status` | 詳細状態取得 | なし | `Dict[str, Any]` |
| `cleanup_detector` | 検出器クリーンアップ | なし | `None` |
| `_process_detection_results` | 検出結果処理 | `results: Any, image: np.ndarray, timestamp: datetime` | `DetectionRecord` |
| `_apply_detection_filters` | 検出フィルター適用 | `detections: List[Dict]` | `List[Dict]` |
| `_save_detection_image` | 検出画像保存 | `image: np.ndarray, detections: List[Dict], timestamp: datetime` | `Optional[Path]` |
| `_draw_detection_boxes` | 検出ボックス描画 | `image: np.ndarray, detections: List[Dict]` | `np.ndarray` |
| `_calculate_detection_confidence` | 検出信頼度算出 | `detections: List[Dict]` | `float` |

### detection_processor.py

| 関数名 | 処理概要 | 引数 | 戻り値 |
|--------|----------|------|--------|
| `DetectionProcessor.__init__` | 検出処理クラス初期化 | `config: SystemConfiguration` | `None` |
| `process_detection_record` | 検出記録処理 | `record: DetectionRecord` | `DetectionRecord` |
| `apply_noise_filtering` | ノイズフィルタリング適用 | `record: DetectionRecord` | `DetectionRecord` |
| `enhance_detection_data` | 検出データ拡張 | `record: DetectionRecord` | `DetectionRecord` |
| `validate_detection_quality` | 検出品質検証 | `record: DetectionRecord` | `bool` |
| `save_processed_record` | 処理済み記録保存 | `record: DetectionRecord` | `bool` |
| `load_detection_records` | 検出記録読み込み | `date: str` | `List[DetectionRecord]` |
| `get_processing_stats` | 処理統計取得 | なし | `DetectionProcessingStats` |
| `cleanup_processor` | 処理器クリーンアップ | なし | `None` |
| `_apply_confidence_threshold` | 信頼度閾値適用 | `detections: List[Dict], threshold: float` | `List[Dict]` |
| `_remove_duplicate_detections` | 重複検出除去 | `detections: List[Dict]` | `List[Dict]` |
| `_enhance_detection_metadata` | 検出メタデータ拡張 | `record: DetectionRecord` | `DetectionRecord` |
| `_calculate_detection_metrics` | 検出指標算出 | `record: DetectionRecord` | `Dict[str, float]` |
| `_save_record_to_database` | データベース保存 | `record: DetectionRecord` | `bool` |

---

## 📊 統計情報

### Phase 1-3 関数統計
- **Phase 1 基盤モジュール**: 58関数
  - config_manager.py: 13関数
  - detection_models.py: 13関数
  - activity_models.py: 12関数
  - system_models.py: 11関数
  - data_validator.py: 9関数
  - file_naming.py: 10関数

- **Phase 2 ハードウェア制御**: 16関数
  - hardware_controller.py: 16関数

- **Phase 3 検出モジュール**: 39関数
  - model_manager.py: 11関数
  - insect_detector.py: 14関数
  - detection_processor.py: 14関数

**総関数数**: 113関数

---

## 📝 実装メモ

### データクラス共通メソッド
- `__init__`: 初期化処理
- `to_dict`: 辞書形式変換
- `from_dict`: 辞書からの復元
- `validate`: 妥当性検証（一部）

### エラーハンドリング
- 各関数は適切な例外処理を実装
- 戻り値での成功・失敗判定
- ログ出力による処理状況記録

### 型ヒント
- 全関数で型ヒントを使用
- Optional型による None 許可の明示
- 複合型（List, Dict, Tuple）の詳細指定

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成・Phase 1-3 関数一覧 |