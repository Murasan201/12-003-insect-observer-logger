# システム仕様書

**プロジェクト**: 昆虫検出トレーニングプロジェクト
**バージョン**: 1.0
**日付**: 2025-07-03
**作成者**: 開発チーム

---

## 1. 概要

本書は、昆虫検出トレーニングプロジェクトの包括的な技術仕様を提供します。本システムは、カブトムシ検出用のカスタムモデルを学習するためのYOLOv8ベースの機械学習システムです。モデルの学習、検証、およびCPUベースの推論環境に最適化されたデプロイワークフローを包含しています。

---

## 2. システム概要

### 2.1 目的
本システムは以下を目的として設計されています：
- 昆虫（カブトムシ）検出用のカスタムYOLOv8モデルの学習
- 効率的なCPUベースの推論機能の提供
- 包括的なログ記録を伴う自動化された学習ワークフローのサポート
- リソース制約のある環境でのモデルデプロイの実現

### 2.2 アーキテクチャ
```
┌─────────────────────────────────────────────────────────────┐
│                    学習パイプライン                          │
├─────────────────────────────────────────────────────────────┤
│  データセット → 前処理 → 学習 → 検証 → エクスポート         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   推論パイプライン                          │
├─────────────────────────────────────────────────────────────┤
│    入力画像 → 検出 → 可視化 → 出力                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. プロジェクト構成

### 3.1 ディレクトリ構成

```
insect-detection-training/
├── 📁 コアコンポーネント
│   ├── detect_insect.py               # メイン検出スクリプト
│   ├── train_yolo.py                  # 学習スクリプト
│   ├── yolov8_training_colab.ipynb   # Jupyter学習ノートブック
│   └── requirements.txt               # Python依存関係
│
├── 📁 設定・ドキュメント
│   ├── CLAUDE.md                      # プロジェクトルール・ガイドライン
│   ├── README.md                      # プロジェクトドキュメント
│   ├── system_specification.md       # 技術仕様書
│   ├── LICENSE                        # プロジェクトライセンス
│   └── .gitignore                     # Git除外ルール
│
├── 📁 学習データ (datasets/)
│   ├── train/
│   │   ├── images/                    # 学習用画像
│   │   └── labels/                    # 学習用ラベル（YOLO形式）
│   ├── valid/
│   │   ├── images/                    # 検証用画像
│   │   └── labels/                    # 検証用ラベル
│   ├── test/
│   │   ├── images/                    # テスト用画像
│   │   └── labels/                    # テスト用ラベル
│   └── data.yaml                      # データセット設定
│
├── 📁 ローカルテスト環境
│   ├── input_images/                  # 🔍 検出用入力画像
│   │   ├── 08-03.jpg                  # サンプルカブトムシ画像（2.0MB）
│   │   ├── 20240810_130054-1600x1200-1-853x640.jpg
│   │   ├── 86791_ext_04_0.jpg
│   │   ├── insect_catching_1220x752.jpg
│   │   └── point_thumb01.jpg
│   │
│   ├── output_images/                 # 📤 検出結果（PNG形式）
│   │   ├── 08-03.png                  # バウンディングボックス付き処理済み画像
│   │   ├── 20240810_130054-1600x1200-1-853x640.png
│   │   ├── 86791_ext_04_0.png
│   │   ├── insect_catching_1220x752.png
│   │   └── point_thumb01.png
│   │
│   ├── weights/                       # 🤖 学習済みモデルファイル
│   │   ├── best.pt                    # 最良モデル重み（6.3MB）
│   │   └── best.onnx                  # ONNXエクスポート（12.3MB）
│   │
│   └── logs/                          # 📊 検出ログ
│       └── detection_log_YYYYMMDD_HHMMSS.csv
│
└── 📁 開発・ビルド
    ├── .git/                          # Gitリポジトリ
    ├── .claude/                       # Claude Code設定
    └── .mcp.json                      # MCP設定
```

### 3.2 ディレクトリの目的

#### 3.2.1 学習データ (`datasets/`)
- **サイズ**: train/valid/test分割で500枚以上のカブトムシ画像
- **形式**: YOLO形式（正規化座標）
- **ソース**: Roboflowデータセット（CC BY 4.0ライセンス）
- **状態**: Gitから除外（.gitignore）

#### 3.2.2 ローカルテスト環境
- **`input_images/`**: 検出テスト用の新規画像を配置
- **`output_images/`**: バウンディングボックス付きのアノテーション結果を受信
- **`weights/`**: 学習済みモデルファイル（PyTorchおよびONNX）を保存
- **`logs/`**: 検出詳細とパフォーマンスメトリクスを含むCSVログ

#### 3.2.3 ワークフロー統合
1. **学習**: Jupyterノートブックまたはtrain_yolo.pyを使用
2. **モデルエクスポート**: best.ptをweights/ディレクトリに保存
3. **ローカルテスト**: input_images/に画像を配置
4. **検出**: カスタムモデルでdetect_insect.pyを実行
5. **結果**: output_images/でアノテーション画像を確認

---

## 4. システムコンポーネント

### 4.1 コアモジュール

#### 4.1.1 学習モジュール (`train_yolo.py`)

> **⚠️ 重要な注意**: このリポジトリの`train_yolo.py`は**参照専用**です。
> 実際のモデル学習には、以下の正式版を使用してください：
> **https://github.com/Murasan201/13-002-insect-detection-training**

**目的**: YOLOv8モデルの自動学習およびファインチューニング

**主な機能**:
- 事前学習済みモデルの初期化
- カスタムデータセット統合
- 自動化された学習パイプライン
- リアルタイム進捗モニタリング
- モデル検証とメトリクスレポート

**技術仕様**:
- **フレームワーク**: Ultralytics YOLOv8
- **サポートモデル**: YOLOv8n, YOLOv8s, YOLOv8m, YOLOv8l, YOLOv8x
- **入力形式**: YOLOフォーマットアノテーション
- **出力形式**: PyTorch (.pt), ONNX, TorchScript

#### 4.1.2 検出モジュール (`detect_insect.py`)
**目的**: バッチ画像処理と昆虫検出

**主な機能**:
- マルチフォーマット画像サポート（JPEG, PNG）
- バッチ処理機能
- バウンディングボックス可視化
- パフォーマンスメトリクスログ記録

---

## 5. 学習システム詳細仕様

### 5.1 学習スクリプトアーキテクチャ

#### 5.1.1 関数概要

| 関数 | 目的 | 入力 | 出力 |
|------|------|------|------|
| `setup_logging()` | ログシステムの初期化 | なし | Loggerインスタンス |
| `validate_dataset()` | データセット構造の検証 | データセットパス | ブール検証結果 |
| `check_system_requirements()` | システム互換性チェック | なし | システム情報ログ |
| `train_model()` | モデル学習の実行 | 学習パラメータ | 学習済みモデル、結果 |
| `validate_model()` | モデル性能評価 | モデル、データセット | 検証メトリクス |
| `export_model()` | モデル形式変換 | モデル、形式 | エクスポートされたモデルファイル |

#### 5.1.2 学習パラメータ

| パラメータ | 型 | デフォルト | 説明 |
|-----------|------|---------|------|
| `--data` | str | 必須 | データセット設定へのパス（data.yaml） |
| `--model` | str | yolov8n.pt | 事前学習済みモデル選択 |
| `--epochs` | int | 100 | 学習エポック数 |
| `--batch` | int | 16 | 学習バッチサイズ |
| `--imgsz` | int | 640 | 入力画像サイズ（ピクセル） |
| `--device` | str | auto | ハードウェアデバイス（auto/cpu/gpu） |
| `--project` | str | training_results | 出力ディレクトリ名 |
| `--name` | str | beetle_detection | 実験識別子 |
| `--export` | bool | False | モデルエクスポート有効化 |
| `--validate` | bool | True | 学習後検証有効化 |

### 5.2 学習ワークフロー

#### 5.2.1 初期化フェーズ
1. **ログ設定**
   - `logs/`ディレクトリにタイムスタンプ付きログファイルを作成
   - デュアル出力（ファイル + コンソール）を設定
   - ログレベルをINFOに設定

2. **システム検証**
   - Pythonバージョン確認
   - PyTorchインストールチェック
   - CUDA利用可能性検出
   - GPU列挙と仕様
   - OpenCVバージョン確認

3. **データセット検証**
   - `data.yaml`存在確認
   - ディレクトリ構造の整合性チェック
   - train/valid/test分割のファイル数カウント
   - 画像-ラベル対応の検証

#### 5.2.2 学習フェーズ
1. **モデル初期化**
   - 事前学習済みYOLOv8重みの読み込み
   - モデルアーキテクチャの設定
   - 学習ハイパーパラメータの設定

2. **学習実行**
   - バッチデータ読み込みと拡張
   - 順伝播/逆伝播
   - 損失計算と最適化
   - チェックポイント保存（10エポックごと）
   - 検証セット評価

3. **進捗モニタリング**
   - リアルタイム損失追跡
   - 検証メトリクス計算
   - 学習時間計測
   - リソース使用率ログ記録

#### 5.2.3 検証フェーズ
1. **パフォーマンスメトリクス**
   - mAP@0.5（IoU 0.5での平均適合率）
   - mAP@0.5:0.95（IoU閾値全体での平均適合率）
   - 適合率（真陽性 / (真陽性 + 偽陽性)）
   - 再現率（真陽性 / (真陽性 + 偽陰性)）

2. **出力生成**
   - 混同行列の可視化
   - 学習/検証曲線
   - サンプル検出の可視化
   - モデルパフォーマンスサマリー

#### 5.2.4 エクスポートフェーズ
1. **形式変換**
   - クロスプラットフォームデプロイ用ONNXエクスポート
   - 本番最適化用TorchScriptエクスポート
   - モデル重み抽出

2. **ファイル整理**
   - 最良モデル重み（`best.pt`）
   - 最新チェックポイント（`last.pt`）
   - 学習設定バックアップ
   - 結果可視化ファイル

---

## 6. データセット仕様

### 6.1 データセット構造
```
datasets/
├── train/
│   ├── images/          # 400枚の学習画像
│   └── labels/          # 400個のYOLO形式ラベル
├── valid/
│   ├── images/          # 50枚の検証画像
│   └── labels/          # 50個のYOLO形式ラベル
├── test/
│   ├── images/          # 50枚のテスト画像
│   └── labels/          # 50個のテストラベル
└── data.yaml            # データセット設定
```

### 6.2 データ形式要件

#### 6.2.1 画像仕様
- **形式**: JPEG, PNG
- **解像度**: 最小640x640ピクセル推奨
- **色空間**: RGB
- **ファイル命名**: 対応するラベルファイルと一致

#### 6.2.2 ラベル形式（YOLO）
```
class_id x_center y_center width height
```
- **class_id**: 整数（'beetle'の場合は0）
- **座標**: 正規化（0.0〜1.0）
- **ファイル拡張子**: `.txt`

#### 6.2.3 設定ファイル（data.yaml）
```yaml
train: ./train/images
val: ./valid/images
test: ./test/images

