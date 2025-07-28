"""
LED制御専用モジュール

IR LED Ring Light (FRS5CS 850nm) の制御を管理する。
HAT使用時の専用制御とGPIOによる基本制御の両方に対応。
- PWM調光制御
- 温度監視
- 自動調光機能
- エラー検出・保護機能
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import threading

# GPIO制御ライブラリ
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available. LED functionality will be limited.")

# HAT専用ライブラリの例（実際のHATに応じて変更）
try:
    # 例: from your_hat_library import LEDController as HATController
    HAT_AVAILABLE = False  # 実際のHATライブラリが利用可能な場合はTrue
except ImportError:
    HAT_AVAILABLE = False


@dataclass
class LEDSettings:
    """LED設定データクラス"""
    pin: int = 18                    # GPIO pin number
    pwm_frequency: int = 1000        # PWM frequency (Hz)
    max_brightness: float = 1.0      # 最大明度制限 (0.0-1.0)
    min_brightness: float = 0.0      # 最小明度制限
    default_brightness: float = 0.8  # デフォルト明度
    fade_duration: float = 0.5       # フェード時間（秒）
    thermal_protection: bool = True  # 熱保護機能
    max_temperature: float = 70.0    # 最大動作温度（℃）
    auto_brightness: bool = False    # 自動明度調整


@dataclass
class LEDStatus:
    """LED状態情報"""
    is_available: bool = False
    is_initialized: bool = False
    is_on: bool = False
    current_brightness: float = 0.0
    target_brightness: float = 0.0
    pwm_frequency: int = 0
    temperature: float = 0.0
    total_on_time: float = 0.0      # 累積点灯時間（秒）
    error_count: int = 0
    last_error: str = ""
    thermal_protection_active: bool = False


class LEDController:
    """
    IR LED Ring Light 制御クラス
    
    Features:
    - PWM調光制御（0-100%）
    - スムーズなフェードイン/アウト
    - 温度監視・保護機能
    - 自動明度調整
    - 使用時間トラッキング
    - HAT/GPIO両対応
    """
    
    def __init__(self, settings: Optional[LEDSettings] = None):
        """
        LED制御器初期化
        
        Args:
            settings: LED設定（Noneの場合はデフォルト設定）
        """
        self.logger = logging.getLogger(__name__ + '.LEDController')
        
        # 設定
        self.settings = settings or LEDSettings()
        
        # 状態管理
        self.status = LEDStatus()
        self.status.is_available = GPIO_AVAILABLE or HAT_AVAILABLE
        
        # PWM制御オブジェクト
        self.pwm = None
        self.hat_controller = None
        
        # 統計・監視
        self.start_time = None
        self.fade_thread = None
        self.monitoring_active = False
        
        # 初期化チェック
        if not self.status.is_available:
            self.logger.error("No LED control method available (GPIO or HAT)")
    
    def initialize(self) -> bool:
        """
        LED制御初期化
        
        Returns:
            bool: 初期化成功可否
        """
        if not self.status.is_available:
            self.logger.error("Cannot initialize LED: no control method available")
            return False
        
        try:
            self.logger.info(f"Initializing LED controller...")
            
            # HAT制御を優先
            if HAT_AVAILABLE:
                success = self._initialize_hat()
                if success:
                    self.logger.info("LED initialized with HAT controller")
                    self.status.is_initialized = True
                    return True
            
            # GPIO制御にフォールバック
            if GPIO_AVAILABLE:
                success = self._initialize_gpio()
                if success:
                    self.logger.info("LED initialized with GPIO controller")
                    self.status.is_initialized = True
                    return True
            
            self.logger.error("LED initialization failed")
            return False
            
        except Exception as e:
            self.logger.error(f"LED initialization failed: {e}")
            self.status.last_error = str(e)
            self.status.error_count += 1
            return False
    
    def _initialize_hat(self) -> bool:
        """HAT制御初期化"""
        try:
            # HAT専用ライブラリの初期化
            # self.hat_controller = HATController()
            # self.hat_controller.initialize()
            
            # 現在はプレースホルダー
            self.logger.warning("HAT controller not implemented yet")
            return False
            
        except Exception as e:
            self.logger.error(f"HAT initialization failed: {e}")
            return False
    
    def _initialize_gpio(self) -> bool:
        """GPIO制御初期化"""
        try:
            # GPIO設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.settings.pin, GPIO.OUT)
            
            # PWM初期化
            self.pwm = GPIO.PWM(self.settings.pin, self.settings.pwm_frequency)
            self.pwm.start(0)  # 0%でスタート
            
            # 状態更新
            self.status.pwm_frequency = self.settings.pwm_frequency
            
            self.logger.info(f"GPIO PWM initialized: pin={self.settings.pin}, "
                           f"freq={self.settings.pwm_frequency}Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"GPIO initialization failed: {e}")
            return False
    
    def set_brightness(self, brightness: float, fade: bool = False) -> bool:
        """
        LED明度設定
        
        Args:
            brightness: 目標明度 (0.0-1.0)
            fade: フェード効果を使用するか
            
        Returns:
            bool: 設定成功可否
        """
        if not self.status.is_initialized:
            self.logger.error("LED not initialized")
            return False
        
        try:
            # 明度を制限範囲内にクランプ
            brightness = max(self.settings.min_brightness, 
                           min(self.settings.max_brightness, brightness))
            
            # 熱保護チェック
            if self.settings.thermal_protection and self._check_thermal_protection(brightness):
                self.logger.warning("Thermal protection active - brightness limited")
                brightness = 0.0
            
            # フェード効果
            if fade and abs(brightness - self.status.current_brightness) > 0.1:
                self._fade_to_brightness(brightness)
            else:
                self._set_brightness_direct(brightness)
            
            # 状態更新
            self.status.target_brightness = brightness
            self.status.is_on = brightness > 0.0
            
            # 点灯時間トラッキング開始/停止
            if self.status.is_on and self.start_time is None:
                self.start_time = time.time()
            elif not self.status.is_on and self.start_time is not None:
                self.status.total_on_time += time.time() - self.start_time
                self.start_time = None
            
            self.logger.debug(f"LED brightness set to {brightness:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set LED brightness: {e}")
            self.status.last_error = str(e)
            self.status.error_count += 1
            return False
    
    def _set_brightness_direct(self, brightness: float) -> None:
        """直接明度設定"""
        duty_cycle = brightness * 100.0  # 0-100%
        
        if self.hat_controller is not None:
            # HAT制御
            # self.hat_controller.set_brightness(brightness)
            pass
        elif self.pwm is not None:
            # GPIO PWM制御
            self.pwm.ChangeDutyCycle(duty_cycle)
        
        self.status.current_brightness = brightness
    
    def _fade_to_brightness(self, target_brightness: float) -> None:
        """フェード効果で明度変更"""
        if self.fade_thread is not None and self.fade_thread.is_alive():
            # 既存のフェードを停止
            self.fade_thread.join(timeout=0.1)
        
        # フェードスレッド開始
        self.fade_thread = threading.Thread(
            target=self._fade_worker,
            args=(target_brightness,),
            daemon=True
        )
        self.fade_thread.start()
    
    def _fade_worker(self, target_brightness: float) -> None:
        """フェードワーカースレッド"""
        try:
            start_brightness = self.status.current_brightness
            steps = int(self.settings.fade_duration * 50)  # 50 FPS
            step_size = (target_brightness - start_brightness) / steps
            
            for i in range(steps + 1):
                current = start_brightness + (step_size * i)
                self._set_brightness_direct(current)
                time.sleep(self.settings.fade_duration / steps)
            
            # 最終値を確実に設定
            self._set_brightness_direct(target_brightness)
            
        except Exception as e:
            self.logger.error(f"Fade operation failed: {e}")
    
    def turn_on(self, brightness: Optional[float] = None, fade: bool = True) -> bool:
        """
        LED点灯
        
        Args:
            brightness: 明度（Noneの場合はデフォルト明度）
            fade: フェード効果使用
            
        Returns:
            bool: 点灯成功可否
        """
        target_brightness = brightness or self.settings.default_brightness
        return self.set_brightness(target_brightness, fade=fade)
    
    def turn_off(self, fade: bool = True) -> bool:
        """
        LED消灯
        
        Args:
            fade: フェード効果使用
            
        Returns:
            bool: 消灯成功可否
        """
        return self.set_brightness(0.0, fade=fade)
    
    def pulse(self, duration: float = 2.0, min_brightness: float = 0.1, 
              max_brightness: float = 1.0) -> None:
        """
        パルス点灯（呼吸効果）
        
        Args:
            duration: パルス周期（秒）
            min_brightness: 最小明度
            max_brightness: 最大明度
        """
        if not self.status.is_initialized:
            return
        
        try:
            steps = int(duration * 20)  # 20 FPS
            half_steps = steps // 2
            
            # フェードイン
            for i in range(half_steps):
                brightness = min_brightness + (max_brightness - min_brightness) * (i / half_steps)
                self._set_brightness_direct(brightness)
                time.sleep(duration / steps)
            
            # フェードアウト
            for i in range(half_steps):
                brightness = max_brightness - (max_brightness - min_brightness) * (i / half_steps)
                self._set_brightness_direct(brightness)
                time.sleep(duration / steps)
            
        except Exception as e:
            self.logger.error(f"Pulse operation failed: {e}")
    
    def blink(self, count: int = 3, on_time: float = 0.5, off_time: float = 0.5) -> None:
        """
        点滅
        
        Args:
            count: 点滅回数
            on_time: 点灯時間（秒）
            off_time: 消灯時間（秒）
        """
        if not self.status.is_initialized:
            return
        
        original_brightness = self.status.current_brightness
        
        try:
            for _ in range(count):
                self.turn_on(fade=False)
                time.sleep(on_time)
                self.turn_off(fade=False)
                time.sleep(off_time)
            
            # 元の明度に復帰
            self.set_brightness(original_brightness, fade=False)
            
        except Exception as e:
            self.logger.error(f"Blink operation failed: {e}")
    
    def _check_thermal_protection(self, target_brightness: float) -> bool:
        """
        熱保護チェック
        
        Args:
            target_brightness: 目標明度
            
        Returns:
            bool: 保護動作が必要かどうか
        """
        if not self.settings.thermal_protection:
            return False
        
        try:
            # 温度取得（簡易実装）
            # 実際のシステムでは温度センサーからの値を使用
            temp = self._get_led_temperature()
            self.status.temperature = temp
            
            if temp > self.settings.max_temperature:
                self.status.thermal_protection_active = True
                return True
            
            self.status.thermal_protection_active = False
            return False
            
        except Exception as e:
            self.logger.error(f"Thermal protection check failed: {e}")
            return False
    
    def _get_led_temperature(self) -> float:
        """
        LED温度取得（プレースホルダー）
        
        Returns:
            float: 推定温度（℃）
        """
        # 実際の実装では温度センサーまたは推定アルゴリズムを使用
        # 現在は使用率に基づく簡易推定
        base_temp = 25.0  # 室温
        brightness_factor = self.status.current_brightness * 30.0  # 明度による発熱
        time_factor = min(10.0, self.status.total_on_time / 60.0)  # 時間による蓄熱
        
        return base_temp + brightness_factor + time_factor
    
    def get_status(self) -> LEDStatus:
        """
        LED状態取得
        
        Returns:
            LEDStatus: 現在の状態
        """
        # 点灯時間更新
        if self.status.is_on and self.start_time is not None:
            current_session = time.time() - self.start_time
        else:
            current_session = 0.0
        
        # 温度更新
        if self.settings.thermal_protection:
            self.status.temperature = self._get_led_temperature()
        
        return self.status
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """
        詳細状態情報取得
        
        Returns:
            Dict[str, Any]: 詳細状態情報
        """
        status = self.get_status()
        
        return {
            "led_status": {
                "available": status.is_available,
                "initialized": status.is_initialized,
                "is_on": status.is_on,
                "current_brightness": status.current_brightness,
                "target_brightness": status.target_brightness,
                "temperature": status.temperature,
                "total_on_time": status.total_on_time,
                "error_count": status.error_count,
                "thermal_protection_active": status.thermal_protection_active
            },
            "settings": {
                "pin": self.settings.pin,
                "pwm_frequency": self.settings.pwm_frequency,
                "max_brightness": self.settings.max_brightness,
                "thermal_protection": self.settings.thermal_protection,
                "max_temperature": self.settings.max_temperature
            },
            "system_info": {
                "gpio_available": GPIO_AVAILABLE,
                "hat_available": HAT_AVAILABLE,
                "control_method": "HAT" if self.hat_controller else "GPIO"
            }
        }
    
    def test_led(self) -> bool:
        """
        LED動作テスト
        
        Returns:
            bool: テスト成功可否
        """
        if not self.status.is_initialized:
            self.logger.error("LED not initialized for testing")
            return False
        
        try:
            self.logger.info("Starting LED test sequence...")
            
            # テストシーケンス
            original_brightness = self.status.current_brightness
            
            # 1. 点灯テスト
            self.turn_on(0.5, fade=False)
            time.sleep(1)
            
            # 2. 明度変更テスト
            for brightness in [0.2, 0.8, 1.0, 0.5]:
                self.set_brightness(brightness, fade=False)
                time.sleep(0.5)
            
            # 3. フェードテスト
            self.set_brightness(0.0, fade=True)
            time.sleep(1)
            self.set_brightness(1.0, fade=True)
            time.sleep(1)
            
            # 4. 点滅テスト
            self.blink(count=2, on_time=0.3, off_time=0.3)
            
            # 5. 元の状態に復帰
            self.set_brightness(original_brightness, fade=False)
            
            self.logger.info("LED test completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"LED test failed: {e}")
            return False
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            # LED消灯
            if self.status.is_initialized:
                self.turn_off(fade=False)
                time.sleep(0.1)
            
            # フェードスレッド停止
            if self.fade_thread is not None and self.fade_thread.is_alive():
                self.fade_thread.join(timeout=1.0)
            
            # PWM停止
            if self.pwm is not None:
                self.pwm.stop()
                self.pwm = None
            
            # GPIO クリーンアップ
            if GPIO_AVAILABLE:
                try:
                    GPIO.cleanup(self.settings.pin)
                except:
                    pass  # GPIO cleanup errors are not critical
            
            # HAT クリーンアップ
            if self.hat_controller is not None:
                # self.hat_controller.cleanup()
                self.hat_controller = None
            
            # 統計更新
            if self.start_time is not None:
                self.status.total_on_time += time.time() - self.start_time
                self.start_time = None
            
            self.status.is_initialized = False
            self.status.is_on = False
            self.status.current_brightness = 0.0
            
            self.logger.info("LED controller cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"LED cleanup failed: {e}")


# 使用例・テスト関数
def test_led_controller():
    """LED制御器のテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # LED設定
    settings = LEDSettings(
        pin=18,
        pwm_frequency=1000,
        default_brightness=0.8,
        thermal_protection=True
    )
    
    # コントローラー作成
    led = LEDController(settings)
    
    try:
        # 初期化
        if led.initialize():
            logger.info("LED initialized successfully")
            
            # 状態表示
            status = led.get_detailed_status()
            logger.info(f"LED status: {status}")
            
            # 動作テスト
            logger.info("Running LED test sequence...")
            led.test_led()
            
            # 手動制御テスト
            logger.info("Testing manual control...")
            led.turn_on(0.3, fade=True)
            time.sleep(2)
            
            led.set_brightness(0.8, fade=True)
            time.sleep(2)
            
            led.pulse(duration=3.0)
            
            led.turn_off(fade=True)
            time.sleep(1)
            
        else:
            logger.error("LED initialization failed")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        led.cleanup()


if __name__ == "__main__":
    test_led_controller()