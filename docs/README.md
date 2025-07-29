# 📚 昆虫自動観察システム - ドキュメント

このディレクトリには、昆虫自動観察＆ログ記録アプリケーションの技術文書が格納されています。

## 📋 ドキュメント構成

### 📖 要件・仕様書
- `requirements/` - 要件定義書
- `specifications/` - システム仕様書

### 🎨 設計書
- `design/` - 設計文書
  - `basic_design/` - 基本設計書（システム構成・外部仕様）
  - `detailed_design/` - 詳細設計書（実装仕様・クラス設計）

### 🚀 デプロイ・運用
- `deployment/` - デプロイメント文書
- `operations/` - 運用ガイド

### 🧪 その他
- `research/` - 調査・研究資料
- `references/` - 参考資料

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
- **設計書作成ルール**: [design_document_standards.md](design/design_document_standards.md) - 設計書作成の標準規約・テンプレート

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

**注意事項:**
- モデルファイルはHugging Face からダウンロード（GitHub未格納）
- ハードウェアはRaspberry Pi + Camera V3 NoIR + IR LED HAT構成
- 全モジュールは単体テスト機能付き（各ファイルの`if __name__ == "__main__"`部分）
- **処理説明書**: 各ソースファイルの関数別処理内容・入出力インターフェースを詳細記述

## 🔄 更新履歴

| 日付 | 内容 | 更新者 |
|------|------|--------|
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