nc: 1
names: ['beetle']

roboflow:
  workspace: z-algae-bilby
  project: beetle
  version: 1
  license: CC BY 4.0
  url: https://universe.roboflow.com/z-algae-bilby/beetle/dataset/1
```

---

## 8. システム要件

### 8.1 ハードウェア要件

#### 8.1.1 最小要件
- **CPU**: クアッドコアプロセッサ（Intel i5またはAMD Ryzen 5相当）
- **RAM**: 8GBシステムメモリ
- **ストレージ**: データセットとモデル用に10GB空き容量
- **GPU**: オプション（高速学習用CUDA互換）

#### 8.1.2 推奨要件
- **CPU**: 8コアプロセッサ（Intel i7またはAMD Ryzen 7）
- **RAM**: 16GB以上のシステムメモリ
- **ストレージ**: 50GB以上のSSDストレージ
- **GPU**: 6GB以上のVRAMを持つNVIDIA GPU（RTX 3060以上）

### 8.2 ソフトウェア要件

#### 8.2.1 オペレーティングシステム
- **主要**: Ubuntu 22.04 LTS（Windows 10/11上のWSL2）
- **代替**: macOS 12以上、WSL2付きWindows 10/11
- **Python**: 3.9以上（3.10.12でテスト済み）

#### 8.2.2 依存関係（検証済みバージョン）
```
# コアMLフレームワーク
torch==2.7.1                    # ディープラーニングフレームワーク
torchvision==0.22.1             # コンピュータビジョン
ultralytics==8.3.162            # YOLOv8実装

# コンピュータビジョン・画像処理
opencv-python==4.11.0.86        # コンピュータビジョンライブラリ
numpy==2.2.6                    # 数値計算
pandas==2.3.0                   # データ分析
matplotlib==3.10.3              # プロット・可視化
pillow>=11.3.0                  # 画像処理

# 追加依存関係
ultralytics-thop==2.0.14        # モデルプロファイリング
pyyaml>=5.3.1                   # 設定ファイル
tqdm>=4.65.0                    # プログレスバー
```

#### 8.2.3 インストールコマンド
```bash
# コア依存関係のインストール
pip3 install torch torchvision ultralytics opencv-python

# または全要件をインストール
pip3 install -r requirements.txt
```

#### 8.2.4 現在の環境状態
- **システム**: Linux WSL2 (Ubuntu) x86_64
- **Python**: 3.10.12（システムレベル）
- **パッケージインストール**: ユーザーレベル（~/.local/lib/python3.10/site-packages/）
- **最終確認**: 2025-07-04

---

## 9. パフォーマンス仕様

### 9.1 学習パフォーマンス

#### 9.1.1 目標メトリクス
- **学習時間**: 100エポックで2時間以下（GPU環境）
- **メモリ使用量**: 学習中8GB RAM以下
- **モデル収束**: 50-80エポック以内で損失安定化
- **検証mAP@0.5**: カブトムシ検出で0.7以上

#### 9.1.2 達成パフォーマンス（2025-07-04）
**優れた結果を達成:**
- **最終mAP@0.5**: 0.9763 (97.63%) - **目標を39.4%上回る**
- **mAP@0.5:0.95**: 0.6550 (65.50%)
- **適合率**: 0.9598 (95.98%)
- **再現率**: 0.9305 (93.05%)
- **学習プラットフォーム**: Google Colab（GPU高速化）
- **モデルサイズ**: YOLOv8 Nano (best.pt: 6.3MB)
- **学習状態**: 本番運用品質

#### 9.1.3 ハードウェア別パフォーマンス
| 構成 | 学習時間（100エポック） | メモリ使用量 | バッチサイズ |
|------|-------------------------|--------------|--------------|
| CPUのみ | 8-12時間 | 4-6 GB | 8-16 |
| RTX 3060 | 1-2時間 | 6-8 GB | 32-64 |
| RTX 4080 | 30-60分 | 8-12 GB | 64-128 |

### 9.2 推論パフォーマンス

#### 9.2.1 目標仕様
- **処理時間**: 画像1枚あたり1,000ms以下（CPU推論）
- **メモリ効率**: 推論中2GB RAM以下
- **精度目標**:
  - 真陽性率: 85%以上
  - 偽陽性率: 5%以下
  - 適合率: 0.8以上
  - 再現率: 0.8以上

#### 9.2.2 達成ローカル推論パフォーマンス（2025-07-04）
**優れたローカルパフォーマンス:**
- **平均処理時間**: 画像1枚あたり約100ms（**目標より90%高速**）
- **処理範囲**: 画像1枚あたり63.4ms - 121.2ms
- **テスト結果**: 5/5枚の画像を正常処理（100%成功率）
- **総検出数**: 5枚の画像で9匹のカブトムシを検出
- **システム**: Linux WSL2, Python 3.10.12, CPUのみ推論
- **モデル**: best.pt (6.3MB YOLOv8 Nano)
- **メモリ使用量**: システムへの影響は最小

---

## 10. 出力仕様

### 10.1 学習出力

#### 10.1.1 モデルファイル
- **best.pt**: 最良パフォーマンスモデル重み（ローカル保存）
- **last.pt**: 最終エポック重み（ローカル保存）
- **モデルエクスポート**: ONNX, TorchScript形式

#### 10.1.2 モデル配布
- **公開リポジトリ**: https://huggingface.co/Murasan/beetle-detection-yolov8
- **ライセンス**: AGPL-3.0（YOLOv8から継承）
- **利用可能形式**:
  - PyTorch形式 (best.pt, 6.26MB)
  - ONNX形式 (best.onnx, 12.3MB)
- **パフォーマンスメトリクス**: mAP@0.5: 97.63%, mAP@0.5:0.95: 89.56%

#### 10.1.3 可視化ファイル
- **results.png**: 学習/検証曲線
- **confusion_matrix.png**: 分類パフォーマンス行列
- **labels.jpg**: 正解ラベル分布
- **predictions.jpg**: モデル予測サンプル

#### 10.1.4 ログファイル
- **学習ログ**: タイムスタンプ付き学習進捗
- **CSVメトリクス**: エポックごとのパフォーマンスデータ
- **システムログ**: ハードウェア使用率とエラー

### 10.2 ファイル構成
```
training_results/
└── beetle_detection/
    ├── weights/
    │   ├── best.pt
    │   └── last.pt
    ├── plots/
    │   ├── results.png
    │   ├── confusion_matrix.png
    │   └── predictions.jpg
    └── logs/
        └── training_YYYYMMDD_HHMMSS.log
```

---

## 11. エラー処理とログ記録

### 11.1 エラー分類

#### 11.1.1 重大エラー
- データセット検証失敗
- モデル読み込みエラー
- CUDAメモリ不足エラー
- ファイルシステム権限問題

#### 11.1.2 警告状態
- 利用可能メモリ低下
- 学習収束遅延
- オプション依存関係の欠落
- 最適でないハードウェア構成

### 11.2 ログ記録仕様

#### 11.2.1 ログレベル
- **INFO**: 通常操作の進捗
- **WARNING**: 非重大な問題
- **ERROR**: 回復可能な障害
- **CRITICAL**: システム停止エラー

#### 11.2.2 ログ形式
```
YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE
```

#### 11.2.3 ログローテーション
- 学習セッションごとに新しいログファイル
- タイムスタンプベースの命名規則
- 古いログの自動クリーンアップ（30日超）

---

## 12. セキュリティ考慮事項

### 12.1 データセキュリティ
- データセットファイルはバージョン管理から除外
- 設定ファイルに機密情報なし
- モデル重みの安全な取り扱い

### 12.2 システムセキュリティ
- 全ユーザーパラメータの入力検証
- 安全なファイルパス処理
- メモリ使用量のモニタリングと制限

---

## 13. デプロイガイドライン

### 13.1 開発環境セットアップ
1. GitHubからリポジトリをクローン
2. Python仮想環境を作成
3. requirements.txtから依存関係をインストール
4. データセットをダウンロードして準備
5. システム要件を確認

### 13.2 学習実行
```bash
# 基本学習コマンド
python train_yolo.py --data datasets/data.yaml --epochs 100

# カスタムパラメータでの本番学習
python train_yolo.py \
    --data datasets/data.yaml \
    --model yolov8s.pt \
    --epochs 200 \
    --batch 32 \
    --imgsz 640 \
    --device 0 \
    --export
```

### 13.3 モデルデプロイ
1. 学習済みモデルをONNX形式にエクスポート
2. ターゲットハードウェアプラットフォーム向けに最適化
3. 推論アプリケーションと統合
4. テストデータセットでパフォーマンスを検証

---

## 14. 保守と更新

### 14.1 モデル再学習
- 推奨頻度: 新規データで月次
- モデル重みのバージョン管理
- 以前のバージョンとのパフォーマンス比較

### 14.2 システム更新
- 定期的な依存関係更新
- YOLOv8フレームワークバージョンの監視
- セキュリティパッチの適用

---

## 15. テストと検証

### 15.1 単体テスト
- データセット検証関数
- モデル読み込み/保存操作
- 設定ファイル解析
- エラー処理メカニズム

### 15.2 結合テスト
- エンドツーエンド学習パイプライン
- モデルエクスポート機能
- クロスプラットフォーム互換性
- パフォーマンスベンチマーク

### 15.3 受け入れテスト
- モデル精度検証
- パフォーマンス要件検証
- ユーザーインターフェーステスト
- ドキュメント完全性

### 15.4 本番環境テストデータ
全ての本番環境テストファイルと長時間ログ記録データは`production/`ディレクトリに保存されています。

#### 15.4.1 本番スクリプト概要

| スクリプト | 目的 | 環境 | 状態 |
|-----------|------|------|------|
| `test_logging_left_half.py` | 本番で使用されたオリジナルロギングスクリプト | Raspberry Pi | 読み取り専用 |
| `test_camera_left_half_realtime.py` | オリジナルリアルタイム検出スクリプト | Raspberry Pi | 読み取り専用 |
| `production_logging_left_half.py` | 書籍版（docstring付き） | 任意 | 編集可能 |
| `production_camera_left_half_realtime.py` | 書籍版（docstring付き） | 任意 | 編集可能 |
| `visualize_detection_data.py` | データ可視化・グラフ生成 | 任意 | 編集可能 |

#### 15.4.2 ログ記録から可視化までのワークフロー

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    本番観察ワークフロー                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  [1] 観察・ログ記録
  ┌─────────────────────────────────────┐
  │  production_logging_left_half.py    │
  │  (または test_logging_left_half.py) │
  │                                     │
  │  • カメラキャプチャ（60秒間隔）     │
  │  • YOLOv8検出                       │
  │  • CSVログ記録                      │
  │  • メタデータJSON出力               │
  └──────────────┬──────────────────────┘
                 │
                 ▼
  [2] 出力ファイル
  ┌─────────────────────────────────────┐
  │  insect_detection_logs/             │
  │                                     │
  │  ├── left_half_detection_log_*.csv  │  ← 検出データ
  │  ├── left_half_metadata_*.json      │  ← セッションパラメータ
  │  └── images/ (オプション)           │  ← 検出画像
  └──────────────┬──────────────────────┘
                 │
                 ▼
  [3] 可視化
  ┌─────────────────────────────────────┐
  │  visualize_detection_data.py        │
  │                                     │
  │  • CSVデータ読み込み                │
  │  • 時系列プロット生成               │
  │  • 累積プロット生成                 │
  │  • 時間帯別活動チャート生成         │
  │  • 統計情報出力                     │
  └──────────────┬──────────────────────┘
                 │
                 ▼
  [4] 可視化出力
  ┌─────────────────────────────────────┐
  │  *_graph.png                        │
  │                                     │
  │  • 時系列検出プロット               │
  │  • 累積検出カウント                 │
  │  • 時間帯別活動棒グラフ             │
  │    （21:00-06:00最適化）            │
  └─────────────────────────────────────┘
```

#### 15.4.3 本番スクリプト詳細

##### 15.4.3.1 ログ記録スクリプト (`production_logging_left_half.py`)

**目的**: 自動ログ記録を伴う長時間昆虫観察

**主要関数**:
| 関数 | 説明 |
|------|------|
| `setup_logging()` | CSVとメタデータファイルの初期化 |
| `save_detection_to_csv()` | 検出レコードをCSVに書き込み |
| `test_logging_left_half()` | メイン観察ループ |
| `distance_to_lens_position()` | フォーカス距離をレンズパラメータに変換 |

**コマンドラインパラメータ**:
```bash
python production_logging_left_half.py \
    --model ../weights/best.pt \      # YOLOv8モデルパス
    --conf 0.4 \                       # 信頼度閾値
    --interval 60 \                    # 観察間隔（秒）
    --duration 32400 \                 # 総時間（9時間）
    --auto-focus \                     # オートフォーカス有効化
    --save-images                      # 検出画像保存
```

##### 15.4.3.2 可視化スクリプト (`visualize_detection_data.py`)

**目的**: CSVログデータからグラフと統計を生成

**主要関数**:
| 関数 | 説明 |
|------|------|
| `load_csv_data()` | CSVファイルをDataFrameに読み込み |
| `process_detection_data()` | データ前処理（型変換、NaN処理） |
| `create_detection_plot()` | 3サブプロット可視化を生成 |
| `create_activity_heatmap()` | 複数日ヒートマップを生成（オプション） |
| `print_statistics()` | 統計サマリーを出力 |

**コマンドライン使用法**:
```bash
# 基本可視化
python visualize_detection_data.py left_half_detection_log_*.csv

# カスタム出力パス指定
python visualize_detection_data.py data.csv -o output.png

# 統計のみ（グラフなし）
python visualize_detection_data.py data.csv --stats-only

# ヒートマップ含む（複数日データ用）
python visualize_detection_data.py data.csv --heatmap
```

#### 15.4.4 CSVデータ形式仕様

**ファイル**: `left_half_detection_log_YYYYMMDD_HHMMSS.csv`

| カラム | 型 | 説明 | 例 |
|--------|------|------|-----|
| timestamp | ISO 8601 | 観察タイムスタンプ | `2025-09-04T21:39:36.674064` |
| observation_number | int | 連続観察カウント | `40` |
| detection_count | int | 検出数 | `1` |
| has_detection | bool | 検出フラグ | `True` |
| class_names | string | 検出クラス（`;`区切り） | `beetle` |
| confidence_values | string | 信頼度スコア | `0.492` |
| bbox_coordinates | string | バウンディングボックス`(x1,y1,x2,y2)` | `(103,586,1108,1296)` |
| center_x | float | 検出中心X座標 | `605.6` |
| center_y | float | 検出中心Y座標 | `941.0` |
| bbox_width | float | バウンディングボックス幅 | `1005.0` |
| bbox_height | float | バウンディングボックス高さ | `710.0` |
| area | float | バウンディングボックス面積（ピクセル²） | `713521.1` |
| detection_area | string | 監視領域 | `left_half` |
| processing_time_ms | float | 処理時間（ミリ秒） | `453.4` |
| image_saved | bool | 画像保存フラグ | `True` |
| image_filename | string | 保存画像ファイル名 | `left_half_detection_*.jpg` |

#### 15.4.5 メタデータ形式仕様

**ファイル**: `left_half_metadata_YYYYMMDD_HHMMSS.json`

```json
{
  "start_time": "2025-09-04T21:00:12.074679",
  "detection_area": "left_half",
  "area_description": "Only left 50% of camera view is monitored",
  "log_file": "/path/to/left_half_detection_log_*.csv",
  "system_info": {
    "camera": "Camera Module 3 Wide NoIR",
    "platform": "Raspberry Pi"
  },
  "focus_mode": "auto",
  "focus_distance_cm": null,
  "model_path": "../weights/best.pt",
  "confidence_threshold": 0.4,
  "resolution": "2304x1296",
  "detection_width": 1152,
  "interval_seconds": 60,
  "duration_seconds": 32400,
  "save_images": true
}
```

#### 15.4.6 実際の本番データ

以下のファイルは参照用として**gitで追跡されている本番データ**です：

| ファイル | 説明 | レコード数 | 期間 |
|----------|------|-----------|------|
| `left_half_detection_log_20250904_210012.csv` | 9時間観察データ | 538 | 21:00-06:00 |
| `left_half_detection_log_20250904_210012_graph.png` | 可視化グラフ | - | - |
| `left_half_metadata_20250904_210012.json` | 本番パラメータ | - | - |

**本番実行コマンド（推定）**:
```bash
python test_logging_left_half.py \
    --conf 0.4 \
    --interval 60 \
    --duration 32400 \
    --auto-focus \
    --save-images
```

#### 15.4.7 ファイル変更ポリシー

| カテゴリ | ファイル | ポリシー |
|----------|----------|----------|
| **オリジナルスクリプト** | `test_logging_left_half.py`, `test_camera_left_half_realtime.py` | **編集禁止** - 本番記録を保持 |
| **オリジナルデータ** | `insect_detection_logs/`内の`*.csv`, `*.json`, `*.png` | **編集禁止** - データ整合性を保持 |
| **書籍版** | `production_logging_left_half.py`, `production_camera_left_half_realtime.py` | ドキュメント用に編集可能 |
| **ユーティリティ** | `visualize_detection_data.py` | 編集可能 |

---

## 16. 付録

### 16.1 コマンドリファレンス
```bash
# ヘルプ情報表示
python train_yolo.py --help

# 最小パラメータでのクイック学習
python train_yolo.py --data datasets/data.yaml --epochs 50

# エクスポート付き高品質学習
python train_yolo.py --data datasets/data.yaml --model yolov8m.pt --epochs 200 --export

# CPUのみ学習
python train_yolo.py --data datasets/data.yaml --device cpu --batch 8
```

### 16.2 トラブルシューティングガイド

#### 16.2.1 一般的な問題
- **「Dataset not found」**: データセットディレクトリ構造を確認
- **「CUDA out of memory」**: バッチサイズを削減するかCPUを使用
- **「Permission denied」**: ファイルシステム権限を確認
- **「Import error」**: 依存関係を再インストール

#### 16.2.2 パフォーマンス最適化
- データ読み込み高速化のためSSDストレージを使用
- 利用可能メモリに基づいてバッチサイズを最適化
- GPU高速化のため混合精度学習を有効化
- 学習中は不要なアプリケーションを終了

---

*ドキュメントバージョン: 1.0*
*最終更新: 2025-07-03*
*連絡先: 開発チーム*
