#!/usr/bin/env python3
"""
昆虫検出器モジュール (detector.py)

このモジュールは昆虫自動観察システムの検出機能を提供します。
YOLOv8モデルを使用した昆虫検出、カメラ制御、ハードウェア制御を行います。

Author: 開発チーム
Date: 2025-07-25
Version: 1.0
"""

import logging
import time
import numpy as np
import cv2
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json

try:
    from ultralytics import YOLO
except ImportError:
    logging.error("ultralytics not found. Please install: pip install ultralytics")
    YOLO = None

try:
    from picamera2 import Picamera2
except ImportError:
    logging.warning("picamera2 not found. Camera functionality will be limited.")
    Picamera2 = None

try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warning("RPi.GPIO not found. GPIO functionality will be limited.")
    GPIO = None


class DetectionStatus(Enum):
    """検出状態を表す列挙型"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    DETECTING = "detecting"
    ERROR = "error"
    CLEANUP = "cleanup"


@dataclass
class DetectionResult:
    """検出結果を格納するデータクラス"""
    x_center: float
    y_center: float
    width: float
    height: float
    confidence: float
    class_id: int
    timestamp: str
    
    def __post_init__(self):
        """初期化後の検証処理 - データの整合性を自動チェック"""
        if not self.validate():
            raise ValueError("Invalid detection result parameters")
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換 - JSONシリアライゼーション用"""
        return {
            'x_center': self.x_center,
            'y_center': self.y_center,
            'width': self.width,
            'height': self.height,
            'confidence': self.confidence,
            'class_id': self.class_id,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetectionResult':
        """辞書から検出結果を作成 - CSVファイル読み込み等で使用"""
        return cls(**data)
    
    def validate(self) -> bool:
        """検出結果の妥当性を検証 - 不正データの除外"""
        try:
            # 座標値の範囲チェック（正規化座標として0-1の範囲）
            # x_center, y_centerは画像中心座標（0.0-1.0）
            if not (0 <= self.x_center <= 1 and 0 <= self.y_center <= 1):
                return False
            # width, heightは相対的なバウンディングボックスサイズ（0-1）
            if not (0 < self.width <= 1 and 0 < self.height <= 1):
                return False
            # 信頼度の範囲チェック（0.0-1.0）
            if not (0 <= self.confidence <= 1):
                return False
            # クラスIDの妥当性チェック（非負整数）
            if not isinstance(self.class_id, int) or self.class_id < 0:
                return False
            return True
        except (TypeError, ValueError):
            return False


class DataValidator:
    """データ検証クラス"""
    
    @staticmethod
    def validate_image(image: np.ndarray) -> bool:
        """画像データの妥当性を検証 - YOLO推論前のチェック"""
        if image is None:
            return False
        if not isinstance(image, np.ndarray):
            return False
        # 3次元配列であることを確認（高さ×幅×チャンネル）
        if len(image.shape) != 3:
            return False
        # RGBの3チャンネルであることを確認
        if image.shape[2] != 3:
            return False
        # 空の画像でないことを確認
        if image.size == 0:
            return False
        return True
    
    @staticmethod
    def validate_detection_result(result: DetectionResult) -> bool:
        """検出結果の妥当性を検証 - ログ出力前のデータチェック"""
        return result.validate()
    
    @staticmethod
    def sanitize_coordinates(x: float, y: float, img_shape: Tuple[int, int, int]) -> Tuple[float, float]:
        """座標値を画像サイズに基づいて正規化 - ピクセル座標→相対座標変換"""
        height, width = img_shape[:2]
        # 0-1の範囲に正規化し、境界値でクリップ
        x_normalized = max(0, min(1, x / width if width > 0 else 0))
        y_normalized = max(0, min(1, y / height if height > 0 else 0))
        return x_normalized, y_normalized


class PerformanceMonitor:
    """性能監視クラス"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> None:
        """タイマー開始 - 処理時間測定の開始点を記録"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """タイマー終了して経過時間を返す - 統計データに追加"""
        if operation not in self.start_times:
            return 0.0
        
        # 経過時間を計算（秒単位）
        elapsed = time.time() - self.start_times[operation]
        
        # 統計用のリストに追加
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(elapsed)
        
        # 開始時間を削除してメモリ解放
        del self.start_times[operation]
        return elapsed
    
    def get_performance_stats(self, operation: str) -> Dict[str, float]:
        """性能統計を取得 - 平均・最大・最小処理時間等を計算"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}
        
        times = self.metrics[operation]
        return {
            'count': len(times),          # 実行回数
            'total': sum(times),          # 総実行時間
            'average': sum(times) / len(times),  # 平均実行時間
            'min': min(times),            # 最短実行時間
            'max': max(times)             # 最長実行時間
        }
    
    def reset_metrics(self) -> None:
        """メトリクスをリセット - 統計データを初期化"""
        self.metrics.clear()
        self.start_times.clear()


class DetectorInterface:
    """検出器インターフェース（抽象基底クラス）"""
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """検出器を初期化"""
        raise NotImplementedError
    
    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """画像から昆虫を検出"""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """検出器の状態を取得"""
        raise NotImplementedError
    
    def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        raise NotImplementedError


class YOLODetector(DetectorInterface):
    """YOLO検出器クラス"""
    
    def __init__(self):
        self.model: Optional[YOLO] = None
        self.config: Dict[str, Any] = {}
        self.initialized: bool = False
        self.model_load_time: float = 0.0
        self.inference_count: int = 0
        self.logger = logging.getLogger(__name__ + '.YOLODetector')
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """YOLO検出器を初期化 - モデルファイルの読み込みと検証"""
        self.config = config
        model_path = config.get('model_path')
        
        # 設定値の検証
        if not model_path:
            self.logger.error("Model path not specified in config")
            return False
        
        # モデルファイルの存在確認
        if not Path(model_path).exists():
            self.logger.error(f"Model file not found: {model_path}")
            return False
        
        # ultralyticsライブラリの利用可能性確認
        if YOLO is None:
            self.logger.error("YOLO not available. Please install ultralytics")
            return False
        
        try:
            # モデル読み込み時間を測定（性能監視用）
            start_time = time.time()
            self.model = YOLO(model_path)
            self.model_load_time = time.time() - start_time
            self.initialized = True
            self.logger.info(f"YOLO model loaded successfully in {self.model_load_time:.2f}s")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {e}")
            return False
    
    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """画像から昆虫を検出 - メイン検出処理パイプライン"""
        # 初期化状態の確認
        if not self.initialized or self.model is None:
            self.logger.error("Detector not initialized")
            return []
        
        # 入力画像の妥当性確認
        if not DataValidator.validate_image(image):
            self.logger.error("Invalid image for detection")
            return []
        
        try:
            # 前処理: BGR→RGB変換等
            processed_image = self.preprocess_image(image)
            
            # YOLO推論実行（verboseをFalseにして出力抑制）
            results = self.model(processed_image, verbose=False)
            self.inference_count += 1  # 推論回数をカウント
            
            # 後処理: 座標正規化・信頼度フィルタリング
            detections = self.postprocess_results(results, image.shape)
            
            self.logger.debug(f"Detected {len(detections)} insects")
            return detections
            
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            return []
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """画像の前処理 - YOLO入力形式への変換"""
        # BGR→RGB変換（OpenCVはBGR、YOLOはRGB想定）
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image_rgb
        return image
    
    def postprocess_results(self, results, img_shape: Tuple[int, int, int]) -> List[DetectionResult]:
        """推論結果の後処理 - バウンディングボックス座標の正規化と信頼度フィルタ"""
        detections = []
        current_time = datetime.now().isoformat()
        
        # 設定から信頼度閾値を取得（デフォルト0.5）
        confidence_threshold = self.config.get('confidence_threshold', 0.5)
        
        for result in results:
            # バウンディングボックスが検出された場合のみ処理
            if result.boxes is not None:
                for box in result.boxes:
                    confidence = float(box.conf.item())
                    
                    # 信頼度が閾値未満の場合はスキップ
                    if confidence < confidence_threshold:
                        continue
                    
                    # バウンディングボックス座標（xyxy形式: 左上・右下座標）
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # 中心座標と幅・高さを計算（画像サイズで正規化）
                    height, width = img_shape[:2]
                    x_center = (x1 + x2) / 2 / width    # 中心x座標（0-1）
                    y_center = (y1 + y2) / 2 / height   # 中心y座標（0-1）
                    bbox_width = (x2 - x1) / width      # 幅（0-1）
                    bbox_height = (y2 - y1) / height    # 高さ（0-1）
                    
                    # 座標の正規化と境界値チェック
                    x_center, y_center = DataValidator.sanitize_coordinates(
                        x_center * width, y_center * height, img_shape
                    )
                    
                    # クラスID取得（昆虫検出では通常0）
                    class_id = int(box.cls.item()) if box.cls is not None else 0
                    
                    try:
                        # DetectionResultオブジェクトを作成
                        detection = DetectionResult(
                            x_center=x_center,
                            y_center=y_center,
                            width=bbox_width,
                            height=bbox_height,
                            confidence=confidence,
                            class_id=class_id,
                            timestamp=current_time
                        )
                        detections.append(detection)
                    except ValueError as e:
                        # 不正な検出結果の場合は警告を出してスキップ
                        self.logger.warning(f"Invalid detection result: {e}")
                        continue
        
        return detections
    
    def get_status(self) -> Dict[str, Any]:
        """検出器の状態を取得"""
        return {
            'initialized': self.initialized,
            'model_loaded': self.model is not None,
            'model_load_time': self.model_load_time,
            'inference_count': self.inference_count,
            'config': self.config.copy()
        }
    
    def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        if self.model is not None:
            del self.model
            self.model = None
        self.initialized = False
        self.logger.info("YOLO detector cleaned up")


class HardwareController:
    """ハードウェア制御クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.camera: Optional[Picamera2] = None
        self.gpio_initialized = False
        self.led_pin = config.get('ir_led_pin', 18)
        self.led_pwm = None
        self.logger = logging.getLogger(__name__ + '.HardwareController')
    
    def initialize_hardware(self) -> bool:
        """ハードウェアを初期化"""
        success = True
        
        # カメラ初期化
        if not self._initialize_camera():
            success = False
        
        # GPIO初期化
        if not self._initialize_gpio():
            success = False
        
        return success
    
    def _initialize_camera(self) -> bool:
        """カメラを初期化（Camera V3 NoIR対応）"""
        if Picamera2 is None:
            self.logger.warning("Picamera2 not available, using mock camera")
            return True
        
        try:
            self.camera = Picamera2()
            
            # Camera V3用の高画質設定
            camera_config = self.camera.create_still_configuration(
                main={
                    "size": self.config.get('camera_resolution', (1640, 1232)),  # V3の最適解像度
                    "format": "RGB888"
                },
                controls={
                    "ExposureTime": self.config.get('exposure_time', 50000),  # 50ms（低照度対応）
                    "AnalogueGain": self.config.get('analogue_gain', 2.0),    # ゲイン調整
                    "AeEnable": False,  # 自動露出無効化（一定条件での検出のため）
                    "AwbEnable": True,  # ホワイトバランス有効
                    "AfMode": self.config.get('af_mode', 1),  # オートフォーカスモード
                    "AfTrigger": 0  # 連続オートフォーカス
                }
            )
            
            self.camera.configure(camera_config)
            self.camera.start()
            
            # Camera V3の場合、起動後少し待機
            time.sleep(2)
            
            self.logger.info("Camera V3 initialized successfully with optimized settings")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def _initialize_gpio(self) -> bool:
        """GPIO初期化"""
        if GPIO is None:
            self.logger.warning("RPi.GPIO not available, using mock GPIO")
            return True
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.led_pin, GPIO.OUT)
            self.led_pwm = GPIO.PWM(self.led_pin, 1000)  # 1kHz
            self.led_pwm.start(0)
            self.gpio_initialized = True
            self.logger.info("GPIO initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize GPIO: {e}")
            return False
    
    def capture_image(self) -> Optional[np.ndarray]:
        """画像を撮影"""
        if self.camera is None:
            self.logger.warning("Camera not available, returning mock image")
            # テスト用のダミー画像を返す
            return np.zeros((480, 640, 3), dtype=np.uint8)
        
        try:
            # カメラから画像を撮影
            image = self.camera.capture_array()
            return image
        except Exception as e:
            self.logger.error(f"Failed to capture image: {e}")
            return None
    
    def control_led(self, brightness: float) -> bool:
        """LED輝度制御"""
        if not self.gpio_initialized:
            self.logger.warning("GPIO not initialized, LED control skipped")
            return True
        
        try:
            # 輝度を0-100%の範囲に制限
            brightness = max(0, min(100, brightness))
            if self.led_pwm:
                self.led_pwm.ChangeDutyCycle(brightness)
            return True
        except Exception as e:
            self.logger.error(f"Failed to control LED: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態取得"""
        return {
            'camera_available': self.camera is not None,
            'gpio_initialized': self.gpio_initialized,
            'led_pin': self.led_pin
        }
    
    def cleanup_resources(self) -> None:
        """リソースクリーンアップ"""
        if self.camera:
            try:
                self.camera.stop()
                self.camera.close()
            except:
                pass
            self.camera = None
        
        if self.gpio_initialized and GPIO:
            try:
                if self.led_pwm:
                    self.led_pwm.stop()
                GPIO.cleanup()
            except:
                pass
            self.gpio_initialized = False
        
        self.logger.info("Hardware resources cleaned up")


class InsectDetector:
    """昆虫検出器メインクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.yolo_detector = YOLODetector()
        self.hardware_controller = HardwareController(config)
        self.performance_monitor = PerformanceMonitor()
        self.status = DetectionStatus.UNINITIALIZED
        self.detection_count = 0
        self.last_detection_time: Optional[datetime] = None
        self.logger = logging.getLogger(__name__ + '.InsectDetector')
        
        # ログレベル設定
        log_level = config.get('log_level', 'INFO')
        self.logger.setLevel(getattr(logging, log_level.upper()))
    
    def initialize(self) -> bool:
        """検出器を初期化"""
        self.status = DetectionStatus.INITIALIZING
        self.logger.info("Initializing insect detector...")
        
        try:
            # YOLO検出器初期化
            if not self.yolo_detector.initialize(self.config):
                self.status = DetectionStatus.ERROR
                return False
            
            # ハードウェア初期化
            if not self.hardware_controller.initialize_hardware():
                self.status = DetectionStatus.ERROR
                return False
            
            self.status = DetectionStatus.READY
            self.logger.info("Insect detector initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.status = DetectionStatus.ERROR
            return False
    
    def perform_detection(self) -> Dict[str, Any]:
        """検出処理を実行"""
        if self.status != DetectionStatus.READY:
            self.logger.error("Detector not ready for detection")
            return {'success': False, 'error': 'Detector not ready'}
        
        self.status = DetectionStatus.DETECTING
        self.performance_monitor.start_timer('detection_cycle')
        
        try:
            # LED点灯
            self.hardware_controller.control_led(
                self.config.get('ir_led_brightness', 50.0)
            )
            
            # 画像撮影
            self.performance_monitor.start_timer('image_capture')
            image = self.hardware_controller.capture_image()
            capture_time = self.performance_monitor.end_timer('image_capture')
            
            if image is None:
                self.status = DetectionStatus.READY
                return {'success': False, 'error': 'Failed to capture image'}
            
            # 昆虫検出
            self.performance_monitor.start_timer('yolo_inference')
            detections = self.yolo_detector.detect(image)
            inference_time = self.performance_monitor.end_timer('yolo_inference')
            
            # LED消灯
            self.hardware_controller.control_led(0.0)
            
            # 検出結果処理
            result = self._process_detection_results(
                detections, image, capture_time, inference_time
            )
            
            self.detection_count += 1
            self.last_detection_time = datetime.now()
            
            total_time = self.performance_monitor.end_timer('detection_cycle')
            result['processing_time_ms'] = total_time * 1000
            
            self.status = DetectionStatus.READY
            return result
            
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            self.status = DetectionStatus.READY
            return {'success': False, 'error': str(e)}
    
    def _process_detection_results(self, detections: List[DetectionResult], 
                                 image: np.ndarray, capture_time: float, 
                                 inference_time: float) -> Dict[str, Any]:
        """検出結果を処理"""
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'insect_detected': len(detections) > 0,
            'detection_count': len(detections),
            'detections': [d.to_dict() for d in detections],
            'image_shape': image.shape,
            'capture_time_ms': capture_time * 1000,
            'inference_time_ms': inference_time * 1000
        }
        
        # 信頼度統計
        if detections:
            confidences = [d.confidence for d in detections]
            result['confidence_stats'] = {
                'max': max(confidences),
                'min': min(confidences),
                'average': sum(confidences) / len(confidences)
            }
        
        self.logger.info(f"Detection completed: {len(detections)} insects found")
        return result
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """検出統計を取得"""
        return {
            'total_detections': self.detection_count,
            'last_detection_time': self.last_detection_time.isoformat() if self.last_detection_time else None,
            'status': self.status.value,
            'performance_stats': {
                'detection_cycle': self.performance_monitor.get_performance_stats('detection_cycle'),
                'image_capture': self.performance_monitor.get_performance_stats('image_capture'),
                'yolo_inference': self.performance_monitor.get_performance_stats('yolo_inference')
            },
            'yolo_stats': self.yolo_detector.get_status(),
            'hardware_stats': self.hardware_controller.get_system_status()
        }
    
    def reset_statistics(self) -> None:
        """統計をリセット"""
        self.detection_count = 0
        self.last_detection_time = None
        self.performance_monitor.reset_metrics()
        self.logger.info("Detection statistics reset")
    
    def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        self.status = DetectionStatus.CLEANUP
        
        try:
            self.yolo_detector.cleanup()
            self.hardware_controller.cleanup_resources()
            self.logger.info("Insect detector cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
        finally:
            self.status = DetectionStatus.UNINITIALIZED


def create_default_config() -> Dict[str, Any]:
    """デフォルト設定を作成（Camera V3 NoIR対応）"""
    return {
        'model_path': './weights/best.pt',
        'confidence_threshold': 0.5,
        'ir_led_pin': 18,
        'ir_led_brightness': 75.0,  # V3 NoIRの感度に合わせて調整
        'log_level': 'INFO',
        'camera_resolution': (1640, 1232),  # V3の最適解像度（4:3アスペクト比）
        'exposure_time': 50000,  # 50ms（昆虫観察に適した露出時間）
        'analogue_gain': 2.0,    # V3の低照度性能を活用
        'af_mode': 1             # 連続オートフォーカス
    }


if __name__ == "__main__":
    # テスト実行例
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = create_default_config()
    detector = InsectDetector(config)
    
    try:
        if detector.initialize():
            print("Detector initialized successfully")
            
            # 検出テスト実行
            result = detector.perform_detection()
            print(f"Detection result: {result}")
            
            # 統計表示
            stats = detector.get_detection_statistics()
            print(f"Statistics: {json.dumps(stats, indent=2, default=str)}")
        else:
            print("Failed to initialize detector")
    
    finally:
        detector.cleanup()