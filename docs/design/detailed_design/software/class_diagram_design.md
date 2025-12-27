# クラス図設計書

**文書番号**: 12-003-CLASS-001  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: クラス図設計書  
**バージョン**: 1.0  
**作成日**: 2025-07-25  
**作成者**: 開発チーム  

---

## 1. 文書概要

### 1.1 目的
本文書は昆虫自動観察システムのクラス構造をPlantUML図で可視化し、クラス間の関係性、継承構造、依存関係を明確に定義する。

### 1.2 適用範囲
- システム全体のクラス構造
- モジュール別クラス図
- データモデルクラス図
- インターフェース・抽象クラス定義
- クラス間の関係性（継承・集約・依存）

### 1.3 関連文書
- ソフトウェア設計書（software_design.md）
- データ設計書（data_design.md）
- システムアーキテクチャ設計書（system_architecture_design.md）

---

## 2. システム全体クラス図

### 2.1 全体構成クラス図

```plantuml
@startuml SystemOverview
!define RECTANGLE class

skinparam class {
    BackgroundColor lightblue
    BorderColor black
    ArrowColor darkblue
}

package "Main System" {
    class InsectObserverSystem {
        -config: SystemConfig
        -detector: InsectDetector
        -calculator: ActivityCalculator
        -hardware_controller: HardwareController
        -logger: logging.Logger
        -running: bool
        +initialize_system(): bool
        +run_main_loop(): None
        +perform_detection_cycle(): Dict[str, Any]
        +perform_daily_analysis(): None
        +shutdown_system(): None
    }
}

package "Detection Module" {
    interface DetectorInterface {
        +initialize(config: Dict): bool
        +detect(image: np.ndarray): List[DetectionResult]
        +get_status(): Dict[str, Any]
        +cleanup(): None
    }
    
    class InsectDetector {
        -config: Dict[str, Any]
        -model: YOLO
        -camera: CameraController
        -hardware_controller: HardwareController
        -detection_count: int
        +initialize_model(model_path: str): bool
        +capture_image(): Optional[np.ndarray]
        +detect_insects(image: np.ndarray): List[DetectionResult]
        +process_detection_results(): Dict[str, Any]
        +save_detection_image(): str
    }
    
    class YOLODetector {
        -model: YOLO
        -config: Dict[str, Any]
        -initialized: bool
        +initialize(config: Dict): bool
        +detect(image: np.ndarray): List[DetectionResult]
        +get_status(): Dict[str, Any]
        +cleanup(): None
    }
}

package "Activity Analysis Module" {
    interface ActivityCalculatorInterface {
        +calculate_daily_activity(): DailyActivitySummary
        +calculate_movement_distance(): List[float]
        +generate_visualization(): List[str]
    }
    
    class ActivityCalculator {
        -config: Dict[str, Any]
        -data_processor: DataProcessor
        -visualizer: Visualizer
        +load_detection_data(date: str): pd.DataFrame
        +calculate_movement_distance(): List[float]
        +calculate_activity_metrics(): ActivityMetrics
        +generate_activity_chart(): str
        +generate_movement_heatmap(): str
    }
    
    class StandardActivityCalculator {
        -movement_threshold: float
        -outlier_threshold: float
        +calculate_daily_activity(): DailyActivitySummary
        +calculate_movement_distance(): List[float]
        +generate_visualization(): List[str]
    }
}

package "Hardware Control Module" {
    interface HardwareControllerInterface {
        +initialize_hardware(): bool
        +capture_image(): Optional[np.ndarray]
        +control_led(brightness: float): bool
        +get_system_status(): Dict[str, Any]
        +cleanup_resources(): None
    }
    
    class HardwareController {
        -config: Dict[str, Any]
        -camera: CameraController
        -gpio_controller: GPIOController
        +initialize_hardware(): bool
        +capture_image(): Optional[np.ndarray]
        +control_led(): bool
        +get_system_status(): Dict[str, Any]
        +cleanup_resources(): None
    }
    
    class RaspberryPiController {
        -camera: Picamera2
        -gpio_initialized: bool
        -led_pwm: GPIO.PWM
        +initialize_hardware(): bool
        +capture_image(): Optional[np.ndarray]
        +control_led(brightness: float): bool
        +get_system_status(): Dict[str, Any]
        +cleanup_resources(): None
    }
}

package "Configuration Module" {
    class ConfigManager {
        -config_path: str
        -config: SystemConfig
        +load_config(): SystemConfig
        +save_config(): None
        +validate_config(): List[str]
        +get_env_config(): Dict[str, Any]
    }
    
    class SystemConfig {
        +detection_interval_seconds: int
        +log_level: str
        +data_retention_days: int
        +camera_resolution: Tuple[int, int]
        +ir_led_brightness: float
        +model_path: str
        +confidence_threshold: float
    }
}

' Relationships
InsectObserverSystem --> DetectorInterface
InsectObserverSystem --> ActivityCalculatorInterface
InsectObserverSystem --> HardwareControllerInterface
InsectObserverSystem --> ConfigManager

InsectDetector ..|> DetectorInterface
YOLODetector ..|> DetectorInterface

ActivityCalculator ..|> ActivityCalculatorInterface
StandardActivityCalculator --|> ActivityCalculator

HardwareController ..|> HardwareControllerInterface
RaspberryPiController --|> HardwareController

ConfigManager --> SystemConfig
@enduml
```

### 2.2 クラス関係性の説明

| 関係 | 説明 | PlantUML記法 |
|------|------|-------------|
| **継承 (Inheritance)** | StandardActivityCalculator は ActivityCalculator を継承 | `--|>` |
| **実装 (Realization)** | 具象クラスがインターフェースを実装 | `..|>` |
| **集約 (Aggregation)** | InsectObserverSystem が各モジュールを集約 | `-->` |
| **依存 (Dependency)** | ConfigManager が SystemConfig に依存 | `-->` |

---

## 3. データモデルクラス図

### 3.1 検出データモデル

```plantuml
@startuml DetectionDataModel
!define RECTANGLE class

skinparam class {
    BackgroundColor lightgreen
    BorderColor darkgreen
    ArrowColor darkgreen
}

package "Detection Data Model" {
    class DetectionResult {
        +x_center: float
        +y_center: float
        +width: float
        +height: float
        +confidence: float
        +class_id: int
        +timestamp: str
        +__init__(x_center, y_center, width, height, confidence, class_id, timestamp)
        +to_dict(): Dict[str, Any]
        +from_dict(data: Dict): DetectionResult
        +validate(): bool
    }
    
    class DetectionRecord {
        +record_id: str
        +timestamp: datetime
        +detection_date: date
        +detection_time: time
        +insect_detected: bool
        +detection_count: int
        +x_center: Optional[float]
        +y_center: Optional[float]
        +bbox_width: Optional[float]
        +bbox_height: Optional[float]
        +confidence: Optional[float]
        +processing_time_ms: float
        +camera_settings: Dict[str, Any]
        +model_version: str
        +image_filepath: Optional[str]
        +annotated_image_filepath: Optional[str]
        +__post_init__(): None
        +to_csv_row(): List[str]
        +from_csv_row(row: List[str]): DetectionRecord
    }
    
    class DetectionDetail {
        +parent_record_id: str
        +detection_index: int
        +x_center: float
        +y_center: float
        +bbox_width: float
        +bbox_height: float
        +confidence: float
        +class_id: int
        +class_name: str
        +__post_init__(): None
        +to_csv_row(): List[str]
    }
}

DetectionRecord --> DetectionResult : converts from/to
DetectionRecord *-- DetectionDetail : contains multiple
@enduml
```

### 3.2 活動量データモデル

```plantuml
@startuml ActivityDataModel
!define RECTANGLE class

skinparam class {
    BackgroundColor lightyellow
    BorderColor orange
    ArrowColor orange
}

package "Activity Data Model" {
    class ActivityMetrics {
        +total_detections: int
        +total_distance: float
        +avg_activity_per_hour: float
        +peak_activity_time: str
        +activity_duration: float
        +movement_patterns: List[str]
        +__post_init__(): None
        +to_dict(): Dict[str, Any]
        +calculate_activity_score(): float
    }
    
    class DailyActivitySummary {
        +summary_date: date
        +total_detections: int
        +unique_detection_periods: int
        +first_detection_time: Optional[time]
        +last_detection_time: Optional[time]
        +total_movement_distance: float
        +average_movement_per_detection: float
        +max_movement_distance: float
        +most_active_hour: int
        +activity_duration_minutes: float
        +inactive_periods_count: int
        +activity_area_pixels: float
        +center_of_activity_x: float
        +center_of_activity_y: float
        +data_completeness_ratio: float
        +detection_reliability_score: float
        +analysis_timestamp: datetime
        +analysis_version: str
        +__post_init__(): None
        +to_csv_row(): List[str]
        +from_csv_row(row: List[str]): DailyActivitySummary
        +generate_summary_text(): str
    }
    
    class HourlyActivitySummary {
        +summary_date: date
        +hour: int
        +detections_count: int
        +movement_distance: float
        +average_confidence: float
        +detection_frequency: float
        +avg_x_position: float
        +avg_y_position: float
        +position_variance_x: float
        +position_variance_y: float
        +analysis_timestamp: datetime
        +__post_init__(): None
        +to_csv_row(): List[str]
    }
}

DailyActivitySummary --> ActivityMetrics : derives from
DailyActivitySummary *-- HourlyActivitySummary : aggregates 24 hours
@enduml
```

---

## 4. モジュール別詳細クラス図

### 4.1 検出モジュール詳細図

```plantuml
@startuml DetectionModuleDetail
!define RECTANGLE class

skinparam class {
    BackgroundColor lightcyan
    BorderColor blue
    ArrowColor blue
}

package "Detection Module Detail" {
    abstract class DetectorInterface {
        {abstract} +initialize(config: Dict): bool
        {abstract} +detect(image: np.ndarray): List[DetectionResult]
        {abstract} +get_status(): Dict[str, Any]
        {abstract} +cleanup(): None
    }
    
    class InsectDetector {
        -config: Dict[str, Any]
        -model: Optional[YOLO]
        -camera: Optional[CameraController]
        -hardware_controller: HardwareController
        -detection_count: int
        -last_detection_time: Optional[datetime]
        +__init__(config: Dict[str, Any])
        +initialize_model(model_path: str): bool
        +capture_image(): Optional[np.ndarray]
        +detect_insects(image: np.ndarray): List[DetectionResult]
        +process_detection_results(results, image): Dict[str, Any]
        +save_detection_image(image, results, timestamp): str
        +get_detection_statistics(): Dict[str, Any]
        +reset_statistics(): None
        +cleanup(): None
    }
    
    class YOLODetector {
        -model: Optional[YOLO]
        -config: Dict[str, Any]
        -initialized: bool
        -model_load_time: float
        -inference_count: int
        +__init__()
        +initialize(config: Dict): bool
        +detect(image: np.ndarray): List[DetectionResult]
        +preprocess_image(image: np.ndarray): np.ndarray
        +postprocess_results(results): List[DetectionResult]
        +get_status(): Dict[str, Any]
        +cleanup(): None
    }
    
    class DataValidator {
        +validate_image(image: np.ndarray): bool
        +validate_detection_result(result: DetectionResult): bool
        +validate_csv_data(df: pd.DataFrame): List[str]
        +sanitize_coordinates(x: float, y: float, img_shape): Tuple[float, float]
    }
    
    class PerformanceMonitor {
        -metrics: Dict[str, List[float]]
        -start_times: Dict[str, float]
        +start_timer(operation: str): None
        +end_timer(operation: str): float
        +get_performance_stats(operation: str): Dict[str, float]
        +reset_metrics(): None
    }
    
    enum DetectionStatus {
        UNINITIALIZED
        INITIALIZING
        READY
        DETECTING
        ERROR
        CLEANUP
    }
}

DetectorInterface <|-- InsectDetector
DetectorInterface <|-- YOLODetector
InsectDetector --> DataValidator : uses
InsectDetector --> PerformanceMonitor : uses
InsectDetector --> DetectionStatus : has
@enduml
```

### 4.2 活動量算出モジュール詳細図

```plantuml
@startuml ActivityModuleDetail
!define RECTANGLE class

skinparam class {
    BackgroundColor lightpink
    BorderColor red
    ArrowColor red
}

package "Activity Analysis Module Detail" {
    abstract class ActivityCalculatorInterface {
        {abstract} +calculate_daily_activity(data: pd.DataFrame): DailyActivitySummary
        {abstract} +calculate_movement_distance(data: pd.DataFrame): List[float]
        {abstract} +generate_visualization(summary, output_path): List[str]
    }
    
    class ActivityCalculator {
        -config: Dict[str, Any]
        -data_processor: DataProcessor
        -visualizer: Visualizer
        -movement_threshold: float
        -outlier_threshold: float
        +__init__(config: Dict[str, Any])
        +load_detection_data(date: str): pd.DataFrame
        +calculate_movement_distance(data: pd.DataFrame): List[float]
        +calculate_activity_metrics(data: pd.DataFrame): ActivityMetrics
        +generate_activity_chart(metrics, output_path): str
        +generate_movement_heatmap(data, output_path): str
        +analyze_activity_patterns(data: pd.DataFrame): Dict[str, Any]
        +detect_anomalies(data: pd.DataFrame): List[Dict[str, Any]]
    }
    
    class StandardActivityCalculator {
        -smoothing_enabled: bool
        -smoothing_window_size: int
        -peak_detection_enabled: bool
        +__init__(config: Dict[str, Any])
        +calculate_daily_activity(data: pd.DataFrame): DailyActivitySummary
        +calculate_movement_distance(data: pd.DataFrame): List[float]
        +generate_visualization(summary, output_path): List[str]
        +smooth_movement_data(distances: List[float]): List[float]
        +detect_activity_peaks(data: pd.DataFrame): List[Tuple[datetime, float]]
        +classify_movement_patterns(data: pd.DataFrame): List[str]
    }
    
    class DataProcessor {
        +clean_detection_data(df: pd.DataFrame): pd.DataFrame
        +remove_duplicates(df: pd.DataFrame): pd.DataFrame
        +handle_outliers(df: pd.DataFrame): pd.DataFrame
        +handle_missing_values(df: pd.DataFrame): pd.DataFrame
        +normalize_data_types(df: pd.DataFrame): pd.DataFrame
        +filter_movement_outliers(df: pd.DataFrame): pd.DataFrame
    }
    
    class Visualizer {
        -config: Dict[str, Any]
        +create_activity_chart(metrics: ActivityMetrics, output_path: str): str
        +create_movement_heatmap(data: pd.DataFrame, output_path: str): str
        +create_hourly_activity_chart(data: pd.DataFrame, output_path: str): str
        +create_movement_trajectory(data: pd.DataFrame, output_path: str): str
        +create_summary_dashboard(summary: DailyActivitySummary, output_path: str): str
    }
    
    class StatisticsCalculator {
        +calculate_basic_stats(data: List[float]): Dict[str, float]
        +calculate_percentiles(data: List[float], percentiles: List[float]): Dict[str, float]
        +calculate_moving_average(data: List[float], window_size: int): List[float]
        +detect_outliers_zscore(data: List[float], threshold: float): List[int]
        +calculate_correlation(x: List[float], y: List[float]): float
    }
}

ActivityCalculatorInterface <|-- ActivityCalculator
ActivityCalculator <|-- StandardActivityCalculator
ActivityCalculator --> DataProcessor : uses
ActivityCalculator --> Visualizer : uses
ActivityCalculator --> StatisticsCalculator : uses
@enduml
```

### 4.3 ハードウェア制御モジュール詳細図

```plantuml
@startuml HardwareModuleDetail
!define RECTANGLE class

skinparam class {
    BackgroundColor lightgray
    BorderColor darkgray
    ArrowColor darkgray
}

package "Hardware Control Module Detail" {
    abstract class HardwareControllerInterface {
        {abstract} +initialize_hardware(): bool
        {abstract} +capture_image(settings): Optional[np.ndarray]
        {abstract} +control_led(brightness: float): bool
        {abstract} +get_system_status(): Dict[str, Any]
        {abstract} +cleanup_resources(): None
    }
    
    class HardwareController {
        -config: Dict[str, Any]
        -camera: Optional[CameraInterface]
        -gpio_controller: Optional[GPIOInterface]
        -initialized: bool
        +__init__(config: Dict[str, Any])
        +initialize_hardware(): bool
        +capture_image(settings): Optional[np.ndarray]
        +control_led(brightness: float): bool
        +get_system_status(): Dict[str, Any]
        +cleanup_resources(): None
    }
    
    class RaspberryPiController {
        -camera: Optional[Picamera2]
        -gpio_initialized: bool
        -led_pwm: Optional[GPIO.PWM]
        -current_brightness: float
        -fade_thread: Optional[threading.Thread]
        -fade_stop_event: threading.Event
        +__init__()
        +initialize_hardware(): bool
        +capture_image(settings): Optional[np.ndarray]
        +control_led(brightness: float): bool
        +led_fade(target_brightness: float, duration_ms: int): bool
        +get_system_status(): Dict[str, Any]
        +cleanup_resources(): None
        -_fade_worker(target_brightness: float, duration_ms: int): None
    }
    
    abstract class CameraInterface {
        {abstract} +initialize(config: Dict): bool
        {abstract} +capture_image(): Optional[np.ndarray]
        {abstract} +set_exposure(exposure_time_us: int): bool
        {abstract} +set_gain(gain: float): bool
        {abstract} +get_camera_info(): Dict[str, Any]
    }
    
    class PiCamera2Controller {
        -camera: Optional[Picamera2]
        -config: Optional[Dict[str, Any]]
        -initialized: bool
        +__init__()
        +initialize(config: Dict): bool
        +capture_image(): Optional[np.ndarray]
        +set_exposure(exposure_time_us: int): bool
        +set_gain(gain: float): bool
        +get_camera_info(): Dict[str, Any]
        +cleanup(): None
        -_create_camera_config(config: Dict): Dict[str, Any]
        -_apply_controls(config: Dict): None
    }
    
    abstract class GPIOInterface {
        {abstract} +initialize(config: Dict): bool
        {abstract} +set_led_brightness(brightness: float): bool
        {abstract} +led_fade(target_brightness: float, duration_ms: int): bool
        {abstract} +cleanup(): None
    }
    
    class RPiGPIOController {
        -initialized: bool
        -led_pin: Optional[int]
        -led_pwm: Optional[GPIO.PWM]
        -current_brightness: float
        -fade_thread: Optional[threading.Thread]
        -fade_stop_event: threading.Event
        +__init__()
        +initialize(config: Dict): bool
        +set_led_brightness(brightness: float): bool
        +led_fade(target_brightness: float, duration_ms: int): bool
        +get_gpio_status(): Dict[str, Any]
        +cleanup(): None
        -_fade_worker(target_brightness: float, duration_ms: int): None
    }
}

HardwareControllerInterface <|-- HardwareController
HardwareController <|-- RaspberryPiController
CameraInterface <|-- PiCamera2Controller
GPIOInterface <|-- RPiGPIOController

HardwareController --> CameraInterface : uses
HardwareController --> GPIOInterface : uses
RaspberryPiController --> PiCamera2Controller : contains
RaspberryPiController --> RPiGPIOController : contains
@enduml
```

---

## 5. 実装時の注意事項

### 5.1 クラス設計ガイドライン

#### 5.1.1 継承vs集約の選択
- **継承を使う場合**: IS-A関係（StandardActivityCalculator は ActivityCalculator である）
- **集約を使う場合**: HAS-A関係（InsectObserverSystem は DetectorInterface を持つ）

#### 5.1.2 インターフェース設計原則
- 各インターフェースは単一責任を持つ
- 実装クラスは複数のインターフェースを実装可能
- 依存性注入でテスタビリティを向上

#### 5.1.3 エラーハンドリング戦略
- 階層化された例外クラス構造
- 各モジュールで適切な例外タイプを発生
- ErrorHandlerで統一的な処理

### 5.2 実装優先順位

#### 5.2.1 Phase 1: 基盤クラス
1. データモデルクラス（DetectionResult, ActivityMetrics等）
2. 設定管理クラス（SystemConfig, ConfigManager）
3. 基本インターフェース定義

#### 5.2.2 Phase 2: コア機能クラス
1. ハードウェア制御クラス
2. 検出器クラス
3. 活動量算出クラス

#### 5.2.3 Phase 3: 統合・運用クラス
1. メインシステムクラス
2. イベントシステム
3. 診断・監視クラス

### 5.3 テスト戦略

#### 5.3.1 単体テスト対象
- 各データモデルクラスの検証機能
- アルゴリズム実装クラス（移動距離計算等）
- ユーティリティクラス

#### 5.3.2 統合テスト対象
- インターフェース実装の互換性
- モジュール間のデータ受け渡し
- エラーハンドリングの連携

#### 5.3.3 モックオブジェクト使用箇所
- ハードウェア制御（カメラ・GPIO）
- 外部API連携（Hugging Face）
- ファイルシステム操作

---

*文書バージョン: 1.0*  
*最終更新日: 2025-07-25*  
*承認者: 開発チーム*