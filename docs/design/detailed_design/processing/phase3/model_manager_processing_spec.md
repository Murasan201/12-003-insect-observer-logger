# model_manager.py 処理説明書

**文書番号**: 12-003-PROC-203  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: model_manager.py 処理説明書  
**対象ファイル**: `model_manager.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
YOLOv8モデルの管理・ダウンロード・検証を行い、Hugging Faceからのモデルダウンロードとローカルモデルの管理を提供する。

### 主要機能
- Hugging Faceからのモデルダウンロード
- ローカルモデルの管理・検証
- モデルバージョン管理
- モデル性能評価
- モデル変換・最適化

---

## 🔧 関数・メソッド仕様

### ModelInfo.__post_init__()

**概要**: ModelInfo データクラスの初期化後処理

**処理内容**:
1. ファイルパスの存在確認
2. ファイルサイズの計算・検証
3. バージョン文字列の妥当性チェック
4. ハッシュ値の計算（指定時）

**入力インターフェース**:
```python
def __post_init__(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 検証完了後に処理終了 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| FileNotFoundError | モデルファイルが存在しない場合 |
| ValueError | バージョン形式が不正な場合 |

### ModelManager.__init__()

**概要**: モデル管理クラスの初期化処理

**処理内容**:
1. ロガーインスタンスを取得
2. 設定管理オブジェクトの初期化
3. モデル保存ディレクトリの確認・作成
4. ローカルモデル一覧の初期化
5. Hugging Face設定の確認

**入力インターフェース**:
```python
def __init__(self, models_dir: str = "./weights", config_manager: Optional[ConfigManager] = None):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| models_dir | str | × | モデル保存ディレクトリ（デフォルト: "./weights"） |
| config_manager | Optional[ConfigManager] | × | 設定管理オブジェクト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | ModelManager | 初期化されたモデル管理オブジェクト |

**使用例**:
```python
manager = ModelManager("./models")
```

### ModelManager.download_from_huggingface()

**概要**: Hugging FaceからYOLOモデルをダウンロード

**処理内容**:
1. Hugging Face Hub ライブラリの利用可能性確認
2. リポジトリの存在確認
3. モデルファイルのダウンロード実行
4. ダウンロード完了の検証
5. モデル情報の更新

**入力インターフェース**:
```python
def download_from_huggingface(self, repo_id: str, filename: str, 
                             local_dir: Optional[str] = None) -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| repo_id | str | ○ | Hugging Face リポジトリID |
| filename | str | ○ | ダウンロードするファイル名 |
| local_dir | Optional[str] | × | 保存先ディレクトリ（None: デフォルト使用） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| model_path | str | ダウンロードされたモデルファイルパス |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ConnectionError | ネットワーク接続エラーの場合 |
| FileNotFoundError | リポジトリ・ファイルが存在しない場合 |

**使用例**:
```python
path = manager.download_from_huggingface("Murasan/beetle-detection-yolov8", "best.pt")
```

### ModelManager.verify_model()

**概要**: モデルファイルの検証

**処理内容**:
1. ファイルの存在確認
2. ファイルサイズの確認
3. YOLOモデルとしての読み込み可能性確認
4. モデル構造の検証
5. 検証結果の報告

**入力インターフェース**:
```python
def verify_model(self, model_path: str) -> Dict[str, Any]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| model_path | str | ○ | 検証対象のモデルファイルパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| verification_result | Dict[str, Any] | 検証結果辞書 |

**使用例**:
```python
result = manager.verify_model("./weights/beetle_detection.pt")
if result['valid']:
    print("モデル検証成功")
```

### ModelManager.load_model()

**概要**: YOLOモデルの読み込み

**処理内容**:
1. モデルファイルパスの検証
2. YOLO オブジェクトの作成
3. モデルの読み込み実行
4. GPU/CPU デバイスの設定
5. 読み込み完了の確認

**入力インターフェース**:
```python
def load_model(self, model_path: str, device: str = "auto") -> YOLO:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| model_path | str | ○ | モデルファイルパス |
| device | str | × | 推論デバイス（"auto", "cpu", "cuda"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| model | YOLO | 読み込まれたYOLOモデルオブジェクト |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| FileNotFoundError | モデルファイルが存在しない場合 |
| RuntimeError | モデル読み込みエラーの場合 |

**使用例**:
```python
model = manager.load_model("./weights/best.pt", "cuda")
```

### ModelManager.get_model_info()

**概要**: モデル情報の取得

**処理内容**:
1. モデルファイルの分析
2. ファイルサイズ・ハッシュ値の計算
3. モデル構造情報の取得
4. 性能メトリクスの取得（可能な場合）
5. ModelInfo オブジェクトの作成

**入力インターフェース**:
```python
def get_model_info(self, model_path: str) -> ModelInfo:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| model_path | str | ○ | モデルファイルパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| model_info | ModelInfo | モデル情報オブジェクト |

**使用例**:
```python
info = manager.get_model_info("./weights/best.pt")
print(f"モデルサイズ: {info.size_mb:.1f}MB")
```

### ModelManager.list_local_models()

**概要**: ローカルモデルの一覧取得

**処理内容**:
1. モデルディレクトリのスキャン
2. YOLOモデルファイルの検出（.pt, .onnx等）
3. 各モデルの情報取得
4. モデル一覧の生成
5. ソート済みリストの返却

**入力インターフェース**:
```python
def list_local_models(self) -> List[ModelInfo]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| models | List[ModelInfo] | ローカルモデル情報リスト |

**使用例**:
```python
models = manager.list_local_models()
for model in models:
    print(f"{model.name} - {model.version}")
```

### ModelManager.delete_model()

**概要**: モデルファイルの削除

**処理内容**:
1. 削除対象モデルの存在確認
2. モデル使用状況の確認
3. 削除確認（安全チェック）
4. ファイル削除の実行
5. 削除完了の確認

**入力インターフェース**:
```python
def delete_model(self, model_path: str, force: bool = False) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| model_path | str | ○ | 削除対象のモデルファイルパス |
| force | bool | × | 強制削除フラグ（デフォルト: False） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 削除成功可否 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| PermissionError | ファイル削除権限がない場合 |

**使用例**:
```python
success = manager.delete_model("./weights/old_model.pt")
```

### ModelManager.backup_model()

**概要**: モデルファイルのバックアップ

**処理内容**:
1. バックアップ対象モデルの存在確認
2. バックアップディレクトリの作成
3. タイムスタンプ付きファイル名生成
4. ファイルのコピー実行
5. バックアップ完了の確認

**入力インターフェース**:
```python
def backup_model(self, model_path: str, backup_dir: Optional[str] = None) -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| model_path | str | ○ | バックアップ対象のモデルファイルパス |
| backup_dir | Optional[str] | × | バックアップディレクトリ（None: 自動設定） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| backup_path | str | バックアップファイルパス |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| IOError | ファイルコピーエラーの場合 |

**使用例**:
```python
backup_path = manager.backup_model("./weights/best.pt", "./backups")
```

### ModelManager.convert_to_onnx()

**概要**: PyTorchモデルのONNX変換

**処理内容**:
1. 変換対象モデルの読み込み
2. ONNX出力設定の準備
3. モデル変換の実行
4. 変換モデルの検証
5. ONNX ファイルの保存

**入力インターフェース**:
```python
def convert_to_onnx(self, model_path: str, output_path: Optional[str] = None, 
                   input_size: Tuple[int, int] = (640, 640)) -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| model_path | str | ○ | 変換元PyTorchモデルパス |
| output_path | Optional[str] | × | ONNX出力パス（None: 自動生成） |
| input_size | Tuple[int, int] | × | 入力画像サイズ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| onnx_path | str | 変換されたONNXファイルパス |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| RuntimeError | モデル変換エラーの場合 |

**使用例**:
```python
onnx_path = manager.convert_to_onnx("./weights/best.pt", "./weights/best.onnx")
```

### ModelManager.benchmark_model()

**概要**: モデル性能ベンチマーク

**処理内容**:
1. ベンチマーク用テストデータの準備
2. 推論速度の測定
3. メモリ使用量の測定
4. CPU/GPU使用率の測定
5. ベンチマーク結果の集計

**入力インターフェース**:
```python
def benchmark_model(self, model_path: str, num_iterations: int = 100) -> Dict[str, float]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| model_path | str | ○ | ベンチマーク対象モデルパス |
| num_iterations | int | × | 測定イテレーション数 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| benchmark_results | Dict[str, float] | ベンチマーク結果辞書 |

**使用例**:
```python
results = manager.benchmark_model("./weights/best.pt", 50)
print(f"平均推論時間: {results['avg_inference_time']:.3f}ms")
```

### ModelManager.update_model_registry()

**概要**: モデルレジストリの更新

**処理内容**:
1. 現在のモデル状況の確認
2. レジストリファイルの読み込み
3. 新規・更新モデル情報の追加
4. バージョン管理情報の更新
5. レジストリファイルの保存

**入力インターフェース**:
```python
def update_model_registry(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 更新完了後に処理終了 |

**使用例**:
```python
manager.update_model_registry()
```

### ModelManager.get_recommended_model()

**概要**: 推奨モデルの取得

**処理内容**:
1. 利用可能モデルの分析
2. 性能・精度メトリクスの比較
3. システム要件との適合性確認
4. 推奨モデルの選定
5. 推奨理由の生成

**入力インターフェース**:
```python
def get_recommended_model(self, criteria: str = "balanced") -> Tuple[str, str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| criteria | str | × | 選定基準（"speed", "accuracy", "balanced"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| model_path | str | 推奨モデルパス |
| reason | str | 推奨理由 |

**使用例**:
```python
model_path, reason = manager.get_recommended_model("accuracy")
print(f"推奨モデル: {model_path}, 理由: {reason}")
```

### ModelManager.cleanup_cache()

**概要**: モデルキャッシュのクリーンアップ

**処理内容**:
1. キャッシュディレクトリの確認
2. 不要なキャッシュファイルの特定
3. 古いダウンロードファイルの削除
4. 一時ファイルのクリーンアップ
5. ディスク容量の最適化

**入力インターフェース**:
```python
def cleanup_cache(self, max_age_days: int = 30) -> Dict[str, int]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| max_age_days | int | × | キャッシュ保持期間（日） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| cleanup_stats | Dict[str, int] | クリーンアップ統計 |

**使用例**:
```python
stats = manager.cleanup_cache(7)
print(f"削除ファイル数: {stats['deleted_files']}")
```

---

## 📊 データ構造

### ModelInfo

**概要**: モデル情報を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| name | str | モデル名 |
| version | str | モデルバージョン |
| path | str | モデルファイルパス |
| size_mb | float | ファイルサイズ（MB） |
| hash_sha256 | str | SHA256ハッシュ値 |
| created_at | datetime | 作成日時 |
| performance_metrics | Dict[str, float] | 性能メトリクス |
| description | str | モデル説明 |

### ModelManager

**概要**: モデル管理クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| models_dir | Path | モデル保存ディレクトリ |
| config_manager | Optional[ConfigManager] | 設定管理オブジェクト |
| local_models | List[ModelInfo] | ローカルモデル一覧 |
| registry_file | Path | モデルレジストリファイルパス |

---

## 🔄 処理フロー

### Hugging Faceダウンロードフロー
```
1. download_from_huggingface()実行
   ↓
2. リポジトリ存在確認
   ↓
3. ファイルダウンロード
   ↓
4. 検証・レジストリ更新
   ↓
5. ダウンロード完了
```

### モデル検証フロー
```
1. verify_model()実行
   ↓
2. ファイル存在・サイズ確認
   ↓
3. YOLOモデル読み込みテスト
   ↓
4. 構造検証
   ↓
5. 検証結果生成
```

### 変換フロー
```
1. convert_to_onnx()実行
   ↓
2. PyTorchモデル読み込み
   ↓
3. ONNX変換実行
   ↓
4. 変換モデル検証
   ↓
5. ONNXファイル保存
```

### エラー処理フロー
```
モデル操作エラー発生
   ↓
例外キャッチ・ログ出力
   ↓
クリーンアップ処理
   ↓
エラー結果返却
```

---

## 📝 実装メモ

### 注意事項
- Hugging Face Hub の認証トークン管理
- 大容量モデルファイルのダウンロード進捗表示
- ネットワーク接続エラーの適切な処理
- モデルファイルの整合性検証
- ONNX変換時のメモリ使用量制御

### 依存関係
- logging（標準ライブラリ）
- hashlib（標準ライブラリ）
- json（標準ライブラリ）
- typing（標準ライブラリ）
- dataclasses（標準ライブラリ）
- pathlib（標準ライブラリ）
- datetime（標準ライブラリ）
- shutil（標準ライブラリ）
- requests（外部ライブラリ）
- urllib.parse（標準ライブラリ）
- huggingface_hub（外部ライブラリ）
- ultralytics（外部ライブラリ）
- torch（外部ライブラリ）
- config.config_manager（プロジェクト内モジュール）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |