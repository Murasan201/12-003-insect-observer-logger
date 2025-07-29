"""
昆虫検出処理モジュール

YOLOv8を使用した昆虫検出処理の実行と制御を行う。
- YOLOv8モデル推論実行
- 検出結果の処理・検証
- カメラ制御・IR LED制御との連携
- 検出品質の評価
- バッチ処理対応
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import threading

# 機械学習・画像処理ライブラリ
try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("ultralytics not available. Install with: pip install ultralytics")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available. Install with: pip install opencv-python")

# プロジェクト内モジュール
from models.detection_models import DetectionResult, DetectionRecord
from models.system_models import SystemLogRecord
from hardware_controller import HardwareController
from utils.data_validator import DataValidator
from utils.file_naming import generate_detection_image_name, generate_log_filename
from error_handler import ErrorHandler, ErrorSeverity, ErrorCategory, ErrorContext, error_handler_decorator


@dataclass
class DetectionSettings:
    """検出設定データクラス"""
    model_path: str = "./weights/beetle_detection.pt"
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    max_detections: int = 10
    input_size: Tuple[int, int] = (640, 640)
    device: str = "cpu"  # "cpu" or "cuda"
    half_precision: bool = False
    save_detection_images: bool = True
    save_confidence_maps: bool = False
    detection_classes: List[int] = None  # None = all classes


@dataclass
class DetectionStats:
    """検出統計情報"""
    total_detections: int = 0
    total_images_processed: int = 0
    average_inference_time: float = 0.0
    average_confidence: float = 0.0
    detection_rate: float = 0.0  # 検出成功率
    error_count: int = 0
    last_detection_time: str = ""
    model_load_time: float = 0.0


class InsectDetector:
    """
    昆虫検出処理クラス
    
    Features:
    - YOLOv8による高精度昆虫検出
    - リアルタイム推論
    - IR照明との自動連携
    - 検出結果の自動保存
    - 品質評価・統計収集
    - バッチ処理対応
    """
    
    def __init__(self, 
                 settings: Optional[DetectionSettings] = None,
                 hardware_controller: Optional[HardwareController] = None):
        """
        検出器初期化
        
        Args:
            settings: 検出設定
            hardware_controller: ハードウェア制御器
        """
        self.logger = logging.getLogger(__name__ + '.InsectDetector')
        
        # 設定
        self.settings = settings or DetectionSettings()
        
        # ハードウェア制御
        self.hardware_controller = hardware_controller
        
        # YOLOモデル
        self.model: Optional[YOLO] = None
        self.model_loaded = False
        
        # 統計・状態管理
        self.stats = DetectionStats()
        self.is_initialized = False
        self.inference_times = []
        self.confidences = []
        
        # データ検証器
        self.validator = DataValidator()
        
        # 可用性チェック
        self.available = YOLO_AVAILABLE and OPENCV_AVAILABLE
        if not self.available:
            self.logger.error("Required libraries not available for detection")
    
    def initialize(self) -> bool:
        """
        検出器初期化
        
        Returns:
            bool: 初期化成功可否
        """
        if not self.available:
            self.logger.error("Cannot initialize detector: required libraries not available")
            return False
        
        try:
            self.logger.info("Initializing insect detector...")
            
            # モデル読み込み
            if not self._load_model():
                return False
            
            # ハードウェア制御器チェック
            if self.hardware_controller is not None:
                hw_status = self.hardware_controller.get_system_status()
                if not hw_status.camera_initialized:
                    self.logger.warning("Camera not initialized in hardware controller")
            
            self.is_initialized = True
            self.logger.info("Insect detector initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Detector initialization failed: {e}")
            return False
    
    def _load_model(self) -> bool:
        """YOLOv8モデル読み込み"""
        try:
            model_path = Path(self.settings.model_path)
            if not model_path.exists():
                self.logger.error(f"Model file not found: {model_path}")
                return False
            
            self.logger.info(f"Loading YOLO model: {model_path}")
            start_time = time.time()
            
            # モデル読み込み
            self.model = YOLO(str(model_path))
            
            # デバイス設定
            if torch.cuda.is_available() and self.settings.device == "cuda":
                self.model.to('cuda')
                self.logger.info("Model loaded on CUDA")
            else:
                self.model.to('cpu')
                self.logger.info("Model loaded on CPU")
            
            # 半精度設定
            if self.settings.half_precision and self.settings.device == "cuda":
                self.model.half()
                self.logger.info("Model set to half precision")
            
            load_time = time.time() - start_time
            self.stats.model_load_time = load_time
            self.model_loaded = True
            
            self.logger.info(f"Model loaded successfully in {load_time:.2f}s")
            
            # モデル情報表示
            model_info = self._get_model_info()
            self.logger.info(f"Model info: {model_info}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Model loading failed: {e}")
            return False
    
    def _get_model_info(self) -> Dict[str, Any]:
        """モデル情報取得"""
        if not self.model_loaded or self.model is None:
            return {"status": "not_loaded"}
        
        try:
            # YOLOモデルの基本情報
            info = {
                "model_type": "YOLOv8",
                "task": getattr(self.model, 'task', 'unknown'),
                "device": str(self.model.device) if hasattr(self.model, 'device') else 'unknown',
                "input_size": self.settings.input_size,
                "confidence_threshold": self.settings.confidence_threshold,
                "nms_threshold": self.settings.nms_threshold
            }
            
            # クラス情報
            if hasattr(self.model, 'names'):
                info['classes'] = self.model.names
                info['num_classes'] = len(self.model.names)
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get model info: {e}")
            return {"status": "error", "error": str(e)}
    
    def detect_single_image(self, 
                           image: Optional[np.ndarray] = None,
                           image_path: Optional[str] = None,
                           use_ir_led: bool = True,
                           save_result: bool = True) -> Optional[DetectionRecord]:
        """
        単一画像の昆虫検出
        
        Args:
            image: 入力画像（指定時はこちらを優先）
            image_path: 画像ファイルパス
            use_ir_led: IR LED使用可否
            save_result: 結果保存可否
            
        Returns:
            Optional[DetectionRecord]: 検出記録
        """
        if not self.is_initialized:
            self.logger.error("Detector not initialized")
            return None
        
        try:
            start_time = time.time()
            
            # 画像取得
            if image is None:
                if image_path is not None:
                    image = cv2.imread(image_path)
                elif self.hardware_controller is not None:
                    image = self._capture_with_ir_led(use_ir_led)
                else:
                    self.logger.error("No image source available")
                    return None
            
            if image is None:
                self.logger.error("Failed to obtain image")
                return None
            
            # 画像検証
            if not self.validator.validate_image(image):
                self.logger.error("Invalid image format")
                return None
            
            # YOLOv8推論実行
            detection_results = self._run_inference(image)
            
            # 検出記録作成
            timestamp = datetime.now().isoformat()
            record = DetectionRecord(
                timestamp=timestamp,
                image_path=image_path or "",
                detection_count=len(detection_results),
                detections=detection_results,
                processing_time_ms=int((time.time() - start_time) * 1000),
                confidence_threshold=self.settings.confidence_threshold,
                model_version="YOLOv8"
            )
            
            # 結果保存
            if save_result and len(detection_results) > 0:
                self._save_detection_result(image, record)
            
            # 統計更新
            self._update_stats(record, time.time() - start_time)
            
            self.logger.debug(f"Detection completed: {len(detection_results)} insects found "
                            f"in {record.processing_time_ms}ms")
            
            return record
            
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            self.stats.error_count += 1
            return None
    
    def _capture_with_ir_led(self, use_ir_led: bool = True) -> Optional[np.ndarray]:
        """IR LED制御付き画像撮影"""
        if self.hardware_controller is None:
            self.logger.error("Hardware controller not available")
            return None
        
        try:
            # IR LED点灯
            if use_ir_led:
                self.hardware_controller.control_ir_led(0.8)
                time.sleep(0.1)  # LED安定化待機
            
            # 画像撮影
            image = self.hardware_controller.capture_image()
            
            # IR LED消灯
            if use_ir_led:
                self.hardware_controller.control_ir_led(0.0)
            
            return image
            
        except Exception as e:
            self.logger.error(f"IR LED capture failed: {e}")
            # エラー時はLED消灯を保証
            if use_ir_led and self.hardware_controller is not None:
                try:
                    self.hardware_controller.control_ir_led(0.0)
                except:
                    pass
            return None
    
    def _run_inference(self, image: np.ndarray) -> List[DetectionResult]:
        """YOLOv8推論実行"""
        if not self.model_loaded or self.model is None:
            self.logger.error("Model not loaded")
            return []
        
        try:
            inference_start = time.time()
            
            # 推論実行
            results = self.model(
                image,
                conf=self.settings.confidence_threshold,
                iou=self.settings.nms_threshold,
                max_det=self.settings.max_detections,
                imgsz=self.settings.input_size,
                device=self.settings.device,
                half=self.settings.half_precision,
                verbose=False
            )
            
            inference_time = time.time() - inference_start
            self.inference_times.append(inference_time)
            
            # 結果変換
            detection_results = []
            timestamp = datetime.now().isoformat()
            
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes
                    
                    for i in range(len(boxes)):
                        # バウンディングボックス情報
                        box = boxes.xyxy[i].cpu().numpy()  # x1, y1, x2, y2
                        conf = float(boxes.conf[i].cpu().numpy())
                        cls = int(boxes.cls[i].cpu().numpy())
                        
                        # 中心座標・サイズ変換
                        x_center = (box[0] + box[2]) / 2
                        y_center = (box[1] + box[3]) / 2
                        width = box[2] - box[0]
                        height = box[3] - box[1]
                        
                        # DetectionResult作成
                        detection = DetectionResult(
                            x_center=float(x_center),
                            y_center=float(y_center),
                            width=float(width),
                            height=float(height),
                            confidence=conf,
                            class_id=cls,
                            timestamp=timestamp
                        )
                        
                        # 検証
                        if self.validator.validate_detection_result(detection):
                            detection_results.append(detection)
                            self.confidences.append(conf)
                        else:
                            self.logger.warning(f"Invalid detection result: {detection}")
            
            self.logger.debug(f"Inference completed in {inference_time:.3f}s, "
                            f"found {len(detection_results)} valid detections")
            
            return detection_results
            
        except Exception as e:
            self.logger.error(f"Inference failed: {e}")
            return []
    
    def _save_detection_result(self, image: np.ndarray, record: DetectionRecord) -> None:
        """検出結果保存"""
        if not self.settings.save_detection_images:
            return
        
        try:
            # 保存ディレクトリ作成
            output_dir = Path("./output/detections")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # ファイル名生成
            filename = generate_detection_image_name(
                datetime.fromisoformat(record.timestamp),
                record.detection_count
            )
            
            image_path = output_dir / filename
            
            # 検出結果描画
            annotated_image = self._draw_detections(image.copy(), record.detections)
            
            # 画像保存
            cv2.imwrite(str(image_path), annotated_image)
            
            # 記録更新
            record.image_path = str(image_path)
            
            self.logger.debug(f"Detection result saved: {image_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save detection result: {e}")
    
    def _draw_detections(self, image: np.ndarray, detections: List[DetectionResult]) -> np.ndarray:
        """検出結果を画像に描画"""
        try:
            for detection in detections:
                # バウンディングボックス座標計算
                x1 = int(detection.x_center - detection.width / 2)
                y1 = int(detection.y_center - detection.height / 2)
                x2 = int(detection.x_center + detection.width / 2)
                y2 = int(detection.y_center + detection.height / 2)
                
                # 色設定（信頼度に応じて）
                if detection.confidence > 0.8:
                    color = (0, 255, 0)  # 緑（高信頼度）
                elif detection.confidence > 0.6:
                    color = (0, 255, 255)  # 黄（中信頼度）
                else:
                    color = (0, 0, 255)  # 赤（低信頼度）
                
                # バウンディングボックス描画
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                
                # ラベル描画
                label = f"Insect {detection.confidence:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), color, -1)
                cv2.putText(image, label, (x1, y1 - 5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to draw detections: {e}")
            return image
    
    def _update_stats(self, record: DetectionRecord, processing_time: float) -> None:
        """統計情報更新"""
        try:
            self.stats.total_images_processed += 1
            self.stats.total_detections += record.detection_count
            
            # 平均推論時間更新
            if self.inference_times:
                self.stats.average_inference_time = np.mean(self.inference_times[-100:])  # 直近100回
            
            # 平均信頼度更新
            if self.confidences:
                self.stats.average_confidence = np.mean(self.confidences[-1000:])  # 直近1000検出
            
            # 検出成功率更新
            if self.stats.total_images_processed > 0:
                images_with_detections = sum(1 for _ in range(self.stats.total_images_processed) 
                                           if record.detection_count > 0)
                self.stats.detection_rate = images_with_detections / self.stats.total_images_processed
            
            # 最後の検出時刻更新
            if record.detection_count > 0:
                self.stats.last_detection_time = record.timestamp
            
        except Exception as e:
            self.logger.error(f"Stats update failed: {e}")
    
    def detect_batch(self, 
                    image_paths: List[str],
                    use_ir_led: bool = False,
                    save_results: bool = True) -> List[DetectionRecord]:
        """
        バッチ検出処理
        
        Args:
            image_paths: 画像ファイルパスリスト
            use_ir_led: IR LED使用（通常はファイル処理時は不要）
            save_results: 結果保存可否
            
        Returns:
            List[DetectionRecord]: 検出記録リスト
        """
        if not self.is_initialized:
            self.logger.error("Detector not initialized")
            return []
        
        self.logger.info(f"Starting batch detection: {len(image_paths)} images")
        
        results = []
        for i, image_path in enumerate(image_paths):
            try:
                self.logger.debug(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
                
                record = self.detect_single_image(
                    image_path=image_path,
                    use_ir_led=use_ir_led,
                    save_result=save_results
                )
                
                if record is not None:
                    results.append(record)
                else:
                    self.logger.warning(f"Failed to process: {image_path}")
                
            except Exception as e:
                self.logger.error(f"Batch processing error for {image_path}: {e}")
                continue
        
        self.logger.info(f"Batch detection completed: {len(results)}/{len(image_paths)} successful")
        return results
    
    def get_detection_stats(self) -> DetectionStats:
        """検出統計取得"""
        return self.stats
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """詳細状態情報取得"""
        return {
            "detector_status": {
                "available": self.available,
                "initialized": self.is_initialized,
                "model_loaded": self.model_loaded,
                "yolo_available": YOLO_AVAILABLE,
                "opencv_available": OPENCV_AVAILABLE
            },
            "model_info": self._get_model_info(),
            "statistics": {
                "total_detections": self.stats.total_detections,
                "total_images_processed": self.stats.total_images_processed,
                "average_inference_time": self.stats.average_inference_time,
                "average_confidence": self.stats.average_confidence,
                "detection_rate": self.stats.detection_rate,
                "error_count": self.stats.error_count,
                "last_detection_time": self.stats.last_detection_time,
                "model_load_time": self.stats.model_load_time
            },
            "settings": {
                "model_path": self.settings.model_path,
                "confidence_threshold": self.settings.confidence_threshold,
                "nms_threshold": self.settings.nms_threshold,
                "max_detections": self.settings.max_detections,
                "device": self.settings.device,
                "input_size": self.settings.input_size
            }
        }
    
    def update_settings(self, new_settings: DetectionSettings) -> bool:
        """
        設定更新
        
        Args:
            new_settings: 新しい設定
            
        Returns:
            bool: 更新成功可否
        """
        try:
            # モデルパスが変更された場合は再読み込み
            if new_settings.model_path != self.settings.model_path:
                self.settings = new_settings
                return self._load_model()
            
            self.settings = new_settings
            self.logger.info("Detection settings updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Settings update failed: {e}")
            return False
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            # モデル解放
            if self.model is not None:
                del self.model
                self.model = None
                self.model_loaded = False
            
            # GPU メモリクリア
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.is_initialized = False
            self.logger.info("Insect detector cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Detector cleanup failed: {e}")


# 使用例・テスト関数
def test_insect_detector():
    """昆虫検出器のテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 検出設定
    settings = DetectionSettings(
        model_path="./weights/beetle_detection.pt",
        confidence_threshold=0.5,
        device="cpu"
    )
    
    # 検出器作成
    detector = InsectDetector(settings)
    
    try:
        # 初期化
        if detector.initialize():
            logger.info("Detector initialized successfully")
            
            # 状態表示
            status = detector.get_detailed_status()
            logger.info(f"Detector status: {status}")
            
            # テスト画像での検出（ファイルが存在する場合）
            test_image_path = "./test_images/test_insect.jpg"
            if Path(test_image_path).exists():
                logger.info("Testing detection with file...")
                result = detector.detect_single_image(image_path=test_image_path)
                if result:
                    logger.info(f"Detection result: {result.detection_count} insects found")
                    
            # 統計表示
            stats = detector.get_detection_stats()
            logger.info(f"Detection stats: {stats}")
            
        else:
            logger.error("Detector initialization failed")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        detector.cleanup()


if __name__ == "__main__":
    test_insect_detector()