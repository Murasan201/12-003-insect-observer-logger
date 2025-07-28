"""
カメラ制御専用モジュール

Raspberry Pi Camera Module V3 NoIR専用の制御機能を提供する。
- picamera2ライブラリを使用した高度なカメラ制御
- 赤外線撮影対応
- 露出・ゲイン・フォーカス制御
- 画像品質最適化
- エラーハンドリング
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

# Raspberry Pi カメラライブラリ
try:
    from picamera2 import Picamera2
    from picamera2.controls import Controls
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    logging.warning("picamera2 not available. Install with: pip install picamera2")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available. Install with: pip install opencv-python")


@dataclass
class CameraSettings:
    """カメラ設定データクラス"""
    resolution: Tuple[int, int] = (1920, 1080)
    framerate: int = 30
    exposure_time: Optional[int] = None  # マイクロ秒
    analogue_gain: float = 1.0
    digital_gain: float = 1.0
    brightness: float = 0.0  # -1.0 to 1.0
    contrast: float = 1.0    # 0.0 to 2.0
    saturation: float = 1.0  # 0.0 to 2.0
    sharpness: float = 1.0   # 0.0 to 2.0
    auto_exposure: bool = True
    auto_white_balance: bool = True
    noise_reduction: bool = True


@dataclass
class CameraStatus:
    """カメラ状態情報"""
    is_available: bool = False
    is_initialized: bool = False
    is_capturing: bool = False
    current_resolution: Tuple[int, int] = (0, 0)
    current_framerate: int = 0
    temperature: float = 0.0
    total_captures: int = 0
    last_capture_time: str = ""
    error_count: int = 0
    last_error: str = ""


class CameraController:
    """
    Raspberry Pi Camera Module V3 NoIR 専用制御クラス
    
    Features:
    - 高解像度静止画撮影 (最大12MP)
    - 赤外線対応撮影
    - 自動/手動露出制御
    - リアルタイム調整機能
    - バッチ撮影機能
    - 画質最適化
    """
    
    def __init__(self, settings: Optional[CameraSettings] = None):
        """
        カメラコントローラー初期化
        
        Args:
            settings: カメラ設定（Noneの場合はデフォルト設定を使用）
        """
        self.logger = logging.getLogger(__name__ + '.CameraController')
        
        # 設定
        self.settings = settings or CameraSettings()
        
        # カメラオブジェクト
        self.picam2: Optional[Picamera2] = None
        self.config: Optional[Dict[str, Any]] = None
        
        # 状態管理
        self.status = CameraStatus()
        self.status.is_available = PICAMERA2_AVAILABLE
        
        # 統計情報
        self.capture_count = 0
        self.error_count = 0
        
        if not PICAMERA2_AVAILABLE:
            self.logger.error("picamera2 is not available")
    
    def initialize(self) -> bool:
        """
        カメラ初期化
        
        Returns:
            bool: 初期化成功可否
        """
        if not PICAMERA2_AVAILABLE:
            self.logger.error("Cannot initialize camera: picamera2 not available")
            return False
        
        try:
            self.logger.info("Initializing camera...")
            
            # カメラオブジェクト作成
            self.picam2 = Picamera2()
            
            # カメラ設定作成
            main_config = {
                "size": self.settings.resolution,
                "format": "RGB888"
            }
            
            # 低解像度プレビュー設定（デバッグ用）
            lores_config = {
                "size": (640, 480),
                "format": "RGB888"
            }
            
            # 設定適用
            camera_config = self.picam2.create_still_configuration(
                main=main_config,
                lores=lores_config,
                display="lores"  # プレビュー用
            )
            
            self.picam2.configure(camera_config)
            self.config = camera_config
            
            # 制御パラメータ設定
            self._apply_camera_controls()
            
            # カメラ開始
            self.picam2.start()
            time.sleep(2)  # カメラ安定化待機
            
            # 状態更新
            self.status.is_initialized = True
            self.status.current_resolution = self.settings.resolution
            self.status.current_framerate = self.settings.framerate
            
            # カメラ情報取得
            camera_properties = self.picam2.camera_properties
            self.logger.info(f"Camera initialized: {camera_properties.get('Model', 'Unknown')}")
            self.logger.info(f"Resolution: {self.settings.resolution}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            self.status.last_error = str(e)
            self.error_count += 1
            return False
    
    def _apply_camera_controls(self) -> None:
        """カメラ制御パラメータ適用"""
        if self.picam2 is None:
            return
            
        controls = {}
        
        # 露出制御
        if not self.settings.auto_exposure and self.settings.exposure_time is not None:
            controls[Controls.ExposureTime] = self.settings.exposure_time
            controls[Controls.AnalogueGain] = self.settings.analogue_gain
            
        # 画質設定
        controls[Controls.Brightness] = self.settings.brightness
        controls[Controls.Contrast] = self.settings.contrast
        controls[Controls.Saturation] = self.settings.saturation
        controls[Controls.Sharpness] = self.settings.sharpness
        
        # ノイズ軽減
        if hasattr(Controls, 'NoiseReductionMode'):
            controls[Controls.NoiseReductionMode] = (
                1 if self.settings.noise_reduction else 0
            )
        
        # 自動制御設定
        if hasattr(Controls, 'AeEnable'):
            controls[Controls.AeEnable] = self.settings.auto_exposure
        if hasattr(Controls, 'AwbEnable'):
            controls[Controls.AwbEnable] = self.settings.auto_white_balance
        
        # 設定適用
        if controls:
            self.picam2.set_controls(controls)
            self.logger.debug(f"Applied camera controls: {controls}")
    
    def capture_image(self, 
                     save_path: Optional[str] = None,
                     return_array: bool = True) -> Optional[np.ndarray]:
        """
        静止画撮影
        
        Args:
            save_path: 保存パス（指定時はJPEGファイルとしても保存）
            return_array: numpy配列として返すかどうか
            
        Returns:
            Optional[np.ndarray]: 撮影画像（BGR形式、OpenCV互換）
        """
        if not self.status.is_initialized or self.picam2 is None:
            self.logger.error("Camera not initialized")
            return None
        
        try:
            self.status.is_capturing = True
            start_time = time.time()
            
            # 画像撮影
            if return_array:
                # numpy配列として取得
                image_array = self.picam2.capture_array("main")
                
                # RGB → BGR変換（OpenCV互換）
                if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) if OPENCV_AVAILABLE else image_array[:, :, ::-1]
                else:
                    image_bgr = image_array
            else:
                image_bgr = None
            
            # ファイル保存（指定された場合）
            if save_path:
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                self.picam2.capture_file(save_path)
                self.logger.debug(f"Image saved to: {save_path}")
            
            # 統計更新
            capture_time = time.time() - start_time
            self.capture_count += 1
            self.status.total_captures = self.capture_count
            self.status.last_capture_time = datetime.now().isoformat()
            
            self.logger.debug(f"Image captured in {capture_time:.3f}s")
            
            return image_bgr
            
        except Exception as e:
            self.logger.error(f"Image capture failed: {e}")
            self.status.last_error = str(e)
            self.error_count += 1
            self.status.error_count = self.error_count
            return None
            
        finally:
            self.status.is_capturing = False
    
    def capture_burst(self, 
                     count: int,
                     interval: float = 0.1,
                     save_dir: Optional[str] = None) -> List[np.ndarray]:
        """
        連続撮影（バーストモード）
        
        Args:
            count: 撮影枚数
            interval: 撮影間隔（秒）
            save_dir: 保存ディレクトリ
            
        Returns:
            List[np.ndarray]: 撮影画像リスト
        """
        if not self.status.is_initialized:
            self.logger.error("Camera not initialized")
            return []
        
        images = []
        self.logger.info(f"Starting burst capture: {count} images")
        
        for i in range(count):
            # 保存パス生成
            save_path = None
            if save_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                save_path = f"{save_dir}/burst_{timestamp}_{i:03d}.jpg"
            
            # 撮影
            image = self.capture_image(save_path=save_path)
            if image is not None:
                images.append(image)
            else:
                self.logger.warning(f"Failed to capture image {i+1}/{count}")
            
            # 間隔待機（最後の画像以外）
            if i < count - 1:
                time.sleep(interval)
        
        self.logger.info(f"Burst capture completed: {len(images)}/{count} images")
        return images
    
    def adjust_for_low_light(self) -> None:
        """低照度環境用設定調整"""
        if not self.status.is_initialized or self.picam2 is None:
            return
        
        try:
            controls = {
                Controls.ExposureTime: 50000,  # 50ms
                Controls.AnalogueGain: 8.0,    # 高ゲイン
                Controls.DigitalGain: 2.0,     # デジタルゲイン
                Controls.Brightness: 0.1       # 明度補正
            }
            
            self.picam2.set_controls(controls)
            self.logger.info("Adjusted camera for low light conditions")
            
        except Exception as e:
            self.logger.error(f"Low light adjustment failed: {e}")
    
    def adjust_for_ir_lighting(self) -> None:
        """赤外線照明用設定調整"""
        if not self.status.is_initialized or self.picam2 is None:
            return
        
        try:
            controls = {
                Controls.ExposureTime: 25000,  # 25ms
                Controls.AnalogueGain: 2.0,    # 中程度ゲイン
                Controls.AwbEnable: False,     # 自動ホワイトバランス無効
                Controls.Brightness: 0.0,      # 標準明度
                Controls.Contrast: 1.2         # コントラスト強化
            }
            
            # 赤外線用ホワイトバランス設定
            if hasattr(Controls, 'ColourGains'):
                controls[Controls.ColourGains] = (1.0, 1.0)  # R, B gain
            
            self.picam2.set_controls(controls)
            self.logger.info("Adjusted camera for IR lighting")
            
        except Exception as e:
            self.logger.error(f"IR lighting adjustment failed: {e}")
    
    def auto_adjust_exposure(self, image: Optional[np.ndarray] = None) -> None:
        """
        画像解析による自動露出調整
        
        Args:
            image: 解析用画像（Noneの場合は新たに撮影）
        """
        if not self.status.is_initialized or self.picam2 is None:
            return
        
        try:
            # 解析用画像取得
            if image is None:
                image = self.capture_image()
                if image is None:
                    return
            
            # 明度解析
            if OPENCV_AVAILABLE:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                mean_brightness = np.mean(gray) / 255.0
            else:
                # OpenCVが使用できない場合の簡易計算
                if len(image.shape) == 3:
                    gray = np.mean(image, axis=2)
                else:
                    gray = image
                mean_brightness = np.mean(gray) / 255.0
            
            # 露出調整
            if mean_brightness < 0.3:
                # 暗すぎる場合
                exposure_time = min(100000, int(25000 / mean_brightness))
                analogue_gain = min(8.0, 2.0 / mean_brightness)
            elif mean_brightness > 0.7:
                # 明るすぎる場合
                exposure_time = max(1000, int(25000 * mean_brightness))
                analogue_gain = max(1.0, 2.0 * mean_brightness)
            else:
                # 適正範囲
                return
            
            # 設定適用
            controls = {
                Controls.ExposureTime: exposure_time,
                Controls.AnalogueGain: analogue_gain
            }
            
            self.picam2.set_controls(controls)
            self.logger.debug(f"Auto exposure adjusted: brightness={mean_brightness:.3f}, "
                            f"exposure={exposure_time}, gain={analogue_gain:.1f}")
            
        except Exception as e:
            self.logger.error(f"Auto exposure adjustment failed: {e}")
    
    def get_camera_info(self) -> Dict[str, Any]:
        """
        カメラ情報取得
        
        Returns:
            Dict[str, Any]: カメラ詳細情報
        """
        info = {
            "available": self.status.is_available,
            "initialized": self.status.is_initialized,
            "picamera2_available": PICAMERA2_AVAILABLE,
            "opencv_available": OPENCV_AVAILABLE
        }
        
        if self.status.is_initialized and self.picam2 is not None:
            try:
                camera_properties = self.picam2.camera_properties
                info.update({
                    "model": camera_properties.get('Model', 'Unknown'),
                    "pixel_array_size": camera_properties.get('PixelArraySize'),
                    "unit_cell_size": camera_properties.get('UnitCellSize'),
                    "colour_filter_arrangement": camera_properties.get('ColourFilterArrangement'),
                    "current_resolution": self.status.current_resolution,
                    "current_framerate": self.status.current_framerate,
                    "total_captures": self.status.total_captures,
                    "error_count": self.status.error_count,
                    "last_capture_time": self.status.last_capture_time
                })
            except Exception as e:
                info["error"] = str(e)
        
        return info
    
    def get_status(self) -> CameraStatus:
        """
        カメラ状態取得
        
        Returns:
            CameraStatus: 現在の状態
        """
        return self.status
    
    def update_settings(self, new_settings: CameraSettings) -> bool:
        """
        設定更新
        
        Args:
            new_settings: 新しい設定
            
        Returns:
            bool: 更新成功可否
        """
        try:
            self.settings = new_settings
            if self.status.is_initialized:
                self._apply_camera_controls()
            self.logger.info("Camera settings updated")
            return True
        except Exception as e:
            self.logger.error(f"Settings update failed: {e}")
            return False
    
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
                self.status.is_initialized = False
                self.status.is_capturing = False


# 使用例・テスト関数
def test_camera_controller():
    """カメラコントローラーのテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # カメラ設定
    settings = CameraSettings(
        resolution=(1920, 1080),
        exposure_time=25000,
        analogue_gain=2.0,
        auto_exposure=False
    )
    
    # コントローラー作成
    camera = CameraController(settings)
    
    try:
        # 初期化
        if camera.initialize():
            logger.info("Camera initialized successfully")
            
            # 情報表示
            info = camera.get_camera_info()
            logger.info(f"Camera info: {info}")
            
            # 単発撮影テスト
            logger.info("Testing single capture...")
            image = camera.capture_image()
            if image is not None:
                logger.info(f"Single capture successful: {image.shape}")
            
            # 赤外線撮影用調整
            logger.info("Adjusting for IR lighting...")
            camera.adjust_for_ir_lighting()
            
            # 調整後撮影
            image_ir = camera.capture_image()
            if image_ir is not None:
                logger.info(f"IR capture successful: {image_ir.shape}")
            
            # 自動露出調整テスト
            logger.info("Testing auto exposure...")
            camera.auto_adjust_exposure(image_ir)
            
            # バースト撮影テスト
            logger.info("Testing burst capture...")
            images = camera.capture_burst(3, interval=0.5)
            logger.info(f"Burst capture: {len(images)} images")
            
        else:
            logger.error("Camera initialization failed")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        camera.cleanup()


if __name__ == "__main__":
    test_camera_controller()