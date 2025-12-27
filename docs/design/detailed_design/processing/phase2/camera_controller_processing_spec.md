# camera_controller.py 処理説明書

**文書番号**: 12-003-PROC-102  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: camera_controller.py 処理説明書  
**対象ファイル**: `camera_controller.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
Raspberry Pi Camera Module V3 NoIR専用の高度なカメラ制御機能を提供し、赤外線撮影対応・露出制御・画像品質最適化を行う。

### 主要機能
- picamera2ライブラリを使用した高度なカメラ制御
- 赤外線撮影対応（NoIRモジュール）
- 露出・ゲイン・フォーカス制御
- 画像品質最適化
- エラーハンドリングとリソース管理

---

## 🔧 関数・メソッド仕様

### CameraSettings.__post_init__()

**概要**: CameraSettingsデータクラスの初期化後処理

**処理内容**:
1. 解像度値の妥当性チェック
2. フレームレートの範囲チェック
3. ゲイン・明度等のパラメータ範囲チェック
4. 設定値の正規化

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

### CameraController.__init__()

**概要**: カメラコントローラーの初期化処理

**処理内容**:
1. ロガーインスタンスを取得
2. カメラ設定の保存
3. picamera2オブジェクトをNoneで初期化
4. カメラ状態の初期化
5. ライブラリ利用可能性確認

**入力インターフェース**:
```python
def __init__(self, settings: CameraSettings):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| settings | CameraSettings | ○ | カメラ設定オブジェクト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | CameraController | 初期化されたカメラコントローラー |

**使用例**:
```python
settings = CameraSettings(resolution=(1920, 1080), framerate=30)
controller = CameraController(settings)
```

### CameraController.initialize()

**概要**: カメラの初期化と基本設定適用

**処理内容**:
1. picamera2の利用可能性確認
2. Picamera2オブジェクトの作成
3. カメラ設定の構築と適用
4. カメラの開始処理
5. 初期化完了の確認

**入力インターフェース**:
```python
def initialize(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 初期化成功可否 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| RuntimeError | カメラデバイスアクセスエラーの場合 |
| ValueError | 設定値が不正な場合 |

**使用例**:
```python
controller = CameraController(settings)
if controller.initialize():
    print("カメラ初期化成功")
```

### CameraController.configure_for_night_vision()

**概要**: 夜間撮影用の最適設定を適用

**処理内容**:
1. 露出時間の延長設定
2. アナログゲインの最適化
3. デジタルゲインの調整
4. ノイズリダクション設定
5. 設定の適用と確認

**入力インターフェース**:
```python
def configure_for_night_vision(self, exposure_time_us: int = 10000, 
                              analogue_gain: float = 4.0) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| exposure_time_us | int | × | 露出時間（マイクロ秒、デフォルト: 10000） |
| analogue_gain | float | × | アナログゲイン（デフォルト: 4.0） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 設定適用成功可否 |

**使用例**:
```python
controller.configure_for_night_vision(15000, 3.5)
```

### CameraController.capture_image()

**概要**: 単一画像の撮影

**処理内容**:
1. カメラの初期化状態確認
2. 画像撮影実行
3. 色空間変換（RGB → BGR）
4. 画像データの検証
5. numpy配列として返却

**入力インターフェース**:
```python
def capture_image(self) -> Optional[np.ndarray]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| image | Optional[np.ndarray] | 撮影画像（BGR形式、None: 撮影失敗） |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| RuntimeError | カメラが初期化されていない場合 |

**使用例**:
```python
image = controller.capture_image()
if image is not None:
    cv2.imwrite("captured.jpg", image)
```

### CameraController.capture_multiple_images()

**概要**: 複数画像の連続撮影

**処理内容**:
1. カメラの初期化状態確認
2. 指定回数分のループ撮影
3. 各画像の撮影間隔制御
4. 撮影画像リストの作成
5. エラー処理と統計情報記録

**入力インターフェース**:
```python
def capture_multiple_images(self, count: int, interval_seconds: float = 0.5) -> List[np.ndarray]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| count | int | ○ | 撮影枚数 |
| interval_seconds | float | × | 撮影間隔（秒、デフォルト: 0.5） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| images | List[np.ndarray] | 撮影画像リスト |

**使用例**:
```python
images = controller.capture_multiple_images(5, 1.0)
print(f"撮影枚数: {len(images)}")
```

### CameraController.save_image_with_metadata()

**概要**: メタデータ付きで画像を保存

**処理内容**:
1. 画像データの検証
2. メタデータ（設定・タイムスタンプ等）の準備
3. ファイル名の生成（タイムスタンプベース）
4. 画像ファイルの保存
5. メタデータファイルの保存

**入力インターフェース**:
```python
def save_image_with_metadata(self, image: np.ndarray, 
                            base_path: str = "./images", 
                            include_settings: bool = True) -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| image | np.ndarray | ○ | 保存する画像データ |
| base_path | str | × | 保存先ベースパス（デフォルト: "./images"） |
| include_settings | bool | × | 設定情報を含むか（デフォルト: True） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| saved_path | str | 保存されたファイルパス |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| IOError | ファイル保存エラーの場合 |

**使用例**:
```python
image = controller.capture_image()
saved_path = controller.save_image_with_metadata(image, "./output")
```

### CameraController.adjust_exposure()

**概要**: 露出設定の動的調整

**処理内容**:
1. 現在の画像の明度分析
2. 適切な露出時間の計算
3. ゲイン値の調整
4. 設定の適用と効果確認
5. 調整結果の記録

**入力インターフェース**:
```python
def adjust_exposure(self, target_brightness: float = 0.5) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| target_brightness | float | × | 目標明度（0.0-1.0、デフォルト: 0.5） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 調整成功可否 |

**使用例**:
```python
controller.adjust_exposure(0.6)  # やや明るめに調整
```

### CameraController.get_camera_info()

**概要**: カメラ情報と現在設定の取得

**処理内容**:
1. カメラのハードウェア情報取得
2. 現在の設定値取得
3. センサー情報の収集
4. 情報辞書の作成
5. ログ出力用フォーマット

**入力インターフェース**:
```python
def get_camera_info(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| info | Dict[str, Any] | カメラ情報辞書 |

**使用例**:
```python
info = controller.get_camera_info()
print(f"解像度: {info['resolution']}")
```

### CameraController.test_camera()

**概要**: カメラ機能のテスト実行

**処理内容**:
1. 基本撮影テスト
2. 設定変更テスト
3. 連続撮影テスト
4. エラー処理テスト
5. テスト結果の集計と報告

**入力インターフェース**:
```python
def test_camera(self) -> Dict[str, bool]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| test_results | Dict[str, bool] | テスト結果辞書 |

**使用例**:
```python
results = controller.test_camera()
if all(results.values()):
    print("全テスト成功")
```

### CameraController.cleanup()

**概要**: カメラリソースのクリーンアップ

**処理内容**:
1. 撮影の停止
2. カメラの停止処理
3. リソースの解放
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
controller.cleanup()
```

---

## 📊 データ構造

### CameraSettings

**概要**: カメラ設定を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| resolution | Tuple[int, int] | 解像度（幅, 高さ） |
| framerate | int | フレームレート |
| exposure_time | Optional[int] | 露出時間（マイクロ秒） |
| analogue_gain | float | アナログゲイン |
| digital_gain | float | デジタルゲイン |
| brightness | float | 明度（-1.0 to 1.0） |
| contrast | float | コントラスト（0.0 to 2.0） |
| saturation | float | 彩度（0.0 to 2.0） |
| sharpness | float | シャープネス（0.0 to 2.0） |

### CameraController

**概要**: カメラ制御専用クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| settings | CameraSettings | カメラ設定オブジェクト |
| camera | Optional[Picamera2] | Picamera2オブジェクト |
| is_initialized | bool | 初期化状態フラグ |
| capture_count | int | 撮影回数カウンター |

---

## 🔄 処理フロー

### カメラ初期化フロー
```
1. CameraController作成
   ↓
2. initialize()実行
   ↓
3. Picamera2オブジェクト作成
   ↓
4. 設定適用
   ↓
5. カメラ開始
```

### 夜間撮影設定フロー
```
1. configure_for_night_vision()実行
   ↓
2. 露出時間延長
   ↓
3. ゲイン調整
   ↓
4. ノイズリダクション設定
   ↓
5. 設定適用確認
```

### 画像撮影フロー
```
1. capture_image()実行
   ↓
2. カメラ状態確認
   ↓
3. 画像撮影
   ↓
4. 色空間変換（RGB→BGR）
   ↓
5. numpy配列返却
```

### エラー処理フロー
```
カメラエラー発生
   ↓
例外キャッチ・ログ出力
   ↓
リソースクリーンアップ
   ↓
False/None返却
```

---

## 📝 実装メモ

### 注意事項
- NoIRモジュール専用設定の最適化
- 赤外線撮影時の露出・ゲイン調整
- picamera2の非同期処理を考慮
- 色空間変換でのメモリ効率
- リソースリークの防止

### 依存関係
- logging（標準ライブラリ）
- time（標準ライブラリ）
- typing（標準ライブラリ）
- numpy（外部ライブラリ）
- dataclasses（標準ライブラリ）
- pathlib（標準ライブラリ）
- datetime（標準ライブラリ）
- picamera2（Raspberry Pi専用）
- cv2（外部ライブラリ）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |