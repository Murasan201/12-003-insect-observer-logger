# hardware_controller.py 処理説明書

**文書番号**: 12-002-PROC-101  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: hardware_controller.py 処理説明書  
**対象ファイル**: `hardware_controller.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
昆虫自動観察システムのハードウェアデバイス制御を統合管理し、カメラ・IR LED・GPIO の制御とハードウェア状態監視を提供する。

### 主要機能
- カメラデバイス制御（Raspberry Pi Camera V3 NoIR）
- IR LED制御（HAT経由）
- ハードウェア状態監視
- デバイスエラーハンドリング
- リソース管理とクリーンアップ

---

## 🔧 関数・メソッド仕様

### CameraController.__init__()

**概要**: カメラコントローラーの初期化処理

**処理内容**:
1. ロガーインスタンスを取得
2. picamera2ライブラリの利用可能性確認
3. カメラオブジェクトをNoneで初期化
4. カメラ設定の初期化

**入力インターフェース**:
```python
def __init__(self, config: Dict[str, Any]):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config | Dict[str, Any] | ○ | カメラ設定辞書 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | CameraController | 初期化されたカメラコントローラー |

**使用例**:
```python
config = {"resolution": [1920, 1080], "fps": 30}
camera_controller = CameraController(config)
```

### CameraController.initialize_camera()

**概要**: カメラの初期化と設定適用

**処理内容**:
1. picamera2の利用可能性確認
2. Picamera2オブジェクトの作成
3. カメラ設定の適用（解像度・FPS・その他パラメータ）
4. カメラの開始処理
5. 初期化完了ログ出力

**入力インターフェース**:
```python
def initialize_camera(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 初期化成功可否 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| RuntimeError | カメラデバイスが利用できない場合 |
| ValueError | 設定値が不正な場合 |

**使用例**:
```python
camera_controller = CameraController(config)
if camera_controller.initialize_camera():
    print("カメラ初期化成功")
```

### CameraController.capture_image()

**概要**: 画像を撮影してnumpy配列として返す

**処理内容**:
1. カメラの初期化状態確認
2. 画像撮影実行
3. RGB形式からBGR形式に変換
4. numpy配列として返却

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
image = camera_controller.capture_image()
if image is not None:
    cv2.imwrite("captured.jpg", image)
```

### CameraController.cleanup()

**概要**: カメラリソースのクリーンアップ

**処理内容**:
1. カメラの停止処理
2. リソースの解放
3. オブジェクトの初期化
4. クリーンアップ完了ログ出力

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
camera_controller.cleanup()
```

### LEDController.__init__()

**概要**: LED制御クラスの初期化処理

**処理内容**:
1. ロガーインスタンスを取得
2. GPIO設定の初期化
3. PWM設定の初期化
4. LED制御ピンの設定

**入力インターフェース**:
```python
def __init__(self, led_pin: int = 18, pwm_frequency: int = 1000):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| led_pin | int | × | LED制御ピン番号（デフォルト: 18） |
| pwm_frequency | int | × | PWM周波数（デフォルト: 1000Hz） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | LEDController | 初期化されたLED制御オブジェクト |

### LEDController.initialize_gpio()

**概要**: GPIO の初期化と設定

**処理内容**:
1. RPi.GPIOライブラリの利用可能性確認
2. GPIO.setmodeでBCMモード設定
3. LED制御ピンを出力に設定
4. PWMオブジェクトの作成・開始

**入力インターフェース**:
```python
def initialize_gpio(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 初期化成功可否 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| RuntimeError | GPIOが既に使用中の場合 |

**使用例**:
```python
led_controller = LEDController(18, 1000)
if led_controller.initialize_gpio():
    print("GPIO初期化成功")
```

### LEDController.set_brightness()

**概要**: LED の明度を設定

**処理内容**:
1. 明度値の範囲チェック（0.0-1.0）
2. PWMのデューティサイクル計算（0-100%）
3. PWM出力の更新
4. 現在の明度値を記録

**入力インターフェース**:
```python
def set_brightness(self, brightness: float) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| brightness | float | ○ | 明度（0.0-1.0） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 設定成功可否 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ValueError | 明度値が範囲外の場合 |

**使用例**:
```python
led_controller.set_brightness(0.8)  # 80%の明度
```

### LEDController.cleanup()

**概要**: LED制御リソースのクリーンアップ

**処理内容**:
1. PWMの停止
2. GPIO.cleanup()の実行
3. オブジェクトの初期化
4. クリーンアップ完了ログ出力

**入力インターフェース**:
```python
def cleanup(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | クリーンアップ完了後に処理終了 |

### HardwareController.__init__()

**概要**: 統合ハードウェア制御クラスの初期化

**処理内容**:
1. ロガーインスタンスを取得
2. 設定辞書の保存
3. カメラ・LED制御オブジェクトをNoneで初期化
4. ハードウェア状態オブジェクトの初期化

**入力インターフェース**:
```python
def __init__(self, config: Dict[str, Any]):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config | Dict[str, Any] | ○ | ハードウェア設定辞書 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | HardwareController | 初期化された統合制御オブジェクト |

### HardwareController.initialize_all()

**概要**: 全ハードウェアデバイスの初期化

**処理内容**:
1. カメラコントローラーの作成・初期化
2. LED制御の作成・初期化
3. 初期化結果の集計
4. ハードウェア状態の更新
5. 初期化完了ログ出力

**入力インターフェース**:
```python
def initialize_all(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 全デバイス初期化成功可否 |

**使用例**:
```python
hardware_controller = HardwareController(config)
if hardware_controller.initialize_all():
    print("全ハードウェア初期化成功")
```

### HardwareController.capture_with_lighting()

**概要**: IR LED点灯下での画像撮影

**処理内容**:
1. LED明度設定（設定値に基づく）
2. 安定化待機時間
3. 画像撮影実行
4. LED消灯
5. 撮影画像の返却

**入力インターフェース**:
```python
def capture_with_lighting(self, led_brightness: float = 0.8, 
                         stabilization_time: float = 0.5) -> Optional[np.ndarray]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| led_brightness | float | × | LED明度（デフォルト: 0.8） |
| stabilization_time | float | × | 安定化待機時間（秒、デフォルト: 0.5） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| image | Optional[np.ndarray] | 撮影画像（BGR形式、None: 撮影失敗） |

**使用例**:
```python
image = hardware_controller.capture_with_lighting(0.9, 0.3)
```

### HardwareController.get_hardware_status()

**概要**: 現在のハードウェア状態を取得

**処理内容**:
1. 各デバイスの状態確認
2. システム温度の取得（可能な場合）
3. 状態オブジェクトの更新
4. 現在時刻の記録

**入力インターフェース**:
```python
def get_hardware_status(self) -> HardwareStatus:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| status | HardwareStatus | 現在のハードウェア状態 |

**使用例**:
```python
status = hardware_controller.get_hardware_status()
print(f"カメラ状態: {status.camera_available}")
```

### HardwareController.cleanup_all()

**概要**: 全ハードウェアリソースのクリーンアップ

**処理内容**:
1. カメラコントローラーのクリーンアップ
2. LED制御のクリーンアップ
3. オブジェクトの初期化
4. ハードウェア状態のリセット
5. 全クリーンアップ完了ログ出力

**入力インターフェース**:
```python
def cleanup_all(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | クリーンアップ完了後に処理終了 |

**使用例**:
```python
hardware_controller.cleanup_all()
```

---

## 📊 データ構造

### HardwareStatus

**概要**: ハードウェア状態情報を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| camera_available | bool | カメラ利用可能フラグ |
| camera_initialized | bool | カメラ初期化済みフラグ |
| gpio_available | bool | GPIO利用可能フラグ |
| gpio_initialized | bool | GPIO初期化済みフラグ |
| led_available | bool | LED利用可能フラグ |
| led_brightness | float | 現在のLED明度 |
| temperature | float | システム温度（℃） |
| last_updated | str | 最終更新時刻 |

### CameraController

**概要**: カメラ専用制御クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| config | Dict[str, Any] | カメラ設定辞書 |
| camera | Optional[Picamera2] | Picamera2オブジェクト |

### LEDController

**概要**: LED制御専用クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| led_pin | int | LED制御ピン番号 |
| pwm_frequency | int | PWM周波数 |
| pwm | Optional[GPIO.PWM] | PWMオブジェクト |
| current_brightness | float | 現在の明度 |

### HardwareController

**概要**: 統合ハードウェア制御クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| config | Dict[str, Any] | ハードウェア設定辞書 |
| camera_controller | Optional[CameraController] | カメラ制御オブジェクト |
| led_controller | Optional[LEDController] | LED制御オブジェクト |
| hardware_status | HardwareStatus | ハードウェア状態 |

---

## 🔄 処理フロー

### ハードウェア初期化フロー
```
1. HardwareController初期化
   ↓
2. initialize_all()実行
   ↓
3. カメラコントローラー初期化
   ↓
4. LED制御初期化
   ↓
5. 状態確認・更新
```

### 画像撮影フロー
```
1. capture_with_lighting()実行
   ↓
2. LED点灯（指定明度）
   ↓
3. 安定化待機
   ↓
4. 画像撮影
   ↓
5. LED消灯
   ↓
6. 画像返却
```

### エラー処理フロー
```
デバイスエラー発生
   ↓
例外キャッチ・ログ出力
   ↓
リソースクリーンアップ
   ↓
False/None返却（継続可能な場合）
```

---

## 📝 実装メモ

### 注意事項
- picamera2・RPi.GPIOライブラリの動的インポートによる環境対応
- GPIO.cleanup()の確実な実行でリソースリーク防止
- PWM周波数の適切な設定で安定したLED制御
- 撮影前のLED安定化時間を考慮

### 依存関係
- logging（標準ライブラリ）
- time（標準ライブラリ）
- typing（標準ライブラリ）
- numpy（外部ライブラリ）
- dataclasses（標準ライブラリ）
- pathlib（標準ライブラリ）
- picamera2（Raspberry Pi専用）
- RPi.GPIO（Raspberry Pi専用）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |