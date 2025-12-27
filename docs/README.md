# 📚 昆虫自動観察システム - ドキュメント

このディレクトリには、昆虫自動観察＆ログ記録アプリケーションの技術文書が格納されています。

## 📋 ドキュメント構成

### 📖 要件・仕様書

#### 📝 要件定義書
- [昆虫自動観察＆ログ記録アプリ要件定義書](requirements/12-003_昆虫自動観察＆ログ記録アプリ_要件定義書.md) - 現行プロジェクトの要件定義
- [昆虫検出アプリケーション要件仕様書](requirements/insect_detection_application_test_project_requirements_spec.md) - ベースプロジェクトの要件

#### 📊 システム仕様書
- [システム仕様書](specifications/system_specification.md) - システム全体の仕様

### 🎨 設計書

#### 📐 基本設計書（システム構成・外部仕様）
- [システムアーキテクチャ設計](design/basic_design/architecture/system_architecture_design.md) - システム全体構造
- [ハードウェア設計](design/basic_design/hardware/hardware_design.md) - 電気回路・物理設計
- [データ設計](design/basic_design/data/data_design.md) - データモデル・ファイル形式
- [インターフェース設計](design/basic_design/interface/interface_design.md) - UI・API設計
- [基本設計書ガイド](design/basic_design/README.md) - 基本設計の読み方

#### 🔧 詳細設計書（実装仕様・クラス設計）
- [ソフトウェア設計](design/detailed_design/software/software_design.md) - モジュール・クラス設計
- [クラス図設計](design/detailed_design/software/class_diagram_design.md) - PlantUMLクラス図
- [詳細設計書ガイド](design/detailed_design/README.md) - 詳細設計の読み方

#### 📋 機能仕様書
- [マスター機能一覧](design/detailed_design/function_specs/master_function_list.md) - 全機能の網羅的リスト
- [Phase 1-3 機能一覧](design/detailed_design/function_specs/phase1-3_function_list.md) - 基盤・ハードウェア・検出機能
- [Phase 4-5 機能一覧](design/detailed_design/function_specs/phase4-5_function_list.md) - 活動量解析・システム統合
- [Phase 6-7 機能一覧](design/detailed_design/function_specs/phase6-7_function_list.md) - エラー処理・CLI拡張

#### 📝 処理説明書（関数・クラス別詳細仕様）
- **Phase 1 - 基盤モジュール**
  - [detection_models処理説明書](design/detailed_design/processing/phase1/detection_models_processing_spec.md) - 検出結果データクラス
  - [activity_models処理説明書](design/detailed_design/processing/phase1/activity_models_processing_spec.md) - 活動量データクラス
  - [system_models処理説明書](design/detailed_design/processing/phase1/system_models_processing_spec.md) - システム設定データクラス
  - [config_manager処理説明書](design/detailed_design/processing/phase1/config_manager_processing_spec.md) - 設定管理クラス
  - [data_validator処理説明書](design/detailed_design/processing/phase1/data_validator_processing_spec.md) - データ検証クラス
  - [file_naming処理説明書](design/detailed_design/processing/phase1/file_naming_processing_spec.md) - ファイル命名規則クラス
- **Phase 2 - ハードウェア制御**
  - [hardware_controller処理説明書](design/detailed_design/processing/phase2/hardware_controller_processing_spec.md) - 統合ハードウェア制御
  - [camera_controller処理説明書](design/detailed_design/processing/phase2/camera_controller_processing_spec.md) - カメラ制御
  - [led_controller処理説明書](design/detailed_design/processing/phase2/led_controller_processing_spec.md) - IR LED制御
- **Phase 3 - 検出機能**
  - [insect_detector処理説明書](design/detailed_design/processing/phase3/insect_detector_processing_spec.md) - YOLOv8昆虫検出
  - [detection_processor処理説明書](design/detailed_design/processing/phase3/detection_processor_processing_spec.md) - 検出結果後処理
  - [model_manager処理説明書](design/detailed_design/processing/phase3/model_manager_processing_spec.md) - YOLOモデル管理
- **Phase 4 - 活動量解析**
  - [activity_calculator処理説明書](design/detailed_design/processing/phase4/activity_calculator_processing_spec.md) - 活動量算出
  - [data_processor処理説明書](design/detailed_design/processing/phase4/data_processor_processing_spec.md) - データ前処理・異常値検出
  - [visualization処理説明書](design/detailed_design/processing/phase4/visualization_processing_spec.md) - グラフ生成
- **Phase 5 - システム統合**
  - [main処理説明書](design/detailed_design/processing/phase5/main_processing_spec.md) - システムメイン
  - [system_controller処理説明書](design/detailed_design/processing/phase5/system_controller_processing_spec.md) - システムオーケストレーション
  - [scheduler処理説明書](design/detailed_design/processing/phase5/scheduler_processing_spec.md) - タスクスケジューリング
- **Phase 6 - エラーハンドリング・モニタリング**
  - [error_handler処理説明書](design/detailed_design/processing/phase6/error_handler_processing_spec.md) - エラー処理・自動復旧
  - [monitoring処理説明書](design/detailed_design/processing/phase6/monitoring_processing_spec.md) - システム監視
- **Phase 7 - CLI拡張**
  - [cli処理説明書](design/detailed_design/processing/phase7/cli_processing_spec.md) - CLI インターフェース
  - [batch_runner処理説明書](design/detailed_design/processing/phase7/batch_runner_processing_spec.md) - バッチ処理
- **追加アプリケーション**
  - [simple_observer処理説明書](design/detailed_design/processing/simple_observer_processing_spec.md) - シンプル観測アプリ

#### 🛠️ 設計規約・ガイドライン
- [設計文書ガイド](design/README.md) - 設計文書の分類・プロセス
- [設計文書標準規約](design/design_document_standards.md) - 設計書作成ルール
- [コメント記載標準ガイド](design/COMMENT_STYLE_GUIDE.md) - Pythonコメント規約

### 🚀 デプロイ・運用

#### 📦 デプロイメント
- [Hailo 8L NPUデプロイガイド](deployment/HAILO_DEPLOYMENT_GUIDE.md) - NPU環境構築

#### 📖 運用ガイド
- [CLI使用ガイド](operations/CLI_USAGE.md) - コマンドラインインターフェース操作方法
- [Simple Observer使用ガイド](operations/simple_observer_usage.md) - シンプル観測アプリケーション使用方法
- [昆虫観測クイックガイド](operations/insect_observation_quick_guide.md) - 観測手順のクイックリファレンス

### 🧪 その他

#### 🔧 トラブルシューティング
- [トラブルシューティングガイド](troubleshooting.md) - カメラ・システム問題の解決方法

#### 🔬 調査・研究資料
- `research/` - 調査・研究資料（現在空）

#### 📚 参考資料
- [Hugging Faceモデルカード](references/huggingface_model_card.md) - 学習済みモデル情報

## 📌 重要ファイル

### プロジェクトルートの重要ファイル
- **CLAUDE.md** - プロジェクト全体のルール・ガイドライン定義
- **README.md** - プロジェクト概要・使用方法
- **requirements.txt** - Python依存関係

### 本ディレクトリの役割
技術文書の一元管理・体系的整理

## 📝 文書管理方針

- 全ての技術文書はこのディレクトリで一元管理
- 文書のバージョン管理はGitで実施
- 重要な変更は文書内に変更履歴を記録
- 英語ファイル名、日本語内容で統一
- **文書管理標準規約**: [document_management_standards.md](document_management_standards.md) - 汎用的なドキュメント管理ルール
- **設計書作成ルール**: [design_document_standards.md](design/design_document_standards.md) - 設計書作成の標準規約・テンプレート
- **コメント記載ルール**: [COMMENT_STYLE_GUIDE.md](design/COMMENT_STYLE_GUIDE.md) - Pythonコードコメント規約

## 📚 文書の読み方

### 初めてプロジェクトに参加する場合
1. [要件定義書](requirements/) - プロジェクトの目的・要求事項
2. [基本設計書](design/basic_design/) - システム全体の理解
3. [詳細設計書](design/detailed_design/) - 実装の詳細

### 実装時の参照順序
1. [詳細設計書](design/detailed_design/) - 実装仕様の確認
2. [データ設計書](design/basic_design/data/) - データモデルの理解
3. [インターフェース設計書](design/basic_design/interface/) - API仕様の確認

## 🚧 実装進捗状況

### ✅ 完了済みフェーズ

#### Phase 1: 基盤モジュール (完了)
**実装済みモジュール:**
- `models/` - データモデル定義
  - `detection_models.py` - 検出結果データクラス
  - `activity_models.py` - 活動量データクラス
- `config/` - システム設定管理
  - `config_manager.py` - 設定ファイル管理
  - `system_config.json` - システム設定ファイル
- `utils/` - ユーティリティ関数
  - `data_validator.py` - データ検証機能
  - `logger.py` - ログ機能

#### Phase 2: ハードウェア制御 (完了)
**実装済みモジュール:**
- `hardware_controller.py` - 統合ハードウェア制御
- `camera_controller.py` - カメラ制御（Raspberry Pi Camera V3 NoIR対応）
- `led_controller.py` - IR LED制御（HAT対応）

#### Phase 3: 検出機能 (完了)
**実装済みモジュール:**
- `insect_detector.py` - YOLOv8ベース昆虫検出
- `detection_processor.py` - 検出結果フィルタリング・処理
- `model_manager.py` - Hugging Face モデル管理

#### Phase 4: 活動量解析 (完了)
**実装済みモジュール:**
- `activity_calculator.py` - 移動距離・活動量算出
- `data_processor.py` - 時系列データ前処理・異常値検出
- `visualization.py` - グラフ・チャート・ダッシュボード生成

#### Phase 5: システム統合 (完了)
**実装済みモジュール:**
- `main.py` - システムメインコントローラー（3つの動作モード対応）
- `system_controller.py` - モジュール間オーケストレーション・健全性監視
- `scheduler.py` - 定期実行スケジューラー・タスク管理

#### Phase 6: エラーハンドリング・モニタリング強化 (完了)
**実装済みモジュール:**
- `error_handler.py` - 統合エラーハンドリング・自動復旧機能
  - 4段階エラーレベル、エラー分類・統計、自動リトライ戦略
- `monitoring.py` - システム監視・メトリクス収集機能
  - CPU/メモリ/ディスク監視、ハードウェア健全性チェック、アラート管理
- エラー処理統合: `main.py`, `system_controller.py`, `insect_detector.py`
- 監視設定追加: `config/system_config.json`

#### Phase 7: CLI インターフェース拡張 (完了)
**実装済みモジュール:**
- `cli.py` - 拡張CLIインターフェース（Click + Rich使用）
  - 対話モード、詳細なシステム診断、リアルタイム監視
- `batch_runner.py` - バッチ処理・スケジューリング機能
  - cron連携、ジョブ管理、定期実行スケジューラー
- `CLI_USAGE.md` - CLI使用ガイド（詳細なコマンド説明）
- `test_cli.py` - CLI機能テストスクリプト

### ✅ プロジェクト完了状況

**全Phase実装完了 (Phase 1-7):**
- ✅ Phase 1: 基盤モジュール
- ✅ Phase 2: ハードウェア制御
- ✅ Phase 3: 検出機能
- ✅ Phase 4: 活動量解析
- ✅ Phase 5: システム統合
- ✅ Phase 6: エラーハンドリング・モニタリング強化
- ✅ Phase 7: CLI インターフェース拡張

### 🔄 次のステップ

**後任者向けガイド:**

1. **システム理解**
   - `CLAUDE.md` - プロジェクトルール・コーディング規約
   - `requirements/` - 要件定義書で機能要求を理解
   - `design/basic_design/` - システム全体構成を把握

2. **開発環境セットアップ**
   - Python 3.10+ 環境構築
   - `pip install -r requirements.txt` で依存関係インストール
   - Hugging Face アカウント設定（モデルダウンロード用）

3. **システム動作確認**
   ```bash
   # 単発検出テスト
   python main.py --mode single
   
   # 連続動作モード
   python main.py --mode continuous
   
   # 分析モード
   python main.py --mode analysis --date YYYY-MM-DD
   ```

4. **システム運用開始**
   - 全Phase実装完了により、システムは本格運用可能
   - 24時間連続動作対応
   - 統合監視・エラー処理による安定運用

5. **重要な設定ファイル**
   - `config/system_config.json` - システム動作設定
   - `CLAUDE.md` - 開発ガイドライン
   - `logs/` - システムログ出力先

6. **処理説明書作成状況**
   - **Phase 1処理説明書**: [processing/phase1/](design/detailed_design/processing/phase1/) - 基盤モジュール6ファイルの処理説明書作成完了
     - `detection_models_processing_spec.md` - 検出結果データクラス仕様
     - `activity_models_processing_spec.md` - 活動量データクラス仕様
     - `system_models_processing_spec.md` - システム設定データクラス仕様
     - `config_manager_processing_spec.md` - 設定管理クラス仕様
     - `data_validator_processing_spec.md` - データ検証クラス仕様
     - `file_naming_processing_spec.md` - ファイル命名規則クラス仕様
   - **Phase 2処理説明書**: [processing/phase2/](design/detailed_design/processing/phase2/) - ハードウェア制御3ファイルの処理説明書作成完了
     - `hardware_controller_processing_spec.md` - 統合ハードウェア制御クラス仕様
     - `camera_controller_processing_spec.md` - Raspberry Pi Camera V3 NoIR制御クラス仕様
     - `led_controller_processing_spec.md` - IR LED Ring Light制御クラス仕様
   - **Phase 3処理説明書**: [processing/phase3/](design/detailed_design/processing/phase3/) - 検出機能3ファイルの処理説明書作成完了
     - `insect_detector_processing_spec.md` - YOLOv8昆虫検出クラス仕様
     - `detection_processor_processing_spec.md` - 検出結果後処理クラス仕様
     - `model_manager_processing_spec.md` - YOLOモデル管理クラス仕様
   - **Phase 4-7処理説明書**: 未作成
     - Phase 4: `activity_calculator.py`, `data_processor.py`, `visualization.py`
     - Phase 5: `main.py`, `system_controller.py`, `scheduler.py`
     - Phase 6: `error_handler.py`, `monitoring.py`
     - Phase 7: `cli.py`, `batch_runner.py`

### 🆕 シンプル観測アプリケーション (simple_observer.py)

**概要**: 既存システムを変更せずに追加された軽量観測ツール

#### 新規追加ファイル
- **`simple_observer.py`** - シンプル継続観測アプリケーション
  - 既存の`insect_detector.py`を内部で呼び出し
  - CSV形式での観測データ自動保存
  - コマンドライン引数による簡単設定
  - Ctrl+Cによる安全停止機能
- **使用ガイド**: [simple_observer_usage.md](operations/simple_observer_usage.md) - 詳細な使用ガイド
  - コマンドライン引数の説明
  - CSV出力フォーマット仕様
  - 実行例とトラブルシューティング

#### 関連ドキュメント
- **ソフトウェア設計書**: [`software/software_design.md`](design/detailed_design/software/software_design.md) 第9章
  - SimpleObserverクラス設計
  - データ構造・処理フロー設計
  - 性能・品質要件・拡張性設計
- **詳細設計書**: [`processing/simple_observer_processing_spec.md`](design/detailed_design/processing/simple_observer_processing_spec.md)
  - 全12関数の詳細仕様（入力・出力・例外処理）
  - ObservationRecordデータ構造
  - 処理フロー図（アプリケーション全体・観測ループ・エラー処理）
  - 実装メモ・パフォーマンス考慮事項

#### 使用方法
```bash
# 基本実行（60秒間隔、無制限）
python simple_observer.py

# カスタム設定（30秒間隔、1時間観測）
python simple_observer.py --interval 30 --duration 3600

# 出力先指定
python simple_observer.py --output-dir ./my_observations
```

#### CSV出力データ
8列のデータ構造で観測結果を記録：
- `timestamp`: 観測時刻（ISO形式）
- `detection_count`: 検出昆虫数
- `has_detection`: 検出有無（True/False）
- `confidence_avg`: 平均信頼度
- `x_center_avg`, `y_center_avg`: 座標平均値
- `processing_time_ms`: 処理時間（ミリ秒）
- `observation_number`: 観測連番

#### 設計思想
- **既存システム保護**: main.py、insect_detector.py完全無変更
- **シンプル操作**: 最小限のコマンドライン引数
- **堅牢性**: エラー発生時の観測継続
- **データ完整性**: CSV書き込みの確実性保証

**注意事項:**
- モデルファイルはHugging Face からダウンロード（GitHub未格納）
- ハードウェアはRaspberry Pi + Camera V3 NoIR + IR LED HAT構成
- 全モジュールは単体テスト機能付き（各ファイルの`if __name__ == "__main__"`部分）
- **処理説明書**: 各ソースファイルの関数別処理内容・入出力インターフェースを詳細記述

## 🔄 更新履歴

| 日付 | 内容 | 更新者 |
|------|------|--------|
| 2025-12-25 | **書籍掲載準備: トップレベルmdファイルをdocs/に移動・包括的索引追加** | 開発チーム |
| 2025-12-25 | CLI_USAGE.md, COMMENT_STYLE_GUIDE.md, simple_observer_usage.mdをdocs/に移動 | 開発チーム |
| 2025-12-25 | docs/README.mdに全ドキュメントの詳細索引を追加 | 開発チーム |
| 2025-08-13 | **simple_observer.py 追加・包括的ドキュメント整備** | 開発チーム |
| 2025-08-13 | シンプル観測アプリケーション実装・使用ガイド作成 | 開発チーム |
| 2025-08-13 | ソフトウェア設計書第9章・詳細設計書作成完了 | 開発チーム |
| 2025-08-13 | Phase 7 CLI処理説明書・機能仕様書作成完了 | 開発チーム |
| 2025-07-29 | **Phase 6完了・全Phase実装完了** | 開発チーム |
| 2025-07-29 | エラーハンドリング・モニタリング強化機能実装 | 開発チーム |
| 2025-07-28 | Phase 3処理説明書作成完了（検出機能3ファイル） | 開発チーム |
| 2025-07-28 | Phase 2処理説明書作成完了（ハードウェア制御3ファイル） | 開発チーム |
| 2025-07-28 | Phase 1処理説明書作成完了（基盤モジュール6ファイル） | 開発チーム |
| 2025-07-28 | Phase 7完了・CLI拡張機能実装完了 | 開発チーム |
| 2025-07-28 | Phase 5完了・実装進捗状況を追加 | 開発チーム |
| 2025-07-27 | CLAUDE.mdをプロジェクトルートに移動 | 開発チーム |
| 2025-07-27 | 設計文書を基本設計・詳細設計に分類 | 開発チーム |
| 2025-07-27 | 文書構造の整理・docsディレクトリ作成 | 開発チーム |