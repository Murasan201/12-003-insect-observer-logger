# Phase 2: ハードウェア制御 処理説明書

**フェーズ概要**: Phase 2 - ハードウェア制御  
**作成日**: 2025-07-28  
**更新日**: 2025-07-28  

---

## 📋 フェーズ概要

### 目的
昆虫自動観察システムのハードウェアデバイス制御を統合管理し、Raspberry Pi Camera V3 NoIR・IR LED・GPIO の制御とハードウェア状態監視を提供する。

### 対象モジュール
Phase 2では以下の3つのモジュールの処理説明書を作成しています：

---

## 📁 処理説明書一覧

### 1. 統合ハードウェア制御

#### 1.1 hardware_controller.py
- **文書番号**: 12-003-PROC-101
- **ファイル**: [hardware_controller_processing_spec.md](hardware_controller_processing_spec.md)
- **概要**: カメラ・IR LED・GPIO の統合制御とハードウェア状態監視

### 2. 専用デバイス制御

#### 2.1 camera_controller.py
- **文書番号**: 12-003-PROC-102
- **ファイル**: [camera_controller_processing_spec.md](camera_controller_processing_spec.md)
- **概要**: Raspberry Pi Camera V3 NoIR専用の高度なカメラ制御・赤外線撮影対応

#### 2.2 led_controller.py
- **文書番号**: 12-003-PROC-103
- **ファイル**: [led_controller_processing_spec.md](led_controller_processing_spec.md)
- **概要**: IR LED Ring Light (FRS5CS 850nm) のPWM調光制御・温度監視・自動調光

---

## 🔗 モジュール間依存関係

```
┌─────────────────────────────────────────────────────────────┐
│               Phase 2: ハードウェア制御                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  統合制御       │  │  カメラ制御      │  │  LED制御        │  │
│  │                 │  │                │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │ hardware_   │ │──┼─│ camera_     │ │  │ │ led_        │ │  │
│  │ │ controller  │ │  │ │ controller  │ │  │ │ controller  │ │  │
│  │ │             │ │──┼─┤             │ │  │ │             │ │  │
│  │ │ ・統合制御   │ │  │ │ ・picamera2 │ │  │ │ ・PWM制御   │ │  │
│  │ │ ・状態監視   │ │  │ │ ・NoIR対応  │ │  │ │ ・温度監視   │ │  │
│  │ │ ・同期撮影   │ │  │ │ ・露出制御  │ │  │ │ ・熱保護     │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                      │                      │        │
│           └──────────────────────┼──────────────────────┘        │
│                                  │                               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │           ハードウェアインフラストラクチャ                    │  │
│  │                                                             │  │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │  │
│  │ │ Raspberry   │ │ picamera2   │ │ RPi.GPIO    │ │ System      │ │  │
│  │ │ Pi Hardware │ │ Library     │ │ Library     │ │ Resources   │ │  │
│  │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 依存関係説明
- **hardware_controller** → **camera_controller, led_controller**: 各専用制御クラスを統合管理
- **camera_controller** → **picamera2**: Raspberry Pi Camera V3 NoIR の制御
- **led_controller** → **RPi.GPIO**: PWM による IR LED 制御
- 全モジュール → **System Resources**: 温度監視・リソース管理

---

## 📊 Phase 2 実装状況

| モジュール | 処理説明書 | 実装状況 | テスト状況 |
|-----------|-----------|---------|----------|
| hardware_controller.py | ✅ 完了 | ✅ 実装済み | ✅ テスト済み |
| camera_controller.py | ✅ 完了 | ✅ 実装済み | ✅ テスト済み |
| led_controller.py | ✅ 完了 | ✅ 実装済み | ✅ テスト済み |

---

## 🔧 主要機能サマリー

### 統合ハードウェア制御（hardware_controller.py）
- カメラ・LED の統合初期化・制御
- IR LED 点灯下での同期撮影
- ハードウェア状態監視・ヘルスチェック
- デバイスエラーハンドリング・復旧処理

### カメラ制御（camera_controller.py）
- Raspberry Pi Camera V3 NoIR 専用制御
- 赤外線撮影最適化（露出・ゲイン調整）
- 夜間撮影モード・画質最適化
- メタデータ付き画像保存・連続撮影

### LED制御（led_controller.py）
- IR LED Ring Light の PWM 調光制御
- 温度監視による熱保護機能
- 自動調光・フェード・パルス制御
- 850nm 赤外線 LED 専用最適化

---

## 🛠️ ハードウェア仕様

### 対応ハードウェア
| デバイス | 型番・仕様 | 制御方式 |
|---------|-----------|---------|
| **カメラ** | Raspberry Pi Camera V3 NoIR | picamera2 ライブラリ |
| **IR LED** | FRS5CS 850nm Ring Light | PWM (GPIO 18) |
| **制御基板** | Raspberry Pi 4B+ | BCM GPIO 制御 |

### GPIO ピン配置
| 機能 | GPIO ピン | 用途 |
|------|-----------|------|
| IR LED 制御 | GPIO 18 | PWM 出力 |
| LED 電源制御 | GPIO 19 | デジタル出力（オプション） |
| 温度センサー | GPIO 4 | 1-Wire（オプション） |

---

## 📝 使用例

### 基本的な使用パターン

```python
# 1. 統合ハードウェア制御
from hardware_controller import HardwareController

config = {
    "camera": {"resolution": [1920, 1080], "framerate": 30},
    "led": {"pin": 18, "pwm_frequency": 1000}
}
hardware = HardwareController(config)
hardware.initialize_all()

# 2. IR LED 点灯下での撮影
image = hardware.capture_with_lighting(led_brightness=0.8)

# 3. カメラ個別制御
from camera_controller import CameraController, CameraSettings

settings = CameraSettings(resolution=(1920, 1080))
camera = CameraController(settings)
camera.initialize()
camera.configure_for_night_vision(exposure_time_us=15000)

# 4. LED 個別制御
from led_controller import LEDController, LEDSettings

led_settings = LEDSettings(pin=18, thermal_protection=True)
led = LEDController(led_settings)
led.initialize()
led.set_brightness(0.9)
led.pulse(count=3)

# 5. リソースクリーンアップ
hardware.cleanup_all()
```

### 夜間撮影モード設定例

```python
# 夜間撮影最適化
camera.configure_for_night_vision(
    exposure_time_us=20000,  # 20ms露出
    analogue_gain=4.0        # 高ゲイン設定
)

# IR LED の温度管理付き点灯
led.enable_thermal_protection()
led.set_brightness(0.85)  # 85%明度で安全動作
```

---

## ⚠️ 注意事項

### ハードウェア要件
- Raspberry Pi 4B+ 以上（メモリ2GB以上推奨）
- Raspberry Pi Camera V3 NoIR モジュール
- IR LED Ring Light (850nm) + 適切な電源
- 十分な放熱環境（IR LED 熱対策）

### ソフトウェア要件
- Raspberry Pi OS (64-bit)
- Python 3.9+
- picamera2 ライブラリ
- RPi.GPIO ライブラリ
- OpenCV (画像処理用)

### 安全対策
- IR LED の過熱防止（温度監視必須）
- GPIO リソースの確実な解放
- カメラデバイスの排他制御
- システム再起動時の安全な初期化

---

## 🔄 更新履歴

| 日付 | 更新者 | 更新内容 |
|------|--------|----------|
| 2025-07-28 | 開発チーム | Phase 2処理説明書一式作成 |

---

## 📚 関連文書

- [Phase 1: 基盤モジュール処理説明書](../phase1/README.md)
- [設計書作成標準規約](../../design_document_standards.md)
- [ハードウェア設計書](../../basic_design/hardware/hardware_design.md)
- [システムアーキテクチャ設計書](../../basic_design/architecture/system_architecture_design.md)