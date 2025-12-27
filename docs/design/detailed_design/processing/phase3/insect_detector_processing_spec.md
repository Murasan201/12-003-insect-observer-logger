# insect_detector.py 処理説明書

**文書番号**: 12-003-PROC-201  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: insect_detector.py 処理説明書  
**対象ファイル**: `insect_detector.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
YOLOv8を使用した昆虫検出処理の実行と制御を行い、カメラ制御・IR LED制御との連携による統合的な検出システムを提供する。

### 主要機能
- YOLOv8モデル推論実行
- 検出結果の処理・検証
- カメラ制御・IR LED制御との連携
- 検出品質の評価
- バッチ処理対応

---

## 🔧 関数・メソッド仕様

### DetectionSettings.__post_init__()

**概要**: DetectionSettings データクラスの初期化後処理

**処理内容**:
1. 信頼度閾値の範囲チェック（0.0-1.0）
2. NMS閾値の範囲チェック（0.0-1.0）
3. 最大検出数の範囲チェック（正の整数）
4. モデルファイルパスの存在確認

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
| ValueError | 設定値が不正な範囲の場合 |
| FileNotFoundError | モデルファイルが存在しない場合 |

### InsectDetector.__init__()

**概要**: 昆虫検出クラスの初期化処理

**処理内容**:
1. ロガーインスタンスを取得
2. 検出設定の保存
3. YOLOモデル・ハードウェア制御オブジェクトをNoneで初期化
4. データ検証器の初期化
5. 検出統計カウンターの初期化

**入力インターフェース**:
```python
def __init__(self, settings: DetectionSettings, hardware_controller: Optional[HardwareController] = None):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| settings | DetectionSettings | ○ | 検出設定オブジェクト |
| hardware_controller | Optional[HardwareController] | × | ハードウェア制御オブジェクト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | InsectDetector | 初期化された検出オブジェクト |

**使用例**:
```python
settings = DetectionSettings(confidence_threshold=0.6)
detector = InsectDetector(settings, hardware_controller)
```

### InsectDetector.initialize_model()

**概要**: YOLOv8モデルの初期化と読み込み

**処理内容**:
1. ultralytics ライブラリの利用可能性確認
2. YOLOモデルファイルの存在確認
3. YOLOオブジェクトの作成・モデル読み込み
4. GPU利用可能性の確認とデバイス設定
5. モデル情報の取得・ログ出力

**入力インターフェース**:
```python
def initialize_model(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | モデル初期化成功可否 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| FileNotFoundError | モデルファイルが存在しない場合 |
| RuntimeError | モデル読み込みエラーの場合 |

**使用例**:
```python
detector = InsectDetector(settings)
if detector.initialize_model():
    print("モデル初期化成功")
```

### InsectDetector.detect_from_camera()

**概要**: カメラから画像を撮影して昆虫検出実行

**処理内容**:
1. ハードウェア制御オブジェクトの存在確認
2. IR LED点灯下での画像撮影
3. 撮影画像の検証
4. YOLO推論実行
5. 検出結果の処理・返却

**入力インターフェース**:
```python
def detect_from_camera(self, led_brightness: float = 0.8, save_image: bool = True) -> Tuple[List[DetectionResult], Optional[np.ndarray]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| led_brightness | float | × | LED明度（デフォルト: 0.8） |
| save_image | bool | × | 画像保存フラグ（デフォルト: True） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| detections | List[DetectionResult] | 検出結果リスト |
| image | Optional[np.ndarray] | 撮影画像（None: 撮影失敗） |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| RuntimeError | カメラが初期化されていない場合 |

**使用例**:
```python
detections, image = detector.detect_from_camera(0.9, True)
print(f"検出数: {len(detections)}")
```

### InsectDetector.detect_from_image()

**概要**: 指定画像に対して昆虫検出実行

**処理内容**:
1. 入力画像の検証
2. 画像前処理（リサイズ・正規化）
3. YOLO推論実行
4. 検出結果の後処理
5. DetectionResultオブジェクトの生成

**入力インターフェース**:
```python
def detect_from_image(self, image: np.ndarray) -> List[DetectionResult]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| image | np.ndarray | ○ | 入力画像（BGR形式） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| detections | List[DetectionResult] | 検出結果リスト |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ValueError | 画像データが不正な場合 |
| RuntimeError | モデルが初期化されていない場合 |

**使用例**:
```python
image = cv2.imread("test_image.jpg")
detections = detector.detect_from_image(image)
```

### InsectDetector.detect_batch()

**概要**: 複数画像の一括検出処理

**処理内容**:
1. 画像リストの検証
2. バッチサイズに応じた分割処理
3. 各画像に対する検出実行
4. 結果の集約・統計情報収集
5. エラー画像の記録

**入力インターフェース**:
```python
def detect_batch(self, images: List[np.ndarray], batch_size: int = 4) -> List[List[DetectionResult]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| images | List[np.ndarray] | ○ | 入力画像リスト |
| batch_size | int | × | バッチサイズ（デフォルト: 4） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| batch_results | List[List[DetectionResult]] | バッチ検出結果リスト |

**使用例**:
```python
images = [cv2.imread(f"image_{i}.jpg") for i in range(10)]
results = detector.detect_batch(images, 2)
```

### InsectDetector.preprocess_image()

**概要**: YOLO推論用の画像前処理

**処理内容**:
1. 画像サイズの確認・リサイズ
2. 色空間変換（BGR → RGB）
3. 画素値正規化（0-255 → 0-1）
4. テンソル形式への変換
5. バッチ次元の追加

**入力インターフェース**:
```python
def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| image | np.ndarray | ○ | 入力画像（BGR形式） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| tensor | torch.Tensor | 前処理済みテンソル |

**使用例**:
```python
image = cv2.imread("input.jpg")
tensor = detector.preprocess_image(image)
```

### InsectDetector.postprocess_results()

**概要**: YOLO推論結果の後処理

**処理内容**:
1. 推論結果テンソルの解析
2. 信頼度フィルタリング
3. NMS（Non-Maximum Suppression）適用
4. 座標変換（正規化 → ピクセル）
5. DetectionResultオブジェクト生成

**入力インターフェース**:
```python
def postprocess_results(self, predictions: torch.Tensor, image_shape: Tuple[int, int]) -> List[DetectionResult]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| predictions | torch.Tensor | ○ | YOLO推論結果テンソル |
| image_shape | Tuple[int, int] | ○ | 元画像サイズ（H, W） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| detections | List[DetectionResult] | 検出結果リスト |

**使用例**:
```python
predictions = model(tensor)
detections = detector.postprocess_results(predictions, (1080, 1920))
```

### InsectDetector.save_detection_results()

**概要**: 検出結果の保存処理

**処理内容**:
1. 保存ディレクトリの作成確認
2. 画像へのバウンディングボックス描画
3. 検出画像の保存
4. 検出結果CSVの作成・保存
5. メタデータの保存

**入力インターフェース**:
```python
def save_detection_results(self, detections: List[DetectionResult], 
                          image: np.ndarray, 
                          base_dir: str = "./detection_results") -> Dict[str, str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 検出結果リスト |
| image | np.ndarray | ○ | 元画像 |
| base_dir | str | × | 保存ベースディレクトリ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| saved_files | Dict[str, str] | 保存ファイルパス辞書 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| IOError | ファイル保存エラーの場合 |

**使用例**:
```python
saved_files = detector.save_detection_results(detections, image, "./output")
```

### InsectDetector.draw_detections()

**概要**: 画像に検出結果のバウンディングボックス描画

**処理内容**:
1. 元画像のコピー作成
2. 各検出結果のバウンディングボックス描画
3. 信頼度・クラス名の描画
4. 色分け処理（信頼度に応じて）
5. 描画済み画像の返却

**入力インターフェース**:
```python
def draw_detections(self, image: np.ndarray, detections: List[DetectionResult]) -> np.ndarray:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| image | np.ndarray | ○ | 元画像 |
| detections | List[DetectionResult] | ○ | 検出結果リスト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| annotated_image | np.ndarray | 描画済み画像 |

**使用例**:
```python
annotated = detector.draw_detections(image, detections)
cv2.imwrite("result.jpg", annotated)
```

### InsectDetector.evaluate_detection_quality()

**概要**: 検出品質の評価

**処理内容**:
1. 検出結果の統計分析
2. 信頼度分布の計算
3. 検出密度の算出
4. 品質スコアの計算
5. 評価レポートの生成

**入力インターフェース**:
```python
def evaluate_detection_quality(self, detections: List[DetectionResult]) -> Dict[str, float]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 検出結果リスト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| quality_metrics | Dict[str, float] | 品質評価メトリクス |

**使用例**:
```python
metrics = detector.evaluate_detection_quality(detections)
print(f"平均信頼度: {metrics['avg_confidence']}")
```

### InsectDetector.get_detection_statistics()

**概要**: 検出統計情報の取得

**処理内容**:
1. 累積検出統計の集計
2. 検出成功率の計算
3. 平均処理時間の算出
4. エラー統計の集計
5. 統計辞書の生成

**入力インターフェース**:
```python
def get_detection_statistics(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| statistics | Dict[str, Any] | 検出統計辞書 |

**使用例**:
```python
stats = detector.get_detection_statistics()
print(f"総検出回数: {stats['total_detections']}")
```

### InsectDetector.cleanup()

**概要**: 検出器リソースのクリーンアップ

**処理内容**:
1. YOLOモデルのメモリ解放
2. GPU キャッシュのクリア
3. 統計情報の最終保存
4. オブジェクトの初期化
5. クリーンアップ完了ログ出力

**入力インターフェース**:
```python
def cleanup(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | クリーンアップ完了後に処理終了 |

**使用例**:
```python
detector.cleanup()
```

---

## 📊 データ構造

### DetectionSettings

**概要**: 検出設定を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| model_path | str | YOLOモデルファイルパス |
| confidence_threshold | float | 信頼度閾値（0.0-1.0） |
| nms_threshold | float | NMS閾値（0.0-1.0） |
| max_detections | int | 最大検出数 |
| input_size | Tuple[int, int] | 入力画像サイズ |
| device | str | 推論デバイス（"cpu", "cuda"） |
| save_annotated_images | bool | 描画済み画像保存フラグ |
| save_detection_logs | bool | 検出ログ保存フラグ |

### InsectDetector

**概要**: 昆虫検出処理クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| settings | DetectionSettings | 検出設定オブジェクト |
| model | Optional[YOLO] | YOLOモデルオブジェクト |
| hardware_controller | Optional[HardwareController] | ハードウェア制御オブジェクト |
| validator | DataValidator | データ検証器 |
| detection_count | int | 検出実行回数カウンター |
| success_count | int | 検出成功回数カウンター |
| total_processing_time | float | 累積処理時間 |

---

## 🔄 処理フロー

### カメラ検出フロー
```
1. detect_from_camera()実行
   ↓
2. IR LED点灯・画像撮影
   ↓
3. 画像前処理
   ↓
4. YOLO推論実行
   ↓
5. 結果後処理・返却
```

### 画像検出フロー
```
1. detect_from_image()実行
   ↓
2. 画像検証・前処理
   ↓
3. YOLO推論実行
   ↓
4. 結果後処理
   ↓
5. DetectionResult生成
```

### バッチ検出フロー
```
1. detect_batch()実行
   ↓
2. 画像リスト分割
   ↓
3. バッチ単位で検出処理
   ↓
4. 結果集約・統計更新
   ↓
5. バッチ結果返却
```

### エラー処理フロー
```
検出エラー発生
   ↓
例外キャッチ・ログ出力
   ↓
エラー統計更新
   ↓
空の結果返却（継続可能な場合）
```

---

## 📝 実装メモ

### 注意事項
- YOLOv8モデルのメモリ効率的な管理
- GPU/CPU自動切り替えによる環境対応
- バッチ処理時のメモリ使用量制御
- 検出結果の信頼性検証
- ハードウェア制御との同期処理

### 依存関係
- logging（標準ライブラリ）
- time（標準ライブラリ）
- typing（標準ライブラリ）
- numpy（外部ライブラリ）
- dataclasses（標準ライブラリ）
- pathlib（標準ライブラリ）
- datetime（標準ライブラリ）
- threading（標準ライブラリ）
- ultralytics（外部ライブラリ）
- torch（外部ライブラリ）
- cv2（外部ライブラリ）
- models.detection_models（プロジェクト内モジュール）
- models.system_models（プロジェクト内モジュール）
- hardware_controller（プロジェクト内モジュール）
- utils.data_validator（プロジェクト内モジュール）
- utils.file_naming（プロジェクト内モジュール）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |