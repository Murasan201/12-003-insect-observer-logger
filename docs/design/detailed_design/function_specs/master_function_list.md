# 統合関数一覧マスターファイル

**文書番号**: 12-002-FUNC-MASTER  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: 統合関数一覧マスターファイル  
**対象範囲**: 全プロジェクトモジュール (Phase 1-7)  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 文書概要

### 目的
昆虫自動観察＆ログ記録アプリの全モジュール（Phase 1-7）における関数・メソッドの統合一覧を提供し、詳細設計仕様書として活用する。

### 構成
- 各フェーズ別の関数統計
- モジュール別関数分布
- 主要処理フローの関数連携
- 依存関係と相互連携

---

## 📊 全体統計サマリー

### フェーズ別関数統計

| フェーズ | 説明 | モジュール数 | 関数数 | 主要クラス |
|---------|-----|-----------|--------|-----------|
| **Phase 1** | 基盤モジュール | 6 | 58 | ConfigManager, データクラス群 |
| **Phase 2** | ハードウェア制御 | 1 | 16 | HardwareController |
| **Phase 3** | 検出モジュール | 3 | 39 | ModelManager, InsectDetector |
| **Phase 4** | 分析・可視化 | 3 | 42 | ActivityCalculator, Visualizer |
| **Phase 5** | システム統合・制御 | 3 | 42 | InsectObserverSystem, SystemController |
| **Phase 6** | エラーハンドリング・監視 | 2 | 30 | ErrorHandler, SystemMonitor |
| **Phase 7** | CLI・ユーザーインターフェース | 2 | 32 | CLIController, BatchRunner |

**総モジュール数**: 20モジュール  
**総関数数**: 259関数

---

## 🔧 モジュール別詳細統計

### Phase 1: 基盤モジュール (58関数)

| モジュール | 関数数 | 主要機能 |
|-----------|--------|----------|
| config_manager.py | 13 | 設定管理・検証・バックアップ |
| detection_models.py | 13 | 検出結果データクラス・統計 |
| activity_models.py | 12 | 活動量データクラス・指標算出 |
| system_models.py | 11 | システム設定・状態データクラス |
| data_validator.py | 9 | データ検証・妥当性チェック |
| file_naming.py | 10 | ファイル命名・管理機能 |

### Phase 2: ハードウェア制御 (16関数)

| モジュール | 関数数 | 主要機能 |
|-----------|--------|----------|
| hardware_controller.py | 16 | カメラ・LED制御・ハードウェア管理 |

### Phase 3: 検出モジュール (39関数)

| モジュール | 関数数 | 主要機能 |
|-----------|--------|----------|
| model_manager.py | 11 | YOLOv8モデル管理・ダウンロード |
| insect_detector.py | 14 | 昆虫検出・画像処理・結果生成 |
| detection_processor.py | 14 | 検出データ処理・品質向上 |

### Phase 4: 分析・可視化 (42関数)

| モジュール | 関数数 | 主要機能 |
|-----------|--------|----------|
| activity_calculator.py | 15 | 活動量算出・統計分析・異常検知 |
| data_processor.py | 14 | データクリーニング・正規化・集約 |
| visualization.py | 13 | グラフ作成・ダッシュボード・レポート |

### Phase 5: システム統合・制御 (42関数)

| モジュール | 関数数 | 主要機能 |
|-----------|--------|----------|
| main.py | 16 | メインシステム制御・ループ実行 |
| system_controller.py | 16 | 統合ワークフロー・健全性チェック |
| scheduler.py | 20 | スケジューリング・タスク管理 |

### Phase 6: エラーハンドリング・監視 (30関数)

| モジュール | 関数数 | 主要機能 |
|-----------|--------|----------|
| error_handler.py | 14 | エラー処理・通知・復旧機能 |
| monitoring.py | 16 | システム監視・アラート・データ収集 |

### Phase 7: CLI・ユーザーインターフェース (32関数)

| モジュール | 関数数 | 主要機能 |
|-----------|--------|----------|
| cli.py | 15 | コマンドライン・対話的操作・表示 |
| batch_runner.py | 17 | バッチ処理・スケジューリング・ジョブ管理 |

---

## 🔄 主要処理フロー・関数連携

### 1. システム初期化フロー
```
ConfigManager.load_config → 
HardwareController.initialize_hardware → 
ModelManager.setup_model → 
InsectObserverSystem.initialize_system
```

### 2. 検出処理フロー
```
HardwareController.capture_image → 
InsectDetector.detect_single_image → 
DetectionProcessor.process_detection_record → 
ActivityCalculator.calculate_activity_metrics
```

### 3. 分析・可視化フロー
```
DataProcessor.process_detection_data → 
ActivityCalculator.calculate_activity_metrics → 
Visualizer.create_activity_chart → 
Visualizer.generate_report_pdf
```

### 4. エラー処理・監視フロー
```
ErrorHandler.handle_detection_error → 
SystemMonitor.check_system_health → 
ErrorHandler.send_error_notification → 
ErrorHandler.recover_from_error
```

### 5. CLI・バッチ処理フロー
```
CLIController.initialize_system → 
BatchRunner.run_scheduler → 
BatchRunner._run_job → 
CLIController.show_system_status
```

---

## 🏗️ アーキテクチャ層別関数分布

### データ層 (44関数)
- **データクラス**: detection_models.py (13), activity_models.py (12), system_models.py (11)
- **データ検証**: data_validator.py (9)

### ビジネスロジック層 (124関数)
- **検出処理**: insect_detector.py (14), detection_processor.py (14)
- **分析処理**: activity_calculator.py (15), data_processor.py (14)
- **システム制御**: main.py (16), system_controller.py (16), scheduler.py (20)
- **ハードウェア制御**: hardware_controller.py (16)
- **モデル管理**: model_manager.py (11)
- **可視化**: visualization.py (13)

### インフラストラクチャ層 (58関数)
- **設定管理**: config_manager.py (13)
- **ファイル管理**: file_naming.py (10)
- **エラー処理**: error_handler.py (14)
- **監視**: monitoring.py (16)

### プレゼンテーション層 (32関数)
- **CLI**: cli.py (15)
- **バッチ処理**: batch_runner.py (17)

---

## 📈 機能別関数分類

### データ管理機能 (67関数)
- **データ入出力**: 18関数 (ファイル読み書き・保存・復元)
- **データ検証**: 15関数 (妥当性チェック・整合性確認)
- **データ変換**: 20関数 (形式変換・正規化・クリーニング)
- **データ集約**: 14関数 (統計算出・サマリー生成)

### システム制御機能 (78関数)
- **初期化・終了**: 20関数 (システム起動・停止・クリーンアップ)
- **ワークフロー実行**: 25関数 (検出・分析・処理フロー)
- **スケジューリング**: 18関数 (定期実行・タスク管理)
- **状態管理**: 15関数 (システム状態・健全性チェック)

### ハードウェア・I/O機能 (35関数)
- **ハードウェア制御**: 16関数 (カメラ・LED・センサー)
- **ファイル操作**: 12関数 (ファイル命名・管理・権限)
- **外部システム連携**: 7関数 (cron・systemd・通知)

### ユーザーインターフェース機能 (32関数)
- **CLI操作**: 15関数 (コマンド実行・対話処理)
- **バッチ処理**: 17関数 (ジョブ管理・スケジューリング)

### エラー処理・監視機能 (30関数)
- **エラーハンドリング**: 14関数 (エラー処理・復旧・通知)
- **システム監視**: 16関数 (メトリクス取得・アラート・レポート)

### 分析・可視化機能 (28関数)
- **統計分析**: 15関数 (活動量算出・トレンド分析)
- **可視化**: 13関数 (グラフ・ダッシュボード・レポート)

---

## 🔗 モジュール間依存関係

### 中核依存関係
```
config_manager.py ← 全モジュール (設定読み込み)
detection_models.py ← 検出・分析系モジュール (データ構造)
error_handler.py ← 全モジュール (エラー処理)
```

### 処理フロー依存関係
```
hardware_controller.py → insect_detector.py → detection_processor.py
detection_processor.py → activity_calculator.py → visualization.py
system_controller.py → main.py → cli.py
scheduler.py → batch_runner.py
```

### ユーティリティ依存関係
```
data_validator.py ← データ処理系モジュール
file_naming.py ← ファイル出力系モジュール
monitoring.py ← システム制御系モジュール
```

---

## 📝 実装パターン・設計原則

### 共通実装パターン

#### データクラスパターン (36関数)
- `__init__`: 初期化処理
- `to_dict`: 辞書形式変換
- `from_dict`: 辞書からの復元
- `validate`: 妥当性検証

#### 管理クラスパターン (65関数)
- `initialize_*`: 初期化処理
- `cleanup_*`: クリーンアップ処理
- `get_*_status`: 状態取得
- `perform_*`: 主処理実行

#### 処理クラスパターン (89関数)
- `process_*`: メイン処理
- `_prepare_*`: 前処理
- `_cleanup_*`: 後処理
- `_validate_*`: 検証処理

#### ユーティリティパターン (45関数)
- `create_*`: 生成処理
- `save_*`: 保存処理
- `load_*`: 読み込み処理
- `export_*`: エクスポート処理

### 設計原則の適用

#### 単一責任の原則
- 各モジュールが明確な責任を持つ
- 関数レベルでの責任分離

#### 開放閉鎖の原則  
- プラグイン形式の拡張機能
- インターフェース統一による拡張性

#### 依存性逆転の原則
- 設定ベースの依存性注入
- 抽象化レイヤーによる疎結合

---

## 🔧 拡張・カスタマイズポイント

### 関数拡張ポイント (38箇所)
- **検出アルゴリズム拡張**: InsectDetector (6関数)
- **分析手法拡張**: ActivityCalculator (8関数)
- **可視化拡張**: Visualizer (7関数)
- **CLI コマンド拡張**: CLIController (5関数)
- **バッチジョブ拡張**: BatchRunner (4関数)
- **監視項目拡張**: SystemMonitor (8関数)

### プラグイン対応関数 (15関数)
- `register_*_callback`: コールバック登録
- `load_*_plugin`: プラグイン読み込み
- `extend_*_functionality`: 機能拡張

---

## 📚 関連文書リンク

### 個別フェーズ仕様書
- [Phase 1-3 モジュール関数一覧](./phase1-3_function_list.md)
- [Phase 4-5 モジュール関数一覧](./phase4-5_function_list.md)
- [Phase 6-7 モジュール関数一覧](./phase6-7_function_list.md)

### 処理仕様書
- [Phase 1 処理説明書](../processing/phase1/README.md)
- [Phase 2 処理説明書](../processing/phase2/README.md)
- [Phase 3 処理説明書](../processing/phase3/README.md)
- [Phase 4 処理説明書](../processing/phase4/README.md)
- [Phase 5 処理説明書](../processing/phase5/README.md)
- [Phase 6 処理説明書](../processing/phase6/README.md)
- [Phase 7 処理説明書](../processing/phase7/README.md)

### 設計文書
- [基本設計書: システムアーキテクチャ設計](../../basic_design/system_architecture_design.md)
- [基本設計書: ソフトウェア設計](../../basic_design/software_design.md)
- [要件定義書](../../../requirements/12-002_昆虫自動観察＆ログ記録アプリ_要件定義書.md)

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成・全フェーズ統合関数一覧 |

---

## 📋 実装進捗管理

### 実装ステータス
- ✅ **Phase 1**: 基盤モジュール (58/58関数) - 100%完了
- ✅ **Phase 2**: ハードウェア制御 (16/16関数) - 100%完了  
- ✅ **Phase 3**: 検出モジュール (39/39関数) - 100%完了
- ✅ **Phase 4**: 分析・可視化 (42/42関数) - 100%完了
- ✅ **Phase 5**: システム統合・制御 (42/42関数) - 100%完了
- 🔄 **Phase 6**: エラーハンドリング・監視 (15/30関数) - 50%完了
- 🔄 **Phase 7**: CLI・ユーザーインターフェース (17/32関数) - 53%完了

**全体進捗**: 229/259関数 (88%完了)

### 次回実装優先度
1. **高優先度**: Phase 6 エラーハンドリング機能
2. **中優先度**: Phase 7 CLI拡張機能  
3. **低優先度**: 追加分析・可視化機能

---

## 💡 開発チーム向けメモ

### コードレビューポイント
- インターフェース一貫性の確認
- エラーハンドリングの適切性
- ログ出力の統一性
- 型ヒントの完全性

### テスト実装要件
- 各関数の単体テスト
- モジュール間結合テスト
- エンドツーエンドテスト
- パフォーマンステスト

### ドキュメント保守
- 関数追加時の一覧更新
- インターフェース変更時の同期
- 実装進捗の定期更新