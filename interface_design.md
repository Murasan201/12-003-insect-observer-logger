# インターフェース設計書

**文書番号**: 12-002-IF-001  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: インターフェース設計書  
**バージョン**: 1.0  
**作成日**: 2025-07-25  
**作成者**: 開発チーム  

---

## 1. 文書概要

### 1.1 目的
本文書は昆虫自動観察システムの各種インターフェース仕様を詳細に定義し、システム内外の連携方法、操作方法、およびデータ交換形式を明確化する。

### 1.2 適用範囲
- ユーザーインターフェース設計
- モジュール間インターフェース設計  
- 外部システム連携インターフェース
- ハードウェアインターフェース仕様
- データ交換インターフェース
- 運用・保守インターフェース

### 1.3 関連文書
- システムアーキテクチャ設計書（system_architecture_design.md）
- ソフトウェア設計書（software_design.md）
- データ設計書（data_design.md）
- 要件定義書（12-002）

---

## 2. インターフェース全体構成

### 2.1 インターフェース構成図

```
┌─────────────────────────────────────────────────────────────────┐
│                インターフェース全体構成                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │                 │  │                 │  │                 │  │
│  │ ユーザー        │  │  システム内部   │  │  外部システム   │  │
│  │インターフェース  │  │ インターフェース │  │ インターフェース │  │
│  │ User Interface  │  │Internal Interface│  │External Interface│  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │ コマンド     │ │  │ │ モジュール   │ │  │ │ Hugging     │ │  │
│  │ │ ライン      │ │  │ │ 間API       │ │  │ │ Face Hub    │ │  │
│  │ │ CLI         │ │  │ │             │ │  │ │ API         │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  │                 │  │        │        │  │                 │  │
│  │ ┌─────────────┐ │  │        ▼        │  │ ┌─────────────┐ │  │
│  │ │ 設定ファイル │ │◄─┼─┌─────────────┐ │  │ │ システム     │ │  │
│  │ │ インター     │ │  │ │ ハード      │ │──┼─│ 監視API     │ │  │
│  │ │ フェース     │ │  │ │ ウェア      │ │  │ │             │ │  │
│  │ └─────────────┘ │  │ │ 制御API     │ │  │ └─────────────┘ │  │
│  │                 │  │ └─────────────┘ │  │                 │  │
│  │ ┌─────────────┐ │  │        │        │  │ ┌─────────────┐ │  │
│  │ │ ログ出力     │ │◄─┘        ▼        │  │ │ データ      │ │  │
│  │ │ インター     │ │    ┌─────────────┐ │  │ │ エクスポート │ │  │
│  │ │ フェース     │ │    │ データ      │ │──┼─│ API         │ │  │
│  │ └─────────────┘ │    │ アクセス    │ │  │ └─────────────┘ │  │
│  │                 │    │ API         │ │  │                 │  │
│  │ ┌─────────────┐ │    └─────────────┘ │  │ ┌─────────────┐ │  │
│  │ │ 可視化       │ │                    │  │ │ メンテナンス │ │  │
│  │ │ インター     │ │                    │  │ │ インター     │ │  │
│  │ │ フェース     │ │                    │  │ │ フェース     │ │  │
│  │ └─────────────┘ │                    │  │ └─────────────┘ │  │
│  │                 │                    │  │                 │  │
│  └─────────────────┘                    │  └─────────────────┘  │
│                                         │                       │
├─────────────────────────────────────────┴───────────────────────┤
│                   ハードウェアインターフェース                    │
│                  Hardware Interface Layer                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │                 │  │                 │  │                 │  │
│  │ カメラ          │  │ GPIO            │  │ ファイル        │  │
│  │ インター        │  │ インター        │  │ システム        │  │
│  │ フェース        │  │ フェース        │  │ インター        │  │
│  │                 │  │                 │  │ フェース        │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │ picamera2   │ │  │ │ RPi.GPIO    │ │  │ │ CSV/JSON    │ │  │
│  │ │ API         │ │  │ │ PWM制御     │ │  │ │ ファイル     │ │  │
│  │ │             │ │  │ │             │ │  │ │ I/O         │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │ 画像キャプチャ│ │  │ │ LED明度制御 │ │  │ │ 画像ファイル │ │  │
│  │ │ 制御        │ │  │ │ インター    │ │  │ │ I/O         │ │  │
│  │ │             │ │  │ │ フェース    │ │  │ │             │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 インターフェース分類

| 分類 | 説明 | 対象 | 重要度 |
|------|------|------|--------|
| **ユーザーインターフェース** | 人間とシステム間の操作インターフェース | 管理者・オペレーター | 高 |
| **モジュール間インターフェース** | システム内部コンポーネント間の通信 | 各ソフトウェアモジュール | 高 |
| **ハードウェアインターフェース** | ソフトウェアとハードウェア間の制御 | カメラ・GPIO・ストレージ | 高 |
| **外部システムインターフェース** | 外部サービス・システムとの連携 | Hugging Face・監視システム | 中 |
| **データ交換インターフェース** | データ入出力・変換処理 | ファイル・ネットワーク | 中 |
| **運用保守インターフェース** | システム運用・保守作業支援 | ログ・診断・バックアップ | 中 |

---

## 3. ユーザーインターフェース設計

### 3.1 コマンドラインインターフェース (CLI)

#### 3.1.1 基本コマンド構造
```bash
# 基本構文
python main.py [OPTIONS] [COMMAND] [ARGS]

# 全体オプション
--config, -c FILE    設定ファイル指定 (default: ./config/system_config.json)
--log-level LEVEL    ログレベル指定 (DEBUG|INFO|WARNING|ERROR)
--verbose, -v        詳細出力モード
--quiet, -q          静寂出力モード
--help, -h           ヘルプ表示
--version            バージョン情報表示
```

#### 3.1.2 主要コマンド仕様

##### 3.1.2.1 連続観察モード
```bash
# 連続観察開始
python main.py run [OPTIONS]

OPTIONS:
  --interval SECONDS     検出間隔秒数 (default: 60)
  --duration HOURS       実行継続時間 (default: 無制限)
  --daemon              デーモンモードで実行
  --pid-file FILE       PIDファイル保存パス

EXAMPLES:
  # 標準設定で連続観察開始
  python main.py run
  
  # 30秒間隔で24時間実行
  python main.py run --interval 30 --duration 24
  
  # デーモンモードで実行
  python main.py run --daemon --pid-file /var/run/insect_observer.pid
```

##### 3.1.2.2 単発検出モード
```bash
# 単発検出実行
python main.py detect [OPTIONS]

OPTIONS:
  --output-dir DIR      出力ディレクトリ (default: ./output)
  --save-image         検出画像を保存
  --no-led             LED照明を使用しない
  --model FILE         カスタムモデル指定

EXAMPLES:
  # 単発検出実行
  python main.py detect
  
  # 画像保存付きで検出
  python main.py detect --save-image --output-dir ./test_output
  
  # カスタムモデルで検出
  python main.py detect --model ./models/custom_beetle_v2.pt
```

##### 3.1.2.3 分析・レポート生成
```bash
# データ分析実行
python main.py analyze [OPTIONS] DATE_OR_RANGE

POSITIONAL ARGUMENTS:
  DATE_OR_RANGE         分析対象日付 (YYYY-MM-DD) または期間 (YYYY-MM-DD:YYYY-MM-DD)

OPTIONS:
  --output-format FORMAT  出力形式 (csv|json|html) (default: csv)
  --include-charts        グラフ生成を含める
  --export-images         画像データもエクスポート

EXAMPLES:
  # 特定日の分析
  python main.py analyze 2025-07-25
  
  # 期間分析（グラフ付き）
  python main.py analyze 2025-07-01:2025-07-31 --include-charts
  
  # HTML形式で詳細レポート生成
  python main.py analyze 2025-07-25 --output-format html --include-charts
```

##### 3.1.2.4 システム制御
```bash
# システム状態確認
python main.py status [OPTIONS]

OPTIONS:
  --json               JSON形式で出力
  --detailed           詳細情報表示

# システム診断実行
python main.py diagnose [OPTIONS]

OPTIONS:
  --full               完全診断実行
  --output-file FILE   結果をファイル出力

# データクリーンアップ
python main.py cleanup [OPTIONS]

OPTIONS:
  --dry-run            実際の削除は行わない（確認のみ）
  --older-than DAYS    指定日数より古いデータを削除

EXAMPLES:
  # システム状態確認
  python main.py status --detailed
  
  # 完全診断実行
  python main.py diagnose --full --output-file ./reports/diagnosis.json
  
  # 30日より古いデータをクリーンアップ（確認のみ）
  python main.py cleanup --older-than 30 --dry-run
```

#### 3.1.3 CLI出力フォーマット

##### 3.1.3.1 標準出力フォーマット
```bash
# 実行時出力例
$ python main.py run
[2025-07-25 10:30:00] INFO: System initialization started
[2025-07-25 10:30:01] INFO: Camera initialized (1920x1080)
[2025-07-25 10:30:01] INFO: GPIO initialized (LED pin: 18)
[2025-07-25 10:30:02] INFO: Model loaded: beetle_detection_v1.pt
[2025-07-25 10:30:02] INFO: Starting detection loop (interval: 60s)
[2025-07-25 10:31:02] INFO: Detection completed - 2 insects found (confidence: 0.85, 0.92)
[2025-07-25 10:32:02] INFO: Detection completed - No insects detected
[2025-07-25 10:33:02] INFO: Detection completed - 1 insect found (confidence: 0.78)
^C
[2025-07-25 10:33:15] INFO: Shutdown signal received
[2025-07-25 10:33:16] INFO: System shutdown completed

Session Summary:
  Duration: 3m 16s
  Total detections: 180
  Insects found: 23
  Detection rate: 12.8%
  Average processing time: 2.3s
```

##### 3.1.3.2 JSON出力フォーマット
```json
{
  "command": "status",
  "timestamp": "2025-07-25T10:30:00+09:00",
  "system_status": {
    "overall": "healthy",
    "components": {
      "camera": {
        "status": "active",
        "resolution": [1920, 1080],
        "fps": 30,
        "last_capture": "2025-07-25T10:29:45+09:00"
      },
      "gpio": {
        "status": "active",
        "led_brightness": 0.8,
        "led_status": "off"
      },
      "model": {
        "status": "loaded",
        "model_path": "./weights/beetle_detection_v1.pt",
        "version": "v1.0.0",
        "load_time_ms": 1247.3
      },
      "storage": {
        "status": "healthy",
        "available_space_gb": 28.4,
        "usage_percentage": 15.2
      }
    },
    "performance": {
      "cpu_usage_percent": 34.2,
      "memory_usage_percent": 28.7,
      "temperature_celsius": 42.1,
      "uptime_seconds": 3847
    },
    "recent_activity": {
      "last_detection": "2025-07-25T10:29:02+09:00",
      "detections_last_hour": 5,
      "average_processing_time_ms": 2347.8
    }
  }
}
```

### 3.2 設定ファイルインターフェース

#### 3.2.1 メイン設定ファイル (system_config.json)
```json
{
  "$schema": "./schema/system_config_schema.json",
  "config_metadata": {
    "version": "1.0.0",
    "last_updated": "2025-07-25T09:00:00+09:00",
    "description": "昆虫自動観察システム メイン設定"
  },
  "system": {
    "detection_interval_seconds": 60,
    "log_level": "INFO",
    "timezone": "Asia/Tokyo",
    "data_retention_days": 365,
    "auto_cleanup_enabled": true,
    "enable_performance_monitoring": true
  },
  "hardware": {
    "camera": {
      "resolution": [1920, 1080],
      "fps": 30,
      "auto_exposure": true,
      "exposure_compensation": 0,
      "white_balance": "auto",
      "image_format": "bgr"
    },
    "ir_led": {
      "gpio_pin": 18,
      "brightness": 0.8,
      "pwm_frequency": 1000,
      "fade_duration_ms": 100,
      "enable_auto_brightness": false
    }
  },
  "detection": {
    "model_config": {
      "model_path": "./weights/beetle_detection_v1.pt",
      "confidence_threshold": 0.5,
      "nms_threshold": 0.4,
      "max_detections_per_frame": 10,
      "input_size": [640, 640]
    },
    "preprocessing": {
      "resize_method": "letterbox",
      "normalization": "yolo_standard",
      "augmentation_enabled": false
    },
    "postprocessing": {
      "filter_small_detections": true,
      "min_bbox_area": 100,
      "merge_nearby_detections": true,
      "merge_threshold": 0.3
    }
  },
  "analysis": {
    "movement_analysis": {
      "movement_threshold_pixels": 5.0,
      "max_movement_per_frame": 200.0,
      "outlier_detection_enabled": true,
      "outlier_threshold_sigma": 3.0
    },
    "activity_calculation": {
      "time_window_minutes": 60,
      "smoothing_enabled": true,
      "smoothing_window_size": 5,
      "peak_detection_enabled": true
    }
  },
  "data_management": {
    "storage": {
      "base_directory": "./data",
      "auto_create_directories": true,
      "file_permissions": "644",
      "directory_permissions": "755"
    },
    "backup": {
      "enabled": true,
      "schedule": "daily",
      "retention_days": 30,
      "compression_enabled": true,
      "backup_location": "./backup"
    },
    "export": {
      "csv_encoding": "utf-8",
      "csv_delimiter": ",",
      "datetime_format": "ISO8601",
      "number_precision": 3
    }
  },
  "logging": {
    "console": {
      "enabled": true,
      "level": "INFO",
      "format": "[%(asctime)s] %(levelname)s: %(message)s"
    },
    "file": {
      "enabled": true,
      "level": "DEBUG",
      "rotation": "daily",
      "max_files": 30,
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "performance": {
      "enabled": true,
      "interval_seconds": 300,
      "metrics": ["cpu", "memory", "temperature", "disk"]
    }
  }
}
```

#### 3.2.2 設定検証スキーマ
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "昆虫観察システム設定スキーマ",
  "type": "object",
  "required": ["config_metadata", "system", "hardware", "detection"],
  "properties": {
    "config_metadata": {
      "type": "object",
      "required": ["version"],
      "properties": {
        "version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$",
          "description": "設定バージョン (セマンティックバージョニング)"
        },
        "last_updated": {
          "type": "string",
          "format": "date-time",
          "description": "最終更新日時 (ISO8601形式)"
        }
      }
    },
    "system": {
      "type": "object",
      "required": ["detection_interval_seconds"],
      "properties": {
        "detection_interval_seconds": {
          "type": "integer",
          "minimum": 10,
          "maximum": 3600,
          "description": "検出実行間隔（秒）"
        },
        "log_level": {
          "type": "string",
          "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
          "description": "ログレベル"
        }
      }
    },
    "hardware": {
      "type": "object",
      "required": ["camera", "ir_led"],
      "properties": {
        "camera": {
          "type": "object",
          "required": ["resolution"],
          "properties": {
            "resolution": {
              "type": "array",
              "items": {"type": "integer", "minimum": 1},
              "minItems": 2,
              "maxItems": 2,
              "description": "カメラ解像度 [幅, 高さ]"
            },
            "fps": {
              "type": "integer",
              "minimum": 1,
              "maximum": 60,
              "description": "フレームレート"
            }
          }
        },
        "ir_led": {
          "type": "object",
          "required": ["gpio_pin", "brightness"],
          "properties": {
            "gpio_pin": {
              "type": "integer",
              "minimum": 1,
              "maximum": 40,
              "description": "GPIO ピン番号"
            },
            "brightness": {
              "type": "number",
              "minimum": 0.0,
              "maximum": 1.0,
              "description": "LED明度 (0.0-1.0)"
            }
          }
        }
      }
    }
  }
}
```

### 3.3 ログ出力インターフェース

#### 3.3.1 構造化ログフォーマット
```python
class StructuredLogger:
    """構造化ログ出力クラス"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.setup_structured_logging()
    
    def log_detection_event(self, 
                          detection_result: DetectionResult,
                          processing_time_ms: float,
                          system_stats: Dict[str, Any]) -> None:
        """検出イベントログ出力"""
        
        log_data = {
            "event_type": "detection",
            "timestamp": datetime.now().isoformat(),
            "detection": {
                "insect_detected": detection_result.insect_detected,
                "detection_count": detection_result.detection_count,
                "confidence": detection_result.confidence,
                "coordinates": {
                    "x_center": detection_result.x_center,
                    "y_center": detection_result.y_center
                } if detection_result.insect_detected else None
            },
            "performance": {
                "processing_time_ms": processing_time_ms,
                "cpu_usage_percent": system_stats.get("cpu_percent"),
                "memory_usage_percent": system_stats.get("memory_percent"),
                "temperature_celsius": system_stats.get("temperature")
            },
            "model": {
                "version": detection_result.model_version,
                "threshold": 0.5
            }
        }
        
        self.logger.info("Detection completed", extra={"structured_data": log_data})
    
    def log_system_event(self, 
                        event_type: str,
                        message: str,
                        details: Dict[str, Any] = None) -> None:
        """システムイベントログ出力"""
        
        log_data = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "details": details or {}
        }
        
        self.logger.info(message, extra={"structured_data": log_data})

# 出力例
{
  "timestamp": "2025-07-25T10:30:15.123456+09:00",
  "level": "INFO",
  "logger": "insect_detector",
  "message": "Detection completed",
  "structured_data": {
    "event_type": "detection",
    "timestamp": "2025-07-25T10:30:15.123456+09:00",
    "detection": {
      "insect_detected": true,
      "detection_count": 2,
      "confidence": 0.85,
      "coordinates": {
        "x_center": 320.5,
        "y_center": 240.3
      }
    },
    "performance": {
      "processing_time_ms": 2847.3,
      "cpu_usage_percent": 45.2,
      "memory_usage_percent": 62.8,
      "temperature_celsius": 48.5
    },
    "model": {
      "version": "v1.0.0",
      "threshold": 0.5
    }
  }
}
```

---

## 4. モジュール間インターフェース設計

### 4.1 内部API仕様

#### 4.1.1 検出器API
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable

class DetectorInterface(ABC):
    """検出器インターフェース"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """検出器初期化
        
        Args:
            config: 検出器設定
            
        Returns:
            初期化成功可否
        """
        pass
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """昆虫検出実行
        
        Args:
            image: 入力画像 (H×W×3, BGR)
            
        Returns:
            検出結果リスト
            
        Raises:
            DetectionError: 検出処理エラー
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """検出器状態取得
        
        Returns:
            状態情報辞書
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """リソース解放"""
        pass

class AsyncDetectorInterface(DetectorInterface):
    """非同期検出器インターフェース"""
    
    @abstractmethod
    async def detect_async(self, 
                          image: np.ndarray,
                          callback: Optional[Callable[[List[DetectionResult]], None]] = None
                         ) -> List[DetectionResult]:
        """非同期昆虫検出実行
        
        Args:
            image: 入力画像
            callback: 結果受信コールバック関数
            
        Returns:
            検出結果リスト
        """
        pass

# 実装例
class YOLODetector(DetectorInterface):
    """YOLO検出器実装"""
    
    def __init__(self):
        self.model = None
        self.config = None
        self.initialized = False
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """検出器初期化実装"""
        try:
            self.config = config
            model_path = config.get('model_path')
            
            # YOLOv8モデル読み込み
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            
            self.initialized = True
            return True
            
        except Exception as e:
            logging.error(f"Detector initialization failed: {e}")
            return False
    
    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """検出実行実装"""
        if not self.initialized:
            raise DetectionError("Detector not initialized")
        
        try:
            # YOLO推論実行
            results = self.model(image, 
                               conf=self.config.get('confidence_threshold', 0.5),
                               iou=self.config.get('nms_threshold', 0.4))
            
            # 結果変換
            detection_results = []
            for result in results:
                for box in result.boxes:
                    detection_result = DetectionResult(
                        x_center=float(box.xywh[0][0]),
                        y_center=float(box.xywh[0][1]),
                        width=float(box.xywh[0][2]),
                        height=float(box.xywh[0][3]),
                        confidence=float(box.conf[0]),
                        class_id=int(box.cls[0]),
                        timestamp=datetime.now().isoformat()
                    )
                    detection_results.append(detection_result)
            
            return detection_results
            
        except Exception as e:
            raise DetectionError(f"Detection failed: {e}")
```

#### 4.1.2 活動量算出API
```python
class ActivityCalculatorInterface(ABC):
    """活動量算出器インターフェース"""
    
    @abstractmethod
    def calculate_daily_activity(self, 
                               detection_data: pd.DataFrame
                              ) -> DailyActivitySummary:
        """日次活動量算出
        
        Args:
            detection_data: 検出データ
            
        Returns:
            日次活動統計
        """
        pass
    
    @abstractmethod
    def calculate_movement_distance(self, 
                                  detection_data: pd.DataFrame
                                 ) -> List[float]:
        """移動距離算出
        
        Args:
            detection_data: 時系列検出データ
            
        Returns:
            時間別移動距離リスト
        """
        pass
    
    @abstractmethod
    def generate_visualization(self, 
                             summary: DailyActivitySummary,
                             output_path: str
                            ) -> List[str]:
        """可視化生成
        
        Args:
            summary: 活動統計データ
            output_path: 出力ディレクトリ
            
        Returns:
            生成ファイルパスリスト
        """
        pass

# 実装例
class StandardActivityCalculator(ActivityCalculatorInterface):
    """標準活動量算出器実装"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.movement_threshold = config.get('movement_threshold_pixels', 5.0)
        self.outlier_threshold = config.get('outlier_threshold_sigma', 3.0)
    
    def calculate_daily_activity(self, 
                               detection_data: pd.DataFrame
                              ) -> DailyActivitySummary:
        """日次活動量算出実装"""
        
        # データ前処理
        detected_data = detection_data[detection_data['insect_detected'] == True].copy()
        
        if detected_data.empty:
            return self._create_empty_summary(detection_data['detection_date'].iloc[0])
        
        # 基本統計算出
        total_detections = len(detected_data)
        first_detection = detected_data['detection_time'].min()
        last_detection = detected_data['detection_time'].max()
        
        # 移動距離算出
        movement_distances = self.calculate_movement_distance(detected_data)
        total_movement = sum(movement_distances)
        
        # 時間分析
        detected_data['hour'] = pd.to_datetime(detected_data['timestamp']).dt.hour
        hourly_counts = detected_data.groupby('hour').size()
        most_active_hour = hourly_counts.idxmax() if not hourly_counts.empty else 0
        
        # 活動継続時間算出
        time_diff = pd.to_datetime(last_detection) - pd.to_datetime(first_detection)
        activity_duration = time_diff.total_seconds() / 60  # 分
        
        # 活動範囲算出
        activity_area = self._calculate_activity_area(detected_data)
        center_x = detected_data['x_center'].mean()
        center_y = detected_data['y_center'].mean()
        
        # データ品質指標算出
        expected_records = 24 * 60  # 1日分の想定レコード数（1分間隔想定）
        completeness_ratio = len(detection_data) / expected_records
        reliability_score = detected_data['confidence'].mean()
        
        return DailyActivitySummary(
            summary_date=detection_data['detection_date'].iloc[0],
            total_detections=total_detections,
            unique_detection_periods=len(self._identify_detection_periods(detected_data)),
            first_detection_time=first_detection,
            last_detection_time=last_detection,
            total_movement_distance=total_movement,
            average_movement_per_detection=total_movement / total_detections if total_detections > 0 else 0,
            max_movement_distance=max(movement_distances) if movement_distances else 0,
            most_active_hour=most_active_hour,
            activity_duration_minutes=activity_duration,
            inactive_periods_count=self._count_inactive_periods(detected_data),
            activity_area_pixels=activity_area,
            center_of_activity_x=center_x,
            center_of_activity_y=center_y,
            data_completeness_ratio=completeness_ratio,
            detection_reliability_score=reliability_score,
            analysis_timestamp=datetime.now(),
            analysis_version="v1.0.0"
        )
```

#### 4.1.3 ハードウェア制御API
```python
class HardwareControllerInterface(ABC):
    """ハードウェア制御インターフェース"""
    
    @abstractmethod
    def initialize_hardware(self) -> bool:
        """ハードウェア初期化
        
        Returns:
            初期化成功可否
        """
        pass
    
    @abstractmethod
    def capture_image(self, 
                     settings: Optional[Dict[str, Any]] = None
                    ) -> Optional[np.ndarray]:
        """画像撮影
        
        Args:
            settings: 撮影設定（解像度、露出等）
            
        Returns:
            撮影画像 (BGR形式) またはNone
        """
        pass
    
    @abstractmethod
    def control_led(self, brightness: float) -> bool:
        """LED制御
        
        Args:
            brightness: 明度 (0.0-1.0)
            
        Returns:
            制御成功可否
        """
        pass
    
    @abstractmethod
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態取得
        
        Returns:
            システム状態情報
        """
        pass
    
    @abstractmethod
    def cleanup_resources(self) -> None:
        """リソース解放"""
        pass

# RPi専用実装
class RaspberryPiController(HardwareControllerInterface):
    """Raspberry Pi専用制御実装"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.camera = None
        self.gpio_initialized = False
        self.led_pwm = None
        
    def initialize_hardware(self) -> bool:
        """ハードウェア初期化実装"""
        success = True
        
        # カメラ初期化
        try:
            from picamera2 import Picamera2
            self.camera = Picamera2()
            
            # カメラ設定
            config = self.camera.create_still_configuration(
                main={"size": tuple(self.config['camera']['resolution'])}
            )
            self.camera.configure(config)
            self.camera.start()
            
            logging.info("Camera initialized successfully")
            
        except Exception as e:
            logging.error(f"Camera initialization failed: {e}")
            success = False
        
        # GPIO初期化
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            
            led_pin = self.config['ir_led']['gpio_pin']
            GPIO.setup(led_pin, GPIO.OUT)
            
            # PWM設定
            pwm_freq = self.config['ir_led']['pwm_frequency']
            self.led_pwm = GPIO.PWM(led_pin, pwm_freq)
            self.led_pwm.start(0)  # 0%で開始
            
            self.gpio_initialized = True
            logging.info(f"GPIO initialized successfully (LED pin: {led_pin})")
            
        except Exception as e:
            logging.error(f"GPIO initialization failed: {e}")
            success = False
        
        return success
    
    def capture_image(self, 
                     settings: Optional[Dict[str, Any]] = None
                    ) -> Optional[np.ndarray]:
        """画像撮影実装"""
        if not self.camera:
            logging.error("Camera not initialized")
            return None
        
        try:
            # 設定適用（露出調整等）
            if settings:
                self._apply_camera_settings(settings)
            
            # 撮影実行
            image_array = self.camera.capture_array()
            
            # BGR形式に変換（OpenCV互換）
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # RGB → BGR変換
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                return image_bgr
            else:
                logging.error(f"Unexpected image format: {image_array.shape}")
                return None
                
        except Exception as e:
            logging.error(f"Image capture failed: {e}")
            return None
    
    def control_led(self, brightness: float) -> bool:
        """LED制御実装"""
        if not self.gpio_initialized or not self.led_pwm:
            logging.error("GPIO not initialized")
            return False
        
        try:
            # 明度値クランプ
            brightness = max(0.0, min(1.0, brightness))
            duty_cycle = brightness * 100  # 0-100%
            
            self.led_pwm.ChangeDutyCycle(duty_cycle)
            
            logging.debug(f"LED brightness set to {brightness:.1%}")
            return True
            
        except Exception as e:
            logging.error(f"LED control failed: {e}")
            return False
```

### 4.2 イベント駆動インターフェース

#### 4.2.1 イベントシステム設計
```python
from enum import Enum
from typing import Any, Callable, Dict, List
import asyncio

class EventType(Enum):
    """イベントタイプ定義"""
    DETECTION_STARTED = "detection_started"
    DETECTION_COMPLETED = "detection_completed"
    INSECT_DETECTED = "insect_detected"
    ANALYSIS_COMPLETED = "analysis_completed"
    SYSTEM_ERROR = "system_error"
    HARDWARE_ERROR = "hardware_error"
    CONFIG_CHANGED = "config_changed"

@dataclass
class Event:
    """イベントデータクラス"""
    event_type: EventType
    timestamp: datetime
    source: str  # イベント発生源
    data: Dict[str, Any]  # イベントデータ
    correlation_id: Optional[str] = None  # 関連ID

class EventBus:
    """イベントバスクラス"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_queue = asyncio.Queue()
        self._processing = False
    
    def subscribe(self, event_type: EventType, 
                 callback: Callable[[Event], None]) -> None:
        """イベント購読登録
        
        Args:
            event_type: 購読するイベントタイプ
            callback: コールバック関数
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        logging.debug(f"Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, 
                   callback: Callable[[Event], None]) -> None:
        """イベント購読解除
        
        Args:
            event_type: 解除するイベントタイプ  
            callback: コールバック関数
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                logging.debug(f"Unsubscribed from {event_type.value}")
            except ValueError:
                pass
    
    async def publish(self, event: Event) -> None:
        """イベント発行
        
        Args:
            event: 発行するイベント
        """
        await self._event_queue.put(event)
        
        if not self._processing:
            self._processing = True
            asyncio.create_task(self._process_events())
    
    async def _process_events(self) -> None:
        """イベント処理ループ"""
        while not self._event_queue.empty():
            try:
                event = await self._event_queue.get()
                await self._dispatch_event(event)
                
            except Exception as e:
                logging.error(f"Event processing error: {e}")
        
        self._processing = False
    
    async def _dispatch_event(self, event: Event) -> None:
        """イベント配信"""
        if event.event_type in self._subscribers:
            callbacks = self._subscribers[event.event_type]
            
            # 並行実行
            tasks = []
            for callback in callbacks:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(event))
                else:
                    # 同期関数を非同期実行
                    task = asyncio.get_event_loop().run_in_executor(
                        None, callback, event
                    )
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

# 使用例
class DetectionEventHandler:
    """検出イベントハンドラー"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.setup_subscriptions()
    
    def setup_subscriptions(self) -> None:
        """イベント購読設定"""
        self.event_bus.subscribe(EventType.INSECT_DETECTED, self.on_insect_detected)
        self.event_bus.subscribe(EventType.SYSTEM_ERROR, self.on_system_error)
    
    def on_insect_detected(self, event: Event) -> None:
        """昆虫検出イベントハンドラー"""
        detection_data = event.data
        logging.info(f"Insect detected: {detection_data['confidence']:.2f}")
        
        # 統計更新
        self.update_detection_statistics(detection_data)
        
        # 通知送信（将来機能）
        # self.send_notification(detection_data)
    
    def on_system_error(self, event: Event) -> None:
        """システムエラーイベントハンドラー"""
        error_data = event.data
        logging.error(f"System error: {error_data['error_message']}")
        
        # エラー統計更新
        self.update_error_statistics(error_data)
        
        # 復旧試行
        self.attempt_recovery(error_data)
```

---

## 5. 外部システムインターフェース設計

### 5.1 Hugging Face Hub連携

#### 5.1.1 モデルダウンロードAPI
```python
from huggingface_hub import hf_hub_download, HfApi
from typing import Optional, Dict, Any

class HuggingFaceConnector:
    """Hugging Face Hub連携クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api = HfApi()
        self.model_repo = config.get('model_repo', 'Murasan/beetle-detection-yolov8')
        self.local_cache_dir = config.get('cache_dir', './cache/models')
    
    def download_model(self, 
                      model_filename: str = 'best.pt',
                      force_download: bool = False
                     ) -> Optional[str]:
        """モデルファイルダウンロード
        
        Args:
            model_filename: ダウンロードするファイル名
            force_download: 強制再ダウンロード
            
        Returns:
            ダウンロードしたファイルの本Pathーまたは)ne
        """
        try:
            logging.info(f"Downloading model: {self.model_repo}/{model_filename}")
            
            model_path = hf_hub_download(
                repo_id=self.model_repo,
                filename=model_filename,
                local_dir=self.local_cache_dir,
                force_download=force_download,
                resume_download=True
            )
            
            logging.info(f"Model downloaded successfully: {model_path}")
            return model_path
            
        except Exception as e:
            logging.error(f"Model download failed: {e}")
            return None
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """モデル情報取得
        
        Returns:
            モデル情報辞書
        """
        try:
            repo_info = self.api.repo_info(self.model_repo)
            
            model_info = {
                'repo_id': self.model_repo,
                'last_modified': repo_info.last_modified,
                'sha': repo_info.sha,
                'files': [f.rfilename for f in repo_info.siblings],
                'model_card': self._get_model_card(),
                'download_count': getattr(repo_info, 'downloads', 0)
            }
            
            return model_info
            
        except Exception as e:
            logging.error(f"Failed to get model info: {e}")
            return None
    
    def _get_model_card(self) -> Optional[str]:
        """モデルカード取得"""
        try:
            return self.api.model_info(self.model_repo).cardData
        except:
            return None
    
    def check_for_updates(self, current_model_path: str) -> bool:
        """モデル更新確認
        
        Args:
            current_model_path: 現在のモデルファイルパス
            
        Returns:
            更新が利用可能かどうか
        """
        try:
            # ローカルファイルの最終更新時刻
            if not os.path.exists(current_model_path):
                return True  # ファイルが存在しない場合は更新必要
            
            local_mtime = datetime.fromtimestamp(
                os.path.getmtime(current_model_path)
            )
            
            # リモートの最終更新時刻
            repo_info = self.api.repo_info(self.model_repo)
            remote_mtime = repo_info.last_modified
            
            return remote_mtime > local_mtime
            
        except Exception as e:
            logging.error(f"Update check failed: {e}")
            return False

# 使用例
class ModelManager:
    """モデル管理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.hf_connector = HuggingFaceConnector(config['huggingface'])
        self.current_model_path = None
        self.model_info = None
    
    def ensure_model_available(self) -> Optional[str]:
        """モデル利用可能性確保
        
        Returns:
            モデルファイルパス
        """
        # 既存モデルの更新確認
        if self.current_model_path and self.hf_connector.check_for_updates(self.current_model_path):
            logging.info("Model update available, downloading...")
            self.current_model_path = self.hf_connector.download_model(force_download=True)
        
        # モデルが存在しない場合はダウンロード
        elif not self.current_model_path or not os.path.exists(self.current_model_path):
            logging.info("Model not found, downloading...")
            self.current_model_path = self.hf_connector.download_model()
        
        # モデル情報更新
        if self.current_model_path:
            self.model_info = self.hf_connector.get_model_info()
        
        return self.current_model_path
```

### 5.2 システム監視インターフェース

#### 5.2.1 メトリクス出力API
```python
import psutil
from typing import Dict, Any, Optional
import json
from datetime import datetime

class SystemMetricsCollector:
    """システムメトリクス収集クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('monitoring_enabled', True)
        self.collection_interval = config.get('collection_interval_seconds', 60)
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """システムメトリクス収集
        
        Returns:
            システムメトリクス辞書
        """
        if not self.enabled:
            return {}
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # メモリ使用状況
            memory = psutil.virtual_memory()
            
            # ディスク使用状況
            disk = psutil.disk_usage('/')
            
            # ネットワーク統計
            network = psutil.net_io_counters()
            
            # システム稼働時間
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            # 温度情報（Raspberry Pi）
            temperature = self._get_cpu_temperature()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'uptime_seconds': uptime_seconds,
                    'boot_time': datetime.fromtimestamp(boot_time).isoformat()
                },
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'temperature_celsius': temperature
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 1)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
            
        except Exception as e:
            logging.error(f"Failed to collect system metrics: {e}")
            return {'error': str(e)}
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """CPU温度取得（Raspberry Pi専用）"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_str = f.read().strip()
                temp_celsius = int(temp_str) / 1000.0
                return round(temp_celsius, 1)
        except:
            return None
    
    def collect_application_metrics(self, 
                                  detection_stats: Dict[str, Any],
                                  processing_stats: Dict[str, Any]
                                 ) -> Dict[str, Any]:
        """アプリケーションメトリクス収集
        
        Args:
            detection_stats: 検出統計情報
            processing_stats: 処理統計情報
            
        Returns:
            アプリケーションメトリクス辞書
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'detection': {
                'total_detections_today': detection_stats.get('total_detections', 0),
                'insects_found_today': detection_stats.get('insects_found', 0),
                'detection_rate_percent': detection_stats.get('detection_rate', 0.0),
                'last_detection_time': detection_stats.get('last_detection_time'),
                'average_confidence': detection_stats.get('average_confidence', 0.0)
            },
            'processing': {
                'average_processing_time_ms': processing_stats.get('avg_processing_time', 0.0),
                'max_processing_time_ms': processing_stats.get('max_processing_time', 0.0),
                'processing_queue_size': processing_stats.get('queue_size', 0),
                'error_count_today': processing_stats.get('error_count', 0),
                'success_rate_percent': processing_stats.get('success_rate', 100.0)
            },
            'model': {
                'model_version': processing_stats.get('model_version', 'unknown'),
                'model_load_time_ms': processing_stats.get('model_load_time', 0.0),
                'inference_count_today': processing_stats.get('inference_count', 0)
            }
        }

class PrometheusExporter:
    """Prometheus形式メトリクス出力クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('prometheus_enabled', False)
        self.port = config.get('prometheus_port', 8000)
        
    def export_metrics(self, 
                      system_metrics: Dict[str, Any],
                      app_metrics: Dict[str, Any]) -> str:
        """Prometheus形式メトリクス出力
        
        Args:
            system_metrics: システムメトリクス
            app_metrics: アプリケーションメトリクス
            
        Returns:
            Prometheus形式メトリクス文字列
        """
        if not self.enabled:
            return ""
        
        prometheus_metrics = []
        
        # システムメトリクス
        if 'cpu' in system_metrics:
            prometheus_metrics.append(
                f"# HELP cpu_usage_percent CPU usage percentage\n"
                f"# TYPE cpu_usage_percent gauge\n"
                f"cpu_usage_percent {system_metrics['cpu']['usage_percent']}"
            )
            
            if system_metrics['cpu']['temperature_celsius']:
                prometheus_metrics.append(
                    f"# HELP cpu_temperature_celsius CPU temperature in Celsius\n"
                    f"# TYPE cpu_temperature_celsius gauge\n"
                    f"cpu_temperature_celsius {system_metrics['cpu']['temperature_celsius']}"
                )
        
        if 'memory' in system_metrics:
            prometheus_metrics.append(
                f"# HELP memory_usage_percent Memory usage percentage\n"
                f"# TYPE memory_usage_percent gauge\n"
                f"memory_usage_percent {system_metrics['memory']['usage_percent']}"
            )
        
        # アプリケーションメトリクス
        if 'detection' in app_metrics:
            detection = app_metrics['detection']
            
            prometheus_metrics.append(
                f"# HELP detections_total Total number of detections today\n"
                f"# TYPE detections_total counter\n"
                f"detections_total {detection['total_detections_today']}"
            )
            
            prometheus_metrics.append(
                f"# HELP insects_found_total Total number of insects found today\n"
                f"# TYPE insects_found_total counter\n"
                f"insects_found_total {detection['insects_found_today']}"
            )
            
            prometheus_metrics.append(
                f"# HELP detection_rate_percent Detection success rate percentage\n"
                f"# TYPE detection_rate_percent gauge\n"
                f"detection_rate_percent {detection['detection_rate_percent']}"
            )
        
        if 'processing' in app_metrics:
            processing = app_metrics['processing']
            
            prometheus_metrics.append(
                f"# HELP processing_time_ms_avg Average processing time in milliseconds\n"
                f"# TYPE processing_time_ms_avg gauge\n"
                f"processing_time_ms_avg {processing['average_processing_time_ms']}"
            )
        
        return '\n\n'.join(prometheus_metrics)

# HTTPサーバー（メトリクス公開用）
from http.server import HTTPServer, BaseHTTPRequestHandler

class MetricsHandler(BaseHTTPRequestHandler):
    """メトリクス公開HTTPハンドラー"""
    
    def __init__(self, metrics_collector, prometheus_exporter):
        self.metrics_collector = metrics_collector
        self.prometheus_exporter = prometheus_exporter
    
    def do_GET(self):
        """GET リクエスト処理"""
        if self.path == '/metrics':
            # メトリクス収集
            system_metrics = self.metrics_collector.collect_system_metrics()
            # アプリメトリクスは別途注入が必要
            app_metrics = {}  # 実際は外部から注入
            
            # Prometheus形式出力
            metrics_text = self.prometheus_exporter.export_metrics(
                system_metrics, app_metrics
            )
            
            # HTTP レスポンス
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(metrics_text.encode('utf-8'))
            
        elif self.path == '/health':
            # ヘルスチェック
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            health_status = {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
            self.wfile.write(json.dumps(health_status).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
```

---

## 6. ハードウェアインターフェース設計

### 6.1 カメラインターフェース仕様

#### 6.1.1 PiCamera2 API仕様
```python
from picamera2 import Picamera2, Preview
from libcamera import controls
import numpy as np
from typing import Dict, Any, Optional, Tuple

class CameraInterface:
    """カメラインターフェース抽象クラス"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """カメラ初期化"""
        pass
    
    @abstractmethod
    def capture_image(self) -> Optional[np.ndarray]:
        """画像撮影"""
        pass
    
    @abstractmethod
    def set_exposure(self, exposure_time_us: int) -> bool:
        """露出時間設定"""
        pass
    
    @abstractmethod
    def set_gain(self, gain: float) -> bool:
        """ゲイン設定"""
        pass
    
    @abstractmethod
    def get_camera_info(self) -> Dict[str, Any]:
        """カメラ情報取得"""
        pass

class PiCamera2Controller(CameraInterface):
    """PiCamera2制御実装"""
    
    def __init__(self):
        self.camera = None
        self.config = None
        self.initialized = False
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """カメラ初期化実装"""
        try:
            self.config = config
            self.camera = Picamera2()
            
            # カメラ設定作成
            camera_config = self._create_camera_config(config)
            self.camera.configure(camera_config)
            
            # 制御設定
            self._apply_controls(config)
            
            # カメラ開始
            self.camera.start()
            
            # 安定化待機
            time.sleep(2)
            
            self.initialized = True
            logging.info("PiCamera2 initialized successfully")
            
            return True
            
        except Exception as e:
            logging.error(f"PiCamera2 initialization failed: {e}")
            return False
    
    def _create_camera_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """カメラ設定作成"""
        resolution = tuple(config.get('resolution', [1920, 1080]))
        
        # 静止画設定
        still_config = self.camera.create_still_configuration(
            main={
                "size": resolution,
                "format": "BGR888"  # OpenCV互換形式
            },
            lores={
                "size": (640, 480),  # 低解像度プレビュー用
                "format": "YUV420"
            },
            display="lores"
        )
        
        return still_config
    
    def _apply_controls(self, config: Dict[str, Any]) -> None:
        """カメラ制御設定適用"""
        control_settings = {}
        
        # 自動露出設定
        if config.get('auto_exposure', True):
            control_settings[controls.AeEnable] = True
        else:
            control_settings[controls.AeEnable] = False
            # マニュアル露出時間設定
            exposure_time = config.get('exposure_time_us', 10000)
            control_settings[controls.ExposureTime] = exposure_time
        
        # ゲイン設定
        if 'gain' in config:
            control_settings[controls.AnalogueGain] = config['gain']
        
        # ホワイトバランス設定
        wb_mode = config.get('white_balance', 'auto')
        if wb_mode == 'auto':
            control_settings[controls.AwbEnable] = True
        else:
            control_settings[controls.AwbEnable] = False
            # マニュアルWB設定
            if 'white_balance_gains' in config:
                control_settings[controls.ColourGains] = config['white_balance_gains']
        
        # 露出補正
        if 'exposure_compensation' in config:
            control_settings[controls.ExposureValue] = config['exposure_compensation']
        
        # フォーカス設定（将来のオートフォーカス対応）
        if config.get('auto_focus', False):
            control_settings[controls.AfMode] = controls.AfModeEnum.Continuous
        
        # 設定適用
        if control_settings:
            self.camera.set_controls(control_settings)
            logging.debug(f"Camera controls applied: {control_settings}")
    
    def capture_image(self) -> Optional[np.ndarray]:
        """画像撮影実装"""
        if not self.initialized:
            logging.error("Camera not initialized")
            return None
        
        try:
            # 静止画撮影
            image_array = self.camera.capture_array("main")
            
            # データ型・形状確認
            if image_array is None:
                logging.error("Captured image is None")
                return None
            
            if len(image_array.shape) != 3 or image_array.shape[2] != 3:
                logging.error(f"Unexpected image shape: {image_array.shape}")
                return None
            
            # uint8型に変換
            if image_array.dtype != np.uint8:
                image_array = image_array.astype(np.uint8)
            
            logging.debug(f"Image captured: {image_array.shape}, dtype: {image_array.dtype}")
            return image_array
            
        except Exception as e:
            logging.error(f"Image capture failed: {e}")
            return None
    
    def set_exposure(self, exposure_time_us: int) -> bool:
        """露出時間設定実装"""
        if not self.initialized:
            return False
        
        try:
            # 自動露出無効化
            controls_dict = {
                controls.AeEnable: False,
                controls.ExposureTime: exposure_time_us
            }
            
            self.camera.set_controls(controls_dict)
            logging.debug(f"Exposure time set to {exposure_time_us}µs")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to set exposure: {e}")
            return False
    
    def set_gain(self, gain: float) -> bool:
        """ゲイン設定実装"""
        if not self.initialized:
            return False
        
        try:
            self.camera.set_controls({controls.AnalogueGain: gain})
            logging.debug(f"Gain set to {gain}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to set gain: {e}")
            return False
    
    def get_camera_info(self) -> Dict[str, Any]:
        """カメラ情報取得実装"""
        if not self.initialized:
            return {}
        
        try:
            # カメラプロパティ取得
            camera_properties = self.camera.camera_properties
            
            # 現在の制御値取得
            current_controls = self.camera.capture_metadata()
            
            info = {
                'model': camera_properties.get('Model', 'Unknown'),
                'resolution': self.config.get('resolution', [1920, 1080]),
                'pixel_array_size': camera_properties.get('PixelArraySize'),
                'unit_cell_size': camera_properties.get('UnitCellSize'),
                'color_filter_arrangement': camera_properties.get('ColorFilterArrangement'),
                'current_controls': {
                    'exposure_time': current_controls.get('ExposureTime'),
                    'analogue_gain': current_controls.get('AnalogueGain'),
                    'colour_gains': current_controls.get('ColourGains'),
                    'lux': current_controls.get('Lux')
                }
            }
            
            return info
            
        except Exception as e:
            logging.error(f"Failed to get camera info: {e}")
            return {'error': str(e)}
    
    def cleanup(self) -> None:
        """リソース解放"""
        if self.camera:
            try:
                self.camera.stop()
                self.camera.close()
                logging.info("Camera resources cleaned up")
            except Exception as e:
                logging.error(f"Camera cleanup error: {e}")
            finally:
                self.camera = None
                self.initialized = False
```

### 6.2 GPIO制御インターフェース

#### 6.2.1 LED制御仕様
```python
import RPi.GPIO as GPIO
import time
import threading
from typing import Dict, Any, Optional

class GPIOInterface:
    """GPIO制御インターフェース抽象クラス"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """GPIO初期化"""
        pass
    
    @abstractmethod
    def set_led_brightness(self, brightness: float) -> bool:
        """LED明度設定"""
        pass
    
    @abstractmethod
    def led_fade(self, target_brightness: float, duration_ms: int) -> bool:
        """LEDフェード制御"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """リソース解放"""
        pass

class RPiGPIOController(GPIOInterface):
    """Raspberry Pi GPIO制御実装"""
    
    def __init__(self):
        self.initialized = False
        self.led_pin = None
        self.led_pwm = None
        self.current_brightness = 0.0
        self.fade_thread = None
        self.fade_stop_event = threading.Event()
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """GPIO初期化実装"""
        try:
            # GPIO設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # LED設定
            self.led_pin = config.get('gpio_pin', 18)
            pwm_frequency = config.get('pwm_frequency', 1000)
            
            GPIO.setup(self.led_pin, GPIO.OUT)
            self.led_pwm = GPIO.PWM(self.led_pin, pwm_frequency)
            self.led_pwm.start(0)  # 0%で開始
            
            self.initialized = True
            logging.info(f"GPIO initialized - LED pin: {self.led_pin}, PWM freq: {pwm_frequency}Hz")
            
            return True
            
        except Exception as e:
            logging.error(f"GPIO initialization failed: {e}")
            return False
    
    def set_led_brightness(self, brightness: float) -> bool:
        """LED明度設定実装"""
        if not self.initialized:
            logging.error("GPIO not initialized")
            return False
        
        try:
            # 明度値検証・クランプ
            brightness = max(0.0, min(1.0, brightness))
            duty_cycle = brightness * 100  # 0-100%
            
            self.led_pwm.ChangeDutyCycle(duty_cycle)
            self.current_brightness = brightness
            
            logging.debug(f"LED brightness set to {brightness:.1%} (duty: {duty_cycle:.1f}%)")
            return True
            
        except Exception as e:
            logging.error(f"LED brightness control failed: {e}")
            return False
    
    def led_fade(self, target_brightness: float, duration_ms: int) -> bool:
        """LEDフェード制御実装"""
        if not self.initialized:
            return False
        
        # 既存のフェード処理停止
        if self.fade_thread and self.fade_thread.is_alive():
            self.fade_stop_event.set()
            self.fade_thread.join(timeout=1.0)
        
        # 新しいフェード処理開始
        self.fade_stop_event.clear()
        self.fade_thread = threading.Thread(
            target=self._fade_worker,
            args=(target_brightness, duration_ms)
        )
        self.fade_thread.daemon = True
        self.fade_thread.start()
        
        return True
    
    def _fade_worker(self, target_brightness: float, duration_ms: int) -> None:
        """フェード処理ワーカー"""
        try:
            start_brightness = self.current_brightness
            steps = max(10, duration_ms // 10)  # 10ms間隔、最低10ステップ
            step_duration = duration_ms / steps / 1000.0  # 秒
            brightness_step = (target_brightness - start_brightness) / steps
            
            for step in range(steps + 1):
                if self.fade_stop_event.is_set():
                    break
                
                current_brightness = start_brightness + (brightness_step * step)
                self.set_led_brightness(current_brightness)
                
                if step < steps:  # 最後のステップでは待機しない
                    time.sleep(step_duration)
            
            logging.debug(f"LED fade completed: {start_brightness:.2f} → {target_brightness:.2f}")
            
        except Exception as e:
            logging.error(f"LED fade error: {e}")
    
    def get_gpio_status(self) -> Dict[str, Any]:
        """GPIO状態取得"""
        return {
            'initialized': self.initialized,
            'led_pin': self.led_pin,
            'current_brightness': self.current_brightness,
            'fade_active': self.fade_thread.is_alive() if self.fade_thread else False
        }
    
    def cleanup(self) -> None:
        """リソース解放実装"""
        try:
            # フェード処理停止
            if self.fade_thread and self.fade_thread.is_alive():
                self.fade_stop_event.set()
                self.fade_thread.join(timeout=2.0)
            
            # LED消灯
            if self.led_pwm:
                self.led_pwm.ChangeDutyCycle(0)
                self.led_pwm.stop()
            
            # GPIO クリーンアップ
            GPIO.cleanup()
            
            self.initialized = False
            logging.info("GPIO resources cleaned up")
            
        except Exception as e:
            logging.error(f"GPIO cleanup error: {e}")

# 使用例とテストコード
class HardwareTest:
    """ハードウェアテストクラス"""
    
    def __init__(self, camera_config: Dict[str, Any], gpio_config: Dict[str, Any]):
        self.camera = PiCamera2Controller()
        self.gpio = RPiGPIOController()
        self.camera_config = camera_config
        self.gpio_config = gpio_config
    
    def run_hardware_test(self) -> Dict[str, Any]:
        """ハードウェステスト実行"""
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'camera_test': {},
            'gpio_test': {},
            'integration_test': {}
        }
        
        # カメラテスト
        test_results['camera_test'] = self._test_camera()
        
        # GPIOテスト
        test_results['gpio_test'] = self._test_gpio()
        
        # 統合テスト
        if test_results['camera_test']['success'] and test_results['gpio_test']['success']:
            test_results['integration_test'] = self._test_integration()
        
        return test_results
    
    def _test_camera(self) -> Dict[str, Any]:
        """カメラテスト"""
        result = {'success': False, 'details': {}}
        
        try:
            # 初期化テスト
            if not self.camera.initialize(self.camera_config):
                result['details']['initialization'] = 'Failed'
                return result
            result['details']['initialization'] = 'Success'
            
            # 撮影テスト
            image = self.camera.capture_image()
            if image is None:
                result['details']['capture'] = 'Failed'
                return result
            
            result['details']['capture'] = f'Success - {image.shape}'
            
            # 画質テスト
            brightness = np.mean(image)
            contrast = np.std(image)
            result['details']['image_quality'] = {
                'brightness': brightness,
                'contrast': contrast,
                'quality_ok': 10 < brightness < 245 and contrast > 5
            }
            
            result['success'] = True
            
        except Exception as e:
            result['details']['error'] = str(e)
        
        finally:
            self.camera.cleanup()
        
        return result
    
    def _test_gpio(self) -> Dict[str, Any]:
        """GPIOテスト"""
        result = {'success': False, 'details': {}}
        
        try:
            # 初期化テスト
            if not self.gpio.initialize(self.gpio_config):
                result['details']['initialization'] = 'Failed'
                return result
            result['details']['initialization'] = 'Success'
            
            # 明度制御テスト
            test_brightnesses = [0.0, 0.5, 1.0, 0.0]
            for brightness in test_brightnesses:
                if not self.gpio.set_led_brightness(brightness):
                    result['details']['brightness_control'] = f'Failed at {brightness}'
                    return result
                time.sleep(0.5)
            result['details']['brightness_control'] = 'Success'
            
            # フェードテスト
            if not self.gpio.led_fade(0.8, 1000):
                result['details']['fade_control'] = 'Failed'
                return result
            time.sleep(1.5)  # フェード完了待機
            result['details']['fade_control'] = 'Success'
            
            result['success'] = True
            
        except Exception as e:
            result['details']['error'] = str(e)
        
        finally:
            self.gpio.cleanup()
        
        return result
    
    def _test_integration(self) -> Dict[str, Any]:
        """統合テスト"""
        result = {'success': False, 'details': {}}
        
        try:
            # 両デバイス初期化
            self.camera.initialize(self.camera_config)
            self.gpio.initialize(self.gpio_config)
            
            # 実際の検出シーケンステスト
            # 1. LED点灯
            self.gpio.led_fade(0.8, 200)
            time.sleep(0.5)
            
            # 2. 画像撮影
            image = self.camera.capture_image()
            
            # 3. LED消灯
            self.gpio.led_fade(0.0, 200)
            
            if image is not None:
                result['details']['sequence_test'] = 'Success'
                result['details']['image_with_led'] = {
                    'shape': image.shape,
                    'brightness': float(np.mean(image))
                }
                result['success'] = True
            else:
                result['details']['sequence_test'] = 'Failed - No image captured'
                
        except Exception as e:
            result['details']['error'] = str(e)
        
        finally:
            self.camera.cleanup()
            self.gpio.cleanup()
        
        return result
```

---

## 7. 運用・保守インターフェース設計

### 7.1 診断インターフェース

#### 7.1.1 システム診断API
```python
import subprocess
import socket
from datetime import datetime, timedelta
from typing import Dict, Any, List

class SystemDiagnostics:
    """システム診断クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.diagnostics_enabled = config.get('diagnostics_enabled', True)
        
    def run_full_diagnostics(self) -> Dict[str, Any]:
        """完全診断実行
        
        Returns:
            診断結果辞書
        """
        if not self.diagnostics_enabled:
            return {'status': 'disabled'}
        
        diagnosis_result = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'checks': {},
            'recommendations': [],
            'critical_issues': [],
            'warnings': []
        }
        
        # 各種診断実行
        diagnosis_result['checks']['system_health'] = self._check_system_health()
        diagnosis_result['checks']['hardware_status'] = self._check_hardware_status()
        diagnosis_result['checks']['software_status'] = self._check_software_status()
        diagnosis_result['checks']['data_integrity'] = self._check_data_integrity()
        diagnosis_result['checks']['performance'] = self._check_performance()
        diagnosis_result['checks']['security'] = self._check_security()
        
        # 総合評価
        diagnosis_result['overall_status'] = self._evaluate_overall_status(diagnosis_result['checks'])
        diagnosis_result['recommendations'] = self._generate_recommendations(diagnosis_result['checks'])
        
        return diagnosis_result
    
    def _check_system_health(self) -> Dict[str, Any]:
        """システム健全性チェック"""
        health_check = {
            'status': 'healthy',
            'issues': [],
            'metrics': {}
        }
        
        try:
            # CPU使用率チェック
            cpu_percent = psutil.cpu_percent(interval=1)
            health_check['metrics']['cpu_usage_percent'] = cpu_percent
            if cpu_percent > 90:
                health_check['issues'].append(f"High CPU usage: {cpu_percent}%")
                health_check['status'] = 'warning'
            
            # メモリ使用率チェック
            memory = psutil.virtual_memory()
            health_check['metrics']['memory_usage_percent'] = memory.percent
            if memory.percent > 85:
                health_check['issues'].append(f"High memory usage: {memory.percent}%")
                health_check['status'] = 'warning'
            
            # ディスク使用率チェック
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            health_check['metrics']['disk_usage_percent'] = round(disk_percent, 1)
            if disk_percent > 80:
                health_check['issues'].append(f"High disk usage: {disk_percent:.1f}%")
                if disk_percent > 90:
                    health_check['status'] = 'critical'
                else:
                    health_check['status'] = 'warning'
            
            # 温度チェック（Raspberry Pi）
            temp = self._get_cpu_temperature()
            if temp:
                health_check['metrics']['cpu_temperature_celsius'] = temp
                if temp > 70:
                    health_check['issues'].append(f"High CPU temperature: {temp}°C")
                    if temp > 80:
                        health_check['status'] = 'critical'
                    else:
                        health_check['status'] = 'warning'
            
            # プロセス状態チェック
            process_count = len(psutil.pids())
            health_check['metrics']['process_count'] = process_count
            if process_count > 500:
                health_check['issues'].append(f"High process count: {process_count}")
                health_check['status'] = 'warning'
            
        except Exception as e:
            health_check['status'] = 'error'
            health_check['issues'].append(f"Health check error: {str(e)}")
        
        return health_check
    
    def _check_hardware_status(self) -> Dict[str, Any]:
        """ハードウェア状態チェック"""
        hardware_check = {
            'status': 'healthy',
            'devices': {},
            'issues': []
        }
        
        try:
            # カメラデバイスチェック
            hardware_check['devices']['camera'] = self._check_camera_device()
            
            # GPIO状態チェック
            hardware_check['devices']['gpio'] = self._check_gpio_status()
            
            # ストレージデバイスチェック
            hardware_check['devices']['storage'] = self._check_storage_health()
            
            # USB デバイスチェック
            hardware_check['devices']['usb'] = self._check_usb_devices()
            
            # 全体評価
            device_statuses = [dev['status'] for dev in hardware_check['devices'].values()]
            if 'error' in device_statuses:
                hardware_check['status'] = 'error'
            elif 'warning' in device_statuses:
                hardware_check['status'] = 'warning'
                
        except Exception as e:
            hardware_check['status'] = 'error'
            hardware_check['issues'].append(f"Hardware check error: {str(e)}")
        
        return hardware_check
    
    def _check_camera_device(self) -> Dict[str, Any]:
        """カメラデバイスチェック"""
        camera_check = {
            'status': 'unknown',
            'detected': False,
            'details': {}
        }
        
        try:
            # /dev/video* デバイス確認
            import glob
            video_devices = glob.glob('/dev/video*')
            camera_check['details']['video_devices'] = video_devices
            
            if video_devices:
                camera_check['detected'] = True
                camera_check['status'] = 'healthy'
            else:
                camera_check['status'] = 'error'
                camera_check['details']['error'] = 'No video devices found'
            
            # libcamera デバイス確認
            try:
                result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    camera_check['details']['libcamera_output'] = result.stdout
                    if 'Available cameras' in result.stdout:
                        camera_check['detected'] = True
                        camera_check['status'] = 'healthy'
                else:
                    camera_check['details']['libcamera_error'] = result.stderr
                    
            except subprocess.TimeoutExpired:
                camera_check['details']['libcamera_error'] = 'Command timeout'
            except FileNotFoundError:
                camera_check['details']['libcamera_error'] = 'libcamera-hello not found'
                
        except Exception as e:
            camera_check['status'] = 'error'
            camera_check['details']['error'] = str(e)
        
        return camera_check
    
    def _check_data_integrity(self) -> Dict[str, Any]:
        """データ整合性チェック"""
        integrity_check = {
            'status': 'healthy',
            'checks': {},
            'issues': []
        }
        
        try:
            # 最新データファイルの整合性チェック
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # 昨日の検出ログチェック
            log_file = f"./data/raw/detection_logs/detection_{yesterday.strftime('%Y%m%d')}.csv"
            integrity_check['checks']['recent_log'] = self._validate_csv_file(log_file)
            
            # データディレクトリ構造チェック
            integrity_check['checks']['directory_structure'] = self._check_directory_structure()
            
            # ファイル権限チェック
            integrity_check['checks']['file_permissions'] = self._check_file_permissions()
            
            # バックアップ整合性チェック
            integrity_check['checks']['backup_integrity'] = self._check_backup_integrity()
            
            # 問題集約
            for check_name, check_result in integrity_check['checks'].items():
                if check_result.get('status') == 'error':
                    integrity_check['status'] = 'error'
                    integrity_check['issues'].extend(check_result.get('issues', []))
                elif check_result.get('status') == 'warning':
                    if integrity_check['status'] != 'error':
                        integrity_check['status'] = 'warning'
                    integrity_check['issues'].extend(check_result.get('issues', []))
                    
        except Exception as e:
            integrity_check['status'] = 'error'
            integrity_check['issues'].append(f"Data integrity check error: {str(e)}")
        
        return integrity_check
    
    def _generate_recommendations(self, checks: Dict[str, Any]) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []
        
        # システム健全性に基づく推奨事項
        if checks.get('system_health', {}).get('status') in ['warning', 'critical']:
            system_issues = checks['system_health'].get('issues', [])
            
            for issue in system_issues:
                if 'High CPU usage' in issue:
                    recommendations.append("CPU使用率が高いです。検出間隔を延ばすか、不要なプロセスを停止してください。")
                elif 'High memory usage' in issue:
                    recommendations.append("メモリ使用率が高いです。システムの再起動を検討してください。")
                elif 'High disk usage' in issue:
                    recommendations.append("ディスク使用率が高いです。古いデータファイルのクリーンアップを実行してください。")
                elif 'High CPU temperature' in issue:
                    recommendations.append("CPU温度が高いです。冷却を確認し、負荷を軽減してください。")
        
        # ハードウェア状態に基づく推奨事項
        if checks.get('hardware_status', {}).get('status') in ['warning', 'error']:
            hardware_devices = checks['hardware_status'].get('devices', {})
            
            if hardware_devices.get('camera', {}).get('status') == 'error':
                recommendations.append("カメラデバイスが検出されません。接続を確認してください。")
            
            if hardware_devices.get('storage', {}).get('status') == 'warning':
                recommendations.append("ストレージに問題があります。ディスクチェックを実行してください。")
        
        # データ整合性に基づく推奨事項
        if checks.get('data_integrity', {}).get('status') in ['warning', 'error']:
            recommendations.append("データ整合性に問題があります。バックアップからの復旧を検討してください。")
        
        # パフォーマンスに基づく推奨事項
        if checks.get('performance', {}).get('status') == 'warning':
            recommendations.append("システムパフォーマンスが低下しています。設定の最適化を検討してください。")
        
        # 一般的な推奨事項
        if not recommendations:
            recommendations.append("システムは正常に動作しています。定期的な保守を継続してください。")
        
        return recommendations

# 診断レポート生成
class DiagnosticsReporter:
    """診断レポート生成クラス"""
    
    def __init__(self):
        pass
    
    def generate_html_report(self, diagnosis_result: Dict[str, Any]) -> str:
        """HTML形式診断レポート生成"""
        
        html_template = """
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>システム診断レポート</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .status-healthy { color: green; font-weight: bold; }
                .status-warning { color: orange; font-weight: bold; }
                .status-error { color: red; font-weight: bold; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .recommendations { background-color: #e6f3ff; }
                .issues { background-color: #ffe6e6; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>昆虫自動観察システム 診断レポート</h1>
                <p>生成日時: {timestamp}</p>
                <p>総合状態: <span class="status-{overall_status}">{overall_status_text}</span></p>
            </div>
            
            {sections}
            
            <div class="section recommendations">
                <h2>推奨事項</h2>
                <ul>
                    {recommendations}
                </ul>
            </div>
        </body>
        </html>
        """
        
        # データ処理
        overall_status = diagnosis_result.get('overall_status', 'unknown')
        status_text_map = {
            'healthy': '正常',
            'warning': '警告', 
            'error': 'エラー',
            'critical': '重大'
        }
        
        # セクション生成
        sections = []
        for check_name, check_result in diagnosis_result.get('checks', {}).items():
            section_html = self._generate_check_section_html(check_name, check_result)
            sections.append(section_html)
        
        # 推奨事項リスト生成
        recommendations_html = '\n'.join([
            f"<li>{rec}</li>" for rec in diagnosis_result.get('recommendations', [])
        ])
        
        # テンプレート埋め込み
        html_content = html_template.format(
            timestamp=diagnosis_result.get('timestamp', ''),
            overall_status=overall_status,
            overall_status_text=status_text_map.get(overall_status, '不明'),
            sections='\n'.join(sections),
            recommendations=recommendations_html
        )
        
        return html_content
    
    def _generate_check_section_html(self, check_name: str, check_result: Dict[str, Any]) -> str:
        """チェック結果セクションHTML生成"""
        
        section_names = {
            'system_health': 'システム健全性',
            'hardware_status': 'ハードウェア状態',
            'software_status': 'ソフトウェア状態',
            'data_integrity': 'データ整合性',
            'performance': 'パフォーマンス',
            'security': 'セキュリティ'
        }
        
        section_name = section_names.get(check_name, check_name)
        status = check_result.get('status', 'unknown')
        
        section_html = f"""
        <div class="section">
            <h2>{section_name}</h2>
            <p>状態: <span class="status-{status}">{status}</span></p>
        """
        
        # メトリクス表示
        if 'metrics' in check_result:
            section_html += "<h3>メトリクス</h3><table>"
            section_html += "<tr><th>項目</th><th>値</th></tr>"
            for metric, value in check_result['metrics'].items():
                section_html += f"<tr><td>{metric}</td><td>{value}</td></tr>"
            section_html += "</table>"
        
        # 問題表示
        if check_result.get('issues'):
            section_html += "<h3>検出された問題</h3><ul>"
            for issue in check_result['issues']:
                section_html += f"<li>{issue}</li>"
            section_html += "</ul>"
        
        section_html += "</div>"
        
        return section_html
```

---

*文書バージョン: 1.0*  
*最終更新日: 2025-07-25*  
*承認者: 開発チーム*