# led_controller.py 処理説明書

**文書番号**: 12-003-PROC-103  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: led_controller.py 処理説明書  
**対象ファイル**: `led_controller.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
IR LED Ring Light (FRS5CS 850nm) の制御を管理し、PWM調光制御・温度監視・自動調光機能・エラー検出保護機能を提供する。

### 主要機能
- PWM調光制御（精密な明度制御）
- 温度監視による熱保護
- 自動調光機能
- HAT使用時の専用制御とGPIOによる基本制御
- エラー検出・保護機能

---

## 🔧 関数・メソッド仕様

### LEDSettings.__post_init__()

**概要**: LEDSettings データクラスの初期化後処理

**処理内容**:
1. GPIO ピン番号の妥当性チェック
2. PWM 周波数の範囲チェック
3. 明度設定値の範囲チェック（0.0-1.0）
4. 温度設定値の妥当性チェック

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

### LEDController.__init__()

**概要**: LED制御クラスの初期化処理

**処理内容**:
1. ロガーインスタンスを取得
2. LED設定の保存
3. GPIO・PWMオブジェクトをNoneで初期化
4. LED状態オブジェクトの初期化
5. 温度監視スレッドの準備

**入力インターフェース**:
```python
def __init__(self, settings: LEDSettings):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| settings | LEDSettings | ○ | LED設定オブジェクト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | LEDController | 初期化されたLED制御オブジェクト |

**使用例**:
```python
settings = LEDSettings(pin=18, pwm_frequency=1000)
controller = LEDController(settings)
```

### LEDController.initialize()

**概要**: GPIO・PWM の初期化

**処理内容**:
1. RPi.GPIO ライブラリの利用可能性確認
2. GPIO.setmode で BCM モード設定
3. LED 制御ピンを出力に設定
4. PWM オブジェクトの作成・開始
5. 温度監視スレッドの開始

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
| RuntimeError | GPIO が既に使用中の場合 |

**使用例**:
```python
controller = LEDController(settings)
if controller.initialize():
    print("LED制御初期化成功")
```

### LEDController.set_brightness()

**概要**: LED の明度を設定

**処理内容**:
1. 明度値の範囲チェック（0.0-1.0）
2. 熱保護状態の確認
3. PWM のデューティサイクル計算（0-100%）
4. フェード処理（設定に応じて）
5. 現在の明度値を記録

**入力インターフェース**:
```python
def set_brightness(self, brightness: float, fade: bool = True) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| brightness | float | ○ | 明度（0.0-1.0） |
| fade | bool | × | フェード有無（デフォルト: True） |

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
controller.set_brightness(0.8, fade=True)  # 80%の明度でフェード
```

### LEDController.fade_to_brightness()

**概要**: 指定明度まで段階的にフェード

**処理内容**:
1. 現在の明度と目標明度の差分計算
2. フェードステップ数の計算
3. 段階的な明度変更ループ
4. 各ステップでの待機時間制御
5. 最終明度の設定と確認

**入力インターフェース**:
```python
def fade_to_brightness(self, target_brightness: float, duration: float = None) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| target_brightness | float | ○ | 目標明度（0.0-1.0） |
| duration | float | × | フェード時間（秒、None: 設定値使用） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | フェード完了成功可否 |

**使用例**:
```python
controller.fade_to_brightness(0.5, 2.0)  # 2秒かけて50%にフェード
```

### LEDController.pulse()

**概要**: LED のパルス点滅

**処理内容**:
1. パルス回数・間隔・明度の設定確認
2. 指定回数分のパルスループ
3. 明度の上下制御
4. パルス間隔の制御
5. 元の明度への復帰

**入力インターフェース**:
```python
def pulse(self, count: int = 3, interval: float = 0.5, 
         max_brightness: float = 1.0) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| count | int | × | パルス回数（デフォルト: 3） |
| interval | float | × | パルス間隔（秒、デフォルト: 0.5） |
| max_brightness | float | × | パルス最大明度（デフォルト: 1.0） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | パルス完了後に処理終了 |

**使用例**:
```python
controller.pulse(5, 0.3, 0.9)  # 5回、0.3秒間隔、最大90%でパルス
```

### LEDController.auto_adjust_brightness()

**概要**: 環境に応じた自動明度調整

**処理内容**:
1. 周囲環境の明度測定（センサー利用時）
2. 時間帯に基づく明度計算
3. 温度状況を考慮した調整
4. 最適明度の算出
5. 明度設定の実行

**入力インターフェース**:
```python
def auto_adjust_brightness(self, ambient_light: Optional[float] = None) -> float:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| ambient_light | Optional[float] | × | 周囲光量（0.0-1.0、None: 自動測定） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| brightness | float | 設定された明度値 |

**使用例**:
```python
brightness = controller.auto_adjust_brightness(0.2)  # 暗い環境での自動調整
```

### LEDController.get_temperature()

**概要**: LED・システムの温度取得

**処理内容**:
1. システム温度ファイルの読み込み
2. 温度データの解析
3. 摂氏温度への変換
4. 温度履歴の更新
5. 異常温度の検出

**入力インターフェース**:
```python
def get_temperature(self) -> Optional[float]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| temperature | Optional[float] | 現在の温度（℃、None: 取得失敗） |

**使用例**:
```python
temp = controller.get_temperature()
if temp and temp > 65.0:
    print("高温警告")
```

### LEDController.monitor_temperature()

**概要**: 温度監視スレッド処理

**処理内容**:
1. 定期的な温度取得
2. 温度履歴の記録
3. 過熱検出時の自動明度削減
4. 冷却待機処理
5. 正常温度復帰時の明度回復

**入力インターフェース**:
```python
def monitor_temperature(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 監視スレッド終了時に処理終了 |

**使用例**:
```python
# 自動的にバックグラウンドで実行される
# 手動呼び出しは通常不要
```

### LEDController.enable_thermal_protection()

**概要**: 熱保護機能の有効化

**処理内容**:
1. 熱保護設定の確認
2. 温度監視スレッドの状態確認
3. 監視スレッドの開始（未開始の場合）
4. 保護機能有効化フラグの設定
5. 保護機能有効化ログ出力

**入力インターフェース**:
```python
def enable_thermal_protection(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 有効化完了後に処理終了 |

**使用例**:
```python
controller.enable_thermal_protection()
```

### LEDController.disable_thermal_protection()

**概要**: 熱保護機能の無効化

**処理内容**:
1. 保護機能無効化フラグの設定
2. 温度監視スレッドの停止指示
3. 現在の明度制限の解除
4. 保護機能無効化ログ出力

**入力インターフェース**:
```python
def disable_thermal_protection(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 無効化完了後に処理終了 |

**使用例**:
```python
controller.disable_thermal_protection()
```

### LEDController.get_status()

**概要**: LED の現在状態を取得

**処理内容**:
1. 現在の明度値取得
2. 温度情報の取得
3. GPIO・PWM の状態確認
4. エラー状態の確認
5. 状態オブジェクトの更新

**入力インターフェース**:
```python
def get_status(self) -> LEDStatus:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| status | LEDStatus | 現在のLED状態オブジェクト |

**使用例**:
```python
status = controller.get_status()
print(f"現在明度: {status.current_brightness}")
```

### LEDController.test_led()

**概要**: LED 機能のテスト実行

**処理内容**:
1. 基本点灯テスト
2. 明度調整テスト
3. フェード機能テスト
4. パルス機能テスト
5. テスト結果の集計と報告

**入力インターフェース**:
```python
def test_led(self) -> Dict[str, bool]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| test_results | Dict[str, bool] | テスト結果辞書 |

**使用例**:
```python
results = controller.test_led()
if all(results.values()):
    print("全LEDテスト成功")
```

### LEDController.cleanup()

**概要**: LED制御リソースのクリーンアップ

**処理内容**:
1. 温度監視スレッドの停止
2. LED の消灯（明度0に設定）
3. PWM の停止
4. GPIO.cleanup() の実行
5. オブジェクトの初期化

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

### LEDSettings

**概要**: LED設定を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| pin | int | GPIO ピン番号 |
| pwm_frequency | int | PWM 周波数（Hz） |
| max_brightness | float | 最大明度制限（0.0-1.0） |
| min_brightness | float | 最小明度制限 |
| default_brightness | float | デフォルト明度 |
| fade_duration | float | フェード時間（秒） |
| thermal_protection | bool | 熱保護機能有無 |
| max_temperature | float | 最大動作温度（℃） |
| auto_brightness | bool | 自動明度調整有無 |

### LEDStatus

**概要**: LED状態情報を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| is_initialized | bool | 初期化状態フラグ |
| current_brightness | float | 現在の明度 |
| target_brightness | float | 目標明度 |
| temperature | float | 現在温度（℃） |
| thermal_protection_active | bool | 熱保護有効状態 |
| error_count | int | エラー発生回数 |
| last_updated | str | 最終更新時刻 |

### LEDController

**概要**: LED制御専用クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| settings | LEDSettings | LED設定オブジェクト |
| pwm | Optional[GPIO.PWM] | PWMオブジェクト |
| status | LEDStatus | LED状態オブジェクト |
| monitor_thread | Optional[threading.Thread] | 温度監視スレッド |
| stop_monitoring | bool | 監視停止フラグ |

---

## 🔄 処理フロー

### LED初期化フロー
```
1. LEDController作成
   ↓
2. initialize()実行
   ↓
3. GPIO設定
   ↓
4. PWM開始
   ↓
5. 温度監視スレッド開始
```

### 明度制御フロー
```
1. set_brightness()実行
   ↓
2. 熱保護状態確認
   ↓
3. フェード処理（必要に応じて）
   ↓
4. PWM出力更新
   ↓
5. 状態記録
```

### 温度監視フロー
```
1. 定期温度取得
   ↓
2. 過熱判定
   ↓
3. 自動明度削減（過熱時）
   ↓
4. 冷却待機
   ↓
5. 明度復帰（正常温度時）
```

### エラー処理フロー
```
LED制御エラー発生
   ↓
例外キャッチ・ログ出力
   ↓
安全状態への移行（消灯）
   ↓
エラーカウンタ更新
```

---

## 📝 実装メモ

### 注意事項
- IR LED の発熱特性を考慮した温度監視
- PWM 周波数の最適化で安定した調光
- GPIO リソースの確実な解放
- 温度監視スレッドの適切な停止処理
- HAT 使用時の専用API対応

### 依存関係
- logging（標準ライブラリ）
- time（標準ライブラリ）
- typing（標準ライブラリ）
- dataclasses（標準ライブラリ）
- datetime（標準ライブラリ）
- threading（標準ライブラリ）
- RPi.GPIO（Raspberry Pi専用）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |