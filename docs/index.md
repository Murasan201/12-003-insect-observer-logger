# 🐛 昆虫自動観察＆ログ記録アプリ - ドキュメントインデックス

プロジェクト「12-002-insect-observer-logger」の技術文書一覧です。

## 📋 要件・仕様

### 📝 要件定義書
- [日本語要件定義書](requirements/12-002_昆虫自動観察＆ログ記録アプリ_要件定義書.md) - 現行プロジェクトの要件定義
- [英語要件仕様書](requirements/insect_detection_application_test_project_requirements_spec.md) - ベースプロジェクトの要件

### 📊 仕様書
- [システム仕様書](specifications/system_specification.md) - システム全体の仕様

## 🎨 設計文書

### 📐 基本設計書
システムの全体構造・外部仕様を定義する上位設計
- [🏗️ アーキテクチャ設計](design/basic_design/architecture/system_architecture_design.md) - システム全体構造
- [🔧 ハードウェア設計](design/basic_design/hardware/hardware_design.md) - 電気回路・物理設計  
- [📊 データ設計](design/basic_design/data/data_design.md) - データモデル・ファイル形式
- [🖥️ インターフェース設計](design/basic_design/interface/interface_design.md) - UI・API設計

### 🔧 詳細設計書
実装レベルの具体的な設計を定義する下位設計
- [💻 ソフトウェア設計](design/detailed_design/software/software_design.md) - モジュール・クラス設計
- [📋 クラス図設計](design/detailed_design/software/class_diagram_design.md) - PlantUMLクラス図

### 📚 設計文書ガイド
- [設計文書概要](design/README.md) - 設計文書の分類・プロセス
- [基本設計書ガイド](design/basic_design/README.md) - 基本設計の読み方
- [詳細設計書ガイド](design/detailed_design/README.md) - 詳細設計の読み方

## 🚀 デプロイ・運用

### 📦 デプロイメント
- [Hailo 8L NPUデプロイガイド](deployment/HAILO_DEPLOYMENT_GUIDE.md) - NPU環境構築

## 📚 参考資料

### 🤖 機械学習モデル
- [Hugging Faceモデルカード](references/huggingface_model_card.md) - 学習済みモデル情報

### ⚙️ プロジェクト管理
- [CLAUDE.md](../CLAUDE.md) - Claude AIへの指示・ルール（プロジェクトルート）

## 🔄 文書管理

### バージョン管理
- 全文書はGitでバージョン管理
- 重要な変更は各文書内に履歴記録

### 更新ルール
- 英語ファイル名、日本語内容で統一
- マークダウン形式（.md）で作成
- 文書間の参照は相対パスで記述

## 📞 問い合わせ

技術的な質問や文書の更新については、開発チームまでお問い合わせください。

---
最終更新: 2025-07-27 | 更新者: 開発チーム