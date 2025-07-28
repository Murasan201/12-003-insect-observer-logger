"""
ハードウェア制御モジュール

昆虫自動観察システムのハードウェアデバイス制御を統合管理する。
- カメラデバイス制御
- IR LED制御（HAT経由）
- ハードウェア状態監視
- デバイスエラーハンドリング
- リソース管理
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from pathlib import Path

# Raspberry Pi関連ライブラリ
try:
    from picamera2 import Picamera2
    from picamera2.controls import Controls
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    logging.warning("picamera2 not available. Camera functionality will be disabled.")

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available. GPIO functionality will be disabled.")


@dataclass
class HardwareStatus:
    """ハードウェア状態情報"""
    camera_available: bool = False
    camera_initialized: bool = False
    gpio_available: bool = False
    gpio_initialized: bool = False
    led_available: bool = False
    led_brightness: float = 0.0
    temperature: float = 0.0
    last_updated: str = ""


class CameraController:
    """カメラ専用制御クラス"""
    
    def __init__(self):
        self.picam2: Optional[Picamera2] = None
        self.config: Optional[Dict[str, Any]] = None
        self.logger = logging.getLogger(__name__ + '.CameraController')
        self.is_initialized = False
        
    def setup_camera(self, config: Dict[str, Any]) -> bool:
        """
        カメラセットアップ
        
        Args:
            config: カメラ設定
            
        Returns:
            bool: セットアップ成功可否
        """
        if not PICAMERA2_AVAILABLE:
            self.logger.error("picamera2 is not available")
            return False
            
        try:
            self.picam2 = Picamera2()
            
            # カメラ設定の作成
            camera_config = self.picam2.create_still_configuration(
                main={"size": tuple(config.get('resolution', (1920, 1080)))},
                lores={"size": (640, 480)},
                display="lores"
            )
            
            self.picam2.configure(camera_config)
            
            # カメラ制御設定
            controls = {}
            if 'exposure_time' in config:
                controls[Controls.ExposureTime] = config['exposure_time']
            if 'analogue_gain' in config:
                controls[Controls.AnalogueGain] = config['analogue_gain']
            if 'brightness' in config:
                controls[Controls.Brightness] = config['brightness']
                
            if controls:
                self.picam2.set_controls(controls)
            
            self.picam2.start()
            time.sleep(2)  # カメラ安定化待機
            
            self.config = config
            self.is_initialized = True
            self.logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Camera setup failed: {e}")
            return False
    
    def capture_still(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        静止画撮影
        
        Args:
            save_path: 保存パス（指定時はファイル保存も実行）
            
        Returns:
            Optional[np.ndarray]: 撮影画像（BGR形式）
        """
        if not self.is_initialized or self.picam2 is None:
            self.logger.error("Camera not initialized")
            return None
            
        try:
            # 画像撮影
            image_array = self.picam2.capture_array("main")
            
            # RGB → BGR変換（OpenCV互換）
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_bgr = image_array[:, :, ::-1]  # RGB to BGR
            else:
                image_bgr = image_array
            
            # ファイル保存（指定された場合）
            if save_path:
                self.picam2.capture_file(save_path)
                self.logger.debug(f"Image saved to: {save_path}")
            
            self.logger.debug("Image captured successfully")
            return image_bgr
            
        except Exception as e:
            self.logger.error(f"Image capture failed: {e}")
            return None
    
    def adjust_exposure(self, scene_brightness: float) -> None:
        """
        露出調整
        
        Args:
            scene_brightness: シーンの明度（0.0-1.0）
        """
        if not self.is_initialized or self.picam2 is None:
            self.logger.warning("Camera not initialized for exposure adjustment")
            return
            
        try:
            # シーンの明度に基づいて露出時間を調整
            if scene_brightness < 0.3:
                # 暗いシーン - 露出時間を長く
                exposure_time = 50000  # 50ms
                analogue_gain = 2.0
            elif scene_brightness > 0.7:
                # 明るいシーン - 露出時間を短く
                exposure_time = 10000  # 10ms
                analogue_gain = 1.0
            else:
                # 中間 - 標準設定
                exposure_time = 25000  # 25ms
                analogue_gain = 1.5
            
            self.picam2.set_controls({
                Controls.ExposureTime: exposure_time,
                Controls.AnalogueGain: analogue_gain
            })
            
            self.logger.debug(f"Exposure adjusted for brightness: {scene_brightness}")
            
        except Exception as e:
            self.logger.error(f"Exposure adjustment failed: {e}")
    
    def get_camera_info(self) -> Dict[str, Any]:
        """
        カメラ情報取得
        
        Returns:
            Dict[str, Any]: カメラ情報
        """
        if not self.is_initialized or self.picam2 is None:
            return {"status": "not_initialized"}
            
        try:
            camera_properties = self.picam2.camera_properties
            return {
                "status": "initialized",
                "model": camera_properties.get('Model', 'Unknown'),
                "resolution": self.config.get('resolution', 'Unknown'),
                "pixel_array_size": camera_properties.get('PixelArraySize', 'Unknown')
            }
        except Exception as e:
            self.logger.error(f"Failed to get camera info: {e}")
            return {"status": "error", "error": str(e)}
    
    def cleanup(self) -> None:
        """リソース解放"""
        if self.picam2 is not None:
            try:
                self.picam2.stop()
                self.picam2.close()
                self.logger.info("Camera cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Camera cleanup failed: {e}")
            finally:
                self.picam2 = None
                self.is_initialized = False


class LEDController:
    """LED制御クラス（HAT使用想定）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.LEDController')
        self.is_initialized = False
        self.current_brightness = 0.0
        self.led_pin = None
        
    def setup_led(self, config: Dict[str, Any]) -> bool:
        """
        LED制御セットアップ（HAT使用想定）
        
        Args:
            config: LED設定
            
        Returns:
            bool: セットアップ成功可否
        """
        try:
            # HAT使用時は専用ライブラリを使用
            # 現在はGPIOによる基本制御として実装
            if GPIO_AVAILABLE:
                self.led_pin = config.get('led_pin', 18)
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.led_pin, GPIO.OUT)
                GPIO.output(self.led_pin, GPIO.LOW)
                self.logger.info(f"LED controller initialized (GPIO pin: {self.led_pin})")
            else:
                self.logger.warning("GPIO not available, LED control disabled")
                
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"LED setup failed: {e}")
            return False
    
    def set_brightness(self, brightness: float) -> None:
        """
        LED明度設定
        
        Args:
            brightness: 明度（0.0-1.0）
        """
        if not self.is_initialized:
            self.logger.warning("LED controller not initialized")
            return
            
        try:
            # 明度を0-1の範囲にクランプ
            brightness = max(0.0, min(1.0, brightness))
            
            if GPIO_AVAILABLE and self.led_pin is not None:
                # シンプルなオン/オフ制御（HAT使用時は専用API使用）
                if brightness > 0:
                    GPIO.output(self.led_pin, GPIO.HIGH)
                else:
                    GPIO.output(self.led_pin, GPIO.LOW)
            
            self.current_brightness = brightness
            self.logger.debug(f"LED brightness set to: {brightness}")
            
        except Exception as e:
            self.logger.error(f"LED brightness control failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        LED状態取得
        
        Returns:
            Dict[str, Any]: LED状態情報
        """
        return {
            "initialized": self.is_initialized,
            "brightness": self.current_brightness,
            "pin": self.led_pin
        }
    
    def cleanup(self) -> None:
        """リソース解放"""
        if self.is_initialized and GPIO_AVAILABLE and self.led_pin is not None:
            try:
                GPIO.output(self.led_pin, GPIO.LOW)
                GPIO.cleanup(self.led_pin)
                self.logger.info("LED controller cleaned up successfully")
            except Exception as e:
                self.logger.error(f"LED cleanup failed: {e}")
        
        self.is_initialized = False
        self.current_brightness = 0.0


class HardwareController:
    """ハードウェア統合制御クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        制御器初期化
        
        Args:
            config: ハードウェア設定
        """
        self.config = config
        self.logger = logging.getLogger(__name__ + '.HardwareController')
        
        # サブコントローラー初期化
        self.camera_controller = CameraController()
        self.led_controller = LEDController()
        
        # 状態管理
        self.status = HardwareStatus()
        self.is_initialized = False
        
    def initialize_hardware(self) -> bool:
        """
        ハードウェア初期化
        
        Returns:
            bool: 初期化成功可否
        """
        self.logger.info("Starting hardware initialization...")
        
        success = True
        
        # カメラ初期化
        camera_config = self.config.get('camera', {})
        if self.camera_controller.setup_camera(camera_config):
            self.status.camera_available = True
            self.status.camera_initialized = True
            self.logger.info("Camera initialization successful")
        else:
            self.logger.error("Camera initialization failed")
            success = False
        
        # LED初期化
        led_config = self.config.get('led', {})
        if self.led_controller.setup_led(led_config):
            self.status.led_available = True
            self.logger.info("LED initialization successful")
        else:
            self.logger.error("LED initialization failed")
            success = False
        
        # GPIO状態更新
        self.status.gpio_available = GPIO_AVAILABLE
        self.status.gpio_initialized = GPIO_AVAILABLE
        
        self.is_initialized = success
        self.update_status()
        
        if success:
            self.logger.info("Hardware initialization completed successfully")
        else:
            self.logger.warning("Hardware initialization completed with errors")
            
        return success
    
    def capture_image(self, 
                     resolution: Optional[Tuple[int, int]] = None,
                     save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        画像撮影
        
        Args:
            resolution: 撮影解像度（未使用、設定で固定）
            save_path: 保存パス
            
        Returns:
            Optional[np.ndarray]: 撮影画像
        """
        if not self.is_initialized:
            self.logger.error("Hardware not initialized")
            return None
            
        return self.camera_controller.capture_still(save_path)
    
    def control_ir_led(self, brightness: float) -> None:
        """
        IR LED制御
        
        Args:
            brightness: 明度（0.0-1.0）
        """
        if not self.is_initialized:
            self.logger.error("Hardware not initialized")
            return
            
        self.led_controller.set_brightness(brightness)
        self.status.led_brightness = brightness
        self.update_status()
    
    def adjust_camera_exposure(self, scene_brightness: float) -> None:
        """
        カメラ露出調整
        
        Args:
            scene_brightness: シーンの明度
        """
        if not self.is_initialized:
            self.logger.error("Hardware not initialized")
            return
            
        self.camera_controller.adjust_exposure(scene_brightness)
    
    def get_system_status(self) -> HardwareStatus:
        """
        システム状態取得
        
        Returns:
            HardwareStatus: システム状態情報
        """
        self.update_status()
        return self.status
    
    def update_status(self) -> None:
        """状態情報更新"""
        try:
            # 温度情報取得（Raspberry Pi）
            temp_path = Path('/sys/class/thermal/thermal_zone0/temp')
            if temp_path.exists():
                with open(temp_path, 'r') as f:
                    temp_millicelsius = int(f.read().strip())
                    self.status.temperature = temp_millicelsius / 1000.0
            
            # 最終更新時刻
            from datetime import datetime
            self.status.last_updated = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Status update failed: {e}")
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """
        詳細状態情報取得
        
        Returns:
            Dict[str, Any]: 詳細状態情報
        """
        self.update_status()
        
        return {
            "hardware_status": {
                "camera_available": self.status.camera_available,
                "camera_initialized": self.status.camera_initialized,
                "gpio_available": self.status.gpio_available,
                "gpio_initialized": self.status.gpio_initialized,
                "led_available": self.status.led_available,
                "led_brightness": self.status.led_brightness,
                "temperature": self.status.temperature,
                "last_updated": self.status.last_updated
            },
            "camera_info": self.camera_controller.get_camera_info(),
            "led_status": self.led_controller.get_status(),
            "system_info": {
                "picamera2_available": PICAMERA2_AVAILABLE,
                "gpio_available": GPIO_AVAILABLE,
                "initialized": self.is_initialized
            }
        }
    
    def cleanup_resources(self) -> None:
        """リソース解放"""
        self.logger.info("Starting hardware cleanup...")
        
        # LED消灯
        try:
            self.led_controller.set_brightness(0.0)
        except Exception as e:
            self.logger.error(f"LED shutdown failed: {e}")
        
        # カメラ停止
        self.camera_controller.cleanup()
        
        # LED制御停止
        self.led_controller.cleanup()
        
        # GPIO全体クリーンアップ
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
                self.logger.info("GPIO cleanup completed")
            except Exception as e:
                self.logger.error(f"GPIO cleanup failed: {e}")
        
        self.is_initialized = False
        self.logger.info("Hardware cleanup completed")


# 使用例・テスト関数
def test_hardware_controller():
    """ハードウェアコントローラーのテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 設定
    config = {
        'camera': {
            'resolution': (1920, 1080),
            'exposure_time': 25000,
            'analogue_gain': 1.5
        },
        'led': {
            'led_pin': 18
        }
    }
    
    # ハードウェアコントローラー初期化
    hw_controller = HardwareController(config)
    
    try:
        # 初期化
        if hw_controller.initialize_hardware():
            logger.info("Hardware initialized successfully")
            
            # 状態確認
            status = hw_controller.get_detailed_status()
            logger.info(f"Hardware status: {status}")
            
            # LED点灯テスト
            logger.info("Testing LED control...")
            hw_controller.control_ir_led(0.5)
            time.sleep(2)
            hw_controller.control_ir_led(0.0)
            
            # 画像撮影テスト
            logger.info("Testing image capture...")
            image = hw_controller.capture_image()
            if image is not None:
                logger.info(f"Image captured: {image.shape}")
            else:
                logger.error("Image capture failed")
                
        else:
            logger.error("Hardware initialization failed")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        hw_controller.cleanup_resources()


if __name__ == "__main__":
    test_hardware_controller()