# データ設計書

**文書番号**: 12-002-DATA-001  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: データ設計書  
**バージョン**: 1.0  
**作成日**: 2025-07-25  
**作成者**: 開発チーム  

---

## 1. 文書概要

### 1.1 目的
本文書は昆虫自動観察システムで扱うデータの構造、保存形式、管理方法、および品質管理について詳細に定義する。

### 1.2 適用範囲
- データモデル設計
- ファイル形式・構造定義
- データフロー設計
- データ品質管理
- バックアップ・復旧設計
- データライフサイクル管理

### 1.3 関連文書
- システムアーキテクチャ設計書（system_architecture_design.md）
- ソフトウェア設計書（software_design.md）
- 要件定義書（12-002）

---

## 2. データアーキテクチャ概要

### 2.1 データアーキテクチャ図

```
┌─────────────────────────────────────────────────────────────────┐
│                  データアーキテクチャ全体構成                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │                 │  │                 │  │                 │  │
│  │   入力データ層   │  │  処理データ層   │  │  出力データ層   │  │
│  │   Input Data    │  │ Processing Data │  │  Output Data    │  │
│  │     Layer       │  │     Layer       │  │     Layer       │  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │   カメラ     │ │──┼─│   画像      │ │──┼─│   検出      │ │  │
│  │ │   画像      │ │  │ │  バッファ    │ │  │ │  ログ       │ │  │
│  │ │(RAW/JPEG)   │ │  │ │ (メモリ)     │ │  │ │ (CSV)       │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  │                 │  │        │        │  │                 │  │
│  │ ┌─────────────┐ │  │        ▼        │  │ ┌─────────────┐ │  │
│  │ │   設定      │ │──┼─┌─────────────┐ │  │ │   注釈      │ │  │
│  │ │  ファイル    │ │  │ │   検出      │ │──┼─│   画像      │ │  │
│  │ │ (JSON)      │ │  │ │  結果       │ │  │ │ (PNG)       │ │  │
│  │ └─────────────┘ │  │ │(オブジェクト)│ │  │ └─────────────┘ │  │
│  │                 │  │ └─────────────┘ │  │                 │  │
│  │ ┌─────────────┐ │  │        │        │  │ ┌─────────────┐ │  │
│  │ │ 学習済み     │ │──┘        ▼        │  │ │  活動量     │ │  │
│  │ │ モデル      │ │    ┌─────────────┐ │  │ │  統計       │ │  │
│  │ │ (.pt/.onnx) │ │    │   活動量    │ │──┼─│ (CSV)       │ │  │
│  │ └─────────────┘ │    │  算出       │ │  │ └─────────────┘ │  │
│  │                 │    │ データ      │ │  │                 │  │
│  └─────────────────┘    │(DataFrame)  │ │  │ ┌─────────────┐ │  │
│                         └─────────────┘ │  │ │  可視化     │ │  │
│                                         │  │ │  グラフ     │ │  │
│                                         │  │ │ (PNG)       │ │  │
│                                         │  │ └─────────────┘ │  │
│                                         │  │                 │  │
│                                         │  └─────────────────┘  │
├─────────────────────────────────────────┴───────────────────────┤
│                      データ管理層                               │
│                   Data Management Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │                 │  │                 │  │                 │  │
│  │ ファイルシステム  │  │  データ品質管理  │  │ バックアップ     │  │
│  │ File System     │  │ Data Quality    │  │ & Recovery      │  │
│  │   Management    │  │  Management     │  │   Management    │  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │ディレクトリ  │ │  │ │   検証      │ │  │ │   自動      │ │  │
│  │ │   構造      │ │  │ │  ルール     │ │  │ │ バックアップ │ │  │
│  │ │   管理      │ │  │ │   実行      │ │  │ │   実行      │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │ファイル名    │ │  │ │  異常値     │ │  │ │   復旧      │ │  │
│  │ │  規則       │ │  │ │  検出       │ │  │ │  手順       │ │  │
│  │ │  統一       │ │  │ │  処理       │ │  │ │  実行       │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │ 容量管理     │ │  │ │  データ     │ │  │ │  世代管理   │ │  │
│  │ │ ログ        │ │  │ │ 整合性      │ │  │ │  ポリシー   │ │  │
│  │ │ ローテーション│ │  │ │  確認       │ │  │ │   適用      │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 データ分類体系

| データ分類 | 説明 | 保存期間 | 重要度 |
|-----------|------|----------|--------|
| **リアルタイムデータ** | 検出処理中の一時データ | 処理完了まで | 低 |
| **検出ログデータ** | 昆虫検出結果の記録 | 1年間 | 高 |  
| **画像データ** | 撮影・注釈付き画像 | 3ヶ月間 | 中 |
| **統計データ** | 活動量・分析結果 | 3年間 | 高 |
| **設定データ** | システム設定情報 | 永続 | 高 |
| **ログデータ** | システム動作ログ | 6ヶ月間 | 中 |

---

## 3. データモデル設計

### 3.1 検出データモデル

#### 3.1.1 検出結果エンティティ
```python
@dataclass
class DetectionRecord:
    """検出結果レコード"""
    
    # 主キー
    record_id: str  # UUID4形式
    
    # 時刻情報
    timestamp: datetime  # 検出実行時刻
    detection_date: date  # 検出日付（分析用）
    detection_time: time  # 検出時刻（分析用）
    
    # 検出結果
    insect_detected: bool  # 昆虫検出フラグ
    detection_count: int   # 同一フレーム内検出数
    
    # 位置情報（最も信頼度の高い検出結果）
    x_center: Optional[float]  # 中心X座標（ピクセル）
    y_center: Optional[float]  # 中心Y座標（ピクセル）
    bbox_width: Optional[float]   # バウンディングボックス幅
    bbox_height: Optional[float]  # バウンディングボックス高さ
    
    # 信頼度情報
    confidence: Optional[float]  # 検出信頼度（0.0-1.0）
    
    # メタデータ
    processing_time_ms: float  # 処理時間（ミリ秒）
    camera_settings: Dict[str, Any]  # カメラ設定情報
    model_version: str  # 使用モデルバージョン
    
    # ファイル関連
    image_filepath: Optional[str]  # 元画像ファイルパス
    annotated_image_filepath: Optional[str]  # 注釈画像パス

# CSV出力フォーマット
CSV_COLUMNS = [
    'record_id', 'timestamp', 'detection_date', 'detection_time',
    'insect_detected', 'detection_count', 'x_center', 'y_center',
    'bbox_width', 'bbox_height', 'confidence', 'processing_time_ms',
    'model_version', 'image_filepath', 'annotated_image_filepath'
]
```

#### 3.1.2 検出詳細エンティティ（複数検出時）
```python
@dataclass
class DetectionDetail:
    """個別検出詳細"""
    
    # 外部キー
    parent_record_id: str  # 親レコードID
    
    # 個別検出情報
    detection_index: int  # 検出インデックス（0から開始）
    x_center: float
    y_center: float
    bbox_width: float
    bbox_height: float
    confidence: float
    class_id: int  # クラスID（将来の複数種対応用）
    class_name: str  # クラス名（'beetle'など）

# CSV出力フォーマット
DETAIL_CSV_COLUMNS = [
    'parent_record_id', 'detection_index', 'x_center', 'y_center',
    'bbox_width', 'bbox_height', 'confidence', 'class_id', 'class_name'
]
```

### 3.2 活動量データモデル

#### 3.2.1 日次活動統計エンティティ
```python
@dataclass
class DailyActivitySummary:
    """日次活動統計"""
    
    # 主キー
    summary_date: date  # 統計対象日付
    
    # 基本統計
    total_detections: int  # 総検出回数
    unique_detection_periods: int  # 検出期間数
    first_detection_time: Optional[time]  # 初回検出時刻
    last_detection_time: Optional[time]   # 最終検出時刻
    
    # 活動量統計
    total_movement_distance: float  # 総移動距離（ピクセル）
    average_movement_per_detection: float  # 検出あたり平均移動距離
    max_movement_distance: float  # 最大移動距離
    
    # 時間分析
    most_active_hour: int  # 最も活発な時間帯（0-23）
    activity_duration_minutes: float  # 活動継続時間（分）
    inactive_periods_count: int  # 非活動期間数
    
    # 位置分析
    activity_area_pixels: float  # 活動範囲面積
    center_of_activity_x: float  # 活動中心X座標
    center_of_activity_y: float  # 活動中心Y座標
    
    # 品質指標
    data_completeness_ratio: float  # データ完全性比率
    detection_reliability_score: float  # 検出信頼性スコア
    
    # メタデータ
    analysis_timestamp: datetime  # 分析実行時刻
    analysis_version: str  # 分析アルゴリズムバージョン

# CSV出力フォーマット  
SUMMARY_CSV_COLUMNS = [
    'summary_date', 'total_detections', 'unique_detection_periods',
    'first_detection_time', 'last_detection_time', 'total_movement_distance',
    'average_movement_per_detection', 'max_movement_distance', 'most_active_hour',
    'activity_duration_minutes', 'inactive_periods_count', 'activity_area_pixels',
    'center_of_activity_x', 'center_of_activity_y', 'data_completeness_ratio',
    'detection_reliability_score', 'analysis_timestamp', 'analysis_version'
]
```

#### 3.2.2 時間別活動統計エンティティ
```python
@dataclass  
class HourlyActivitySummary:
    """時間別活動統計"""
    
    # 主キー
    summary_date: date
    hour: int  # 時間（0-23）
    
    # 時間別統計
    detections_count: int  # 該当時間の検出回数
    movement_distance: float  # 該当時間の移動距離
    average_confidence: float  # 平均信頼度
    detection_frequency: float  # 検出頻度（回/分）
    
    # 位置統計
    avg_x_position: float  # 平均X位置
    avg_y_position: float  # 平均Y位置
    position_variance_x: float  # X位置分散
    position_variance_y: float  # Y位置分散
    
    # メタデータ
    analysis_timestamp: datetime

# CSV出力フォーマット
HOURLY_CSV_COLUMNS = [
    'summary_date', 'hour', 'detections_count', 'movement_distance',
    'average_confidence', 'detection_frequency', 'avg_x_position',
    'avg_y_position', 'position_variance_x', 'position_variance_y',
    'analysis_timestamp'
]
```

### 3.3 システムデータモデル

#### 3.3.1 システム設定エンティティ
```python
@dataclass
class SystemConfiguration:
    """システム設定"""
    
    # 設定メタデータ
    config_version: str  # 設定バージョン
    last_updated: datetime  # 最終更新時刻
    updated_by: str  # 更新者
    
    # システム設定
    detection_interval_seconds: int  # 検出間隔
    log_level: str  # ログレベル
    data_retention_days: int  # データ保持期間
    auto_cleanup_enabled: bool  # 自動クリーンアップ有効
    
    # ハードウェア設定
    camera_resolution_width: int
    camera_resolution_height: int
    camera_fps: int
    ir_led_brightness: float  # 0.0-1.0
    ir_led_pwm_frequency: int
    
    # 検出設定
    model_path: str
    confidence_threshold: float
    nms_threshold: float
    max_detections_per_frame: int
    
    # 分析設定
    movement_threshold_pixels: float
    outlier_detection_enabled: bool
    outlier_threshold_sigma: float

# JSON出力フォーマット例
SYSTEM_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "config_version": {"type": "string"},
        "last_updated": {"type": "string", "format": "date-time"},
        "detection": {
            "type": "object",
            "properties": {
                "interval_seconds": {"type": "integer", "minimum": 1},
                "confidence_threshold": {"type": "number", "minimum": 0, "maximum": 1}
            }
        }
    }
}
```

#### 3.3.2 システムログエンティティ
```python
@dataclass
class SystemLogRecord:
    """システムログレコード"""
    
    # 基本情報
    log_id: str  # UUID4
    timestamp: datetime
    log_level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # ログ内容
    module_name: str  # ログ出力モジュール
    function_name: str  # ログ出力関数
    message: str  # ログメッセージ
    
    # 詳細情報
    exception_type: Optional[str]  # 例外タイプ
    exception_message: Optional[str]  # 例外メッセージ
    stack_trace: Optional[str]  # スタックトレース
    
    # システム状態
    cpu_usage_percent: Optional[float]
    memory_usage_percent: Optional[float]
    disk_usage_percent: Optional[float]
    temperature_celsius: Optional[float]

# ログフォーマット（JSON Lines形式）
LOG_JSON_FORMAT = {
    "timestamp": "2025-07-25T10:30:15.123456+09:00",
    "level": "INFO",
    "module": "insect_detector",
    "function": "detect_insects",
    "message": "Detection completed successfully",
    "processing_time_ms": 2847.3,
    "detections_found": 2,
    "system_stats": {
        "cpu_percent": 45.2,
        "memory_percent": 62.8,
        "temperature": 48.5
    }
}
```

---

## 4. ファイル形式・構造設計

### 4.1 ディレクトリ構造

```
/home/pi/insect_observer/
├── data/                           # メインデータディレクトリ
│   ├── raw/                        # 生データ
│   │   ├── detection_logs/         # 検出ログ（日別）
│   │   │   ├── detection_20250725.csv
│   │   │   ├── detection_20250726.csv
│   │   │   └── ...
│   │   ├── detection_details/      # 検出詳細（複数検出時）
│   │   │   ├── details_20250725.csv
│   │   │   └── ...
│   │   └── images/                 # 撮影画像
│   │       ├── original/           # 元画像（検出時のみ）
│   │       │   ├── 20250725_103045_001.jpg
│   │       │   └── ...
│   │       └── annotated/          # 注釈付き画像
│   │           ├── 20250725_103045_001_annotated.png
│   │           └── ...
│   ├── processed/                  # 処理済みデータ
│   │   ├── daily_summaries/        # 日次統計
│   │   │   ├── daily_summary_20250725.csv
│   │   │   └── ...
│   │   ├── hourly_summaries/       # 時間別統計
│   │   │   ├── hourly_summary_20250725.csv
│   │   │   └── ...
│   │   └── analysis_reports/       # 分析レポート
│   │       ├── monthly_report_202507.json
│   │       └── ...
│   └── visualizations/             # 可視化データ
│       ├── charts/                 # グラフ画像
│       │   ├── activity_chart_20250725.png
│       │   ├── movement_heatmap_20250725.png
│       │   └── ...
│       └── animations/             # アニメーション（将来用）
│           └── ...
├── config/                         # 設定ファイル
│   ├── system_config.json          # システム設定
│   ├── hardware_config.json        # ハードウェア設定
│   ├── detection_config.json       # 検出設定
│   └── analysis_config.json        # 分析設定
├── logs/                           # ログファイル
│   ├── system/                     # システムログ
│   │   ├── system_20250725.log     # 日別システムログ
│   │   └── ...
│   ├── detection/                  # 検出ログ
│   │   ├── detection_20250725.log  # 日別検出ログ
│   │   └── ...
│   └── error/                      # エラーログ
│       ├── error_20250725.log      # 日別エラーログ
│       └── ...
├── backup/                         # バックアップデータ
│   ├── daily/                      # 日次バックアップ
│   │   ├── backup_20250725.tar.gz
│   │   └── ...
│   └── weekly/                     # 週次バックアップ
│       ├── backup_week_30.tar.gz
│       └── ...
└── temp/                           # 一時ファイル
    ├── processing/                 # 処理中ファイル
    └── cache/                      # キャッシュファイル
```

### 4.2 ファイル命名規則

#### 4.2.1 命名規則体系
```python
class FileNamingConvention:
    """ファイル命名規則クラス"""
    
    # 日付フォーマット
    DATE_FORMAT = "%Y%m%d"          # 20250725
    DATETIME_FORMAT = "%Y%m%d_%H%M%S"  # 20250725_103045
    
    # ファイル名パターン
    DETECTION_LOG_PATTERN = "detection_{date}.csv"
    DETECTION_DETAIL_PATTERN = "details_{date}.csv"
    DAILY_SUMMARY_PATTERN = "daily_summary_{date}.csv"
    HOURLY_SUMMARY_PATTERN = "hourly_summary_{date}.csv"
    
    # 画像ファイルパターン
    ORIGINAL_IMAGE_PATTERN = "{datetime}_{sequence:03d}.jpg"
    ANNOTATED_IMAGE_PATTERN = "{datetime}_{sequence:03d}_annotated.png"
    
    # 可視化ファイルパターン
    ACTIVITY_CHART_PATTERN = "activity_chart_{date}.png"
    MOVEMENT_HEATMAP_PATTERN = "movement_heatmap_{date}.png"
    
    # ログファイルパターン
    SYSTEM_LOG_PATTERN = "system_{date}.log"
    DETECTION_LOG_FILE_PATTERN = "detection_{date}.log"
    ERROR_LOG_PATTERN = "error_{date}.log"
    
    # バックアップファイルパターン
    DAILY_BACKUP_PATTERN = "backup_{date}.tar.gz"
    WEEKLY_BACKUP_PATTERN = "backup_week_{week_number:02d}.tar.gz"
    
    @classmethod
    def generate_detection_log_filename(cls, date: datetime) -> str:
        """検出ログファイル名生成"""
        return cls.DETECTION_LOG_PATTERN.format(
            date=date.strftime(cls.DATE_FORMAT)
        )
    
    @classmethod
    def generate_image_filename(cls, timestamp: datetime, sequence: int, 
                              annotated: bool = False) -> str:
        """画像ファイル名生成"""
        datetime_str = timestamp.strftime(cls.DATETIME_FORMAT)
        if annotated:
            return cls.ANNOTATED_IMAGE_PATTERN.format(
                datetime=datetime_str, sequence=sequence
            )
        else:
            return cls.ORIGINAL_IMAGE_PATTERN.format(
                datetime=datetime_str, sequence=sequence
            )
    
    @classmethod
    def parse_filename_timestamp(cls, filename: str) -> Optional[datetime]:
        """ファイル名からタイムスタンプ抽出"""
        import re
        
        # 日時パターンを抽出
        pattern = r'(\d{8}_\d{6})'
        match = re.search(pattern, filename)
        
        if match:
            datetime_str = match.group(1)
            return datetime.strptime(datetime_str, cls.DATETIME_FORMAT)
        
        # 日付のみパターンを抽出
        pattern = r'(\d{8})'
        match = re.search(pattern, filename)
        
        if match:
            date_str = match.group(1)
            return datetime.strptime(date_str, cls.DATE_FORMAT)
        
        return None
```

### 4.3 データファイル形式定義

#### 4.3.1 検出ログCSV形式
```csv
# detection_20250725.csv
# 文字エンコーディング: UTF-8 (BOM なし)
# 区切り文字: カンマ (,)
# 改行文字: LF (\n)
# 数値フォーマット: 小数点以下3桁まで

record_id,timestamp,detection_date,detection_time,insect_detected,detection_count,x_center,y_center,bbox_width,bbox_height,confidence,processing_time_ms,model_version,image_filepath,annotated_image_filepath
"550e8400-e29b-41d4-a716-446655440000","2025-07-25T10:30:00.123+09:00","2025-07-25","10:30:00",true,2,320.5,240.3,45.2,38.7,0.852,2847.3,"v1.0.0","./data/raw/images/original/20250725_103000_001.jpg","./data/raw/images/annotated/20250725_103000_001_annotated.png"
"550e8400-e29b-41d4-a716-446655440001","2025-07-25T10:31:00.456+09:00","2025-07-25","10:31:00",false,0,,,,,0.0,1234.5,"v1.0.0","",""
```

#### 4.3.2 日次統計CSV形式
```csv
# daily_summary_20250725.csv
# 日次活動統計データ

summary_date,total_detections,unique_detection_periods,first_detection_time,last_detection_time,total_movement_distance,average_movement_per_detection,max_movement_distance,most_active_hour,activity_duration_minutes,inactive_periods_count,activity_area_pixels,center_of_activity_x,center_of_activity_y,data_completeness_ratio,detection_reliability_score,analysis_timestamp,analysis_version
"2025-07-25",145,23,"06:23:15","23:45:30",2847.6,19.6,156.3,22,892.5,12,15670.2,324.7,251.8,0.993,0.876,"2025-07-26T01:00:15.789+09:00","v1.0.0"
```

#### 4.3.3 システム設定JSON形式
```json
{
  "config_metadata": {
    "config_version": "1.0.0",
    "last_updated": "2025-07-25T09:00:00+09:00",
    "updated_by": "system_admin",
    "schema_version": "1.0"
  },
  "system": {
    "detection_interval_seconds": 60,
    "log_level": "INFO",
    "data_retention_days": 365,
    "auto_cleanup_enabled": true,
    "timezone": "Asia/Tokyo"
  },
  "hardware": {
    "camera": {
      "resolution_width": 1920,
      "resolution_height": 1080,
      "fps": 30,
      "auto_exposure": true,
      "exposure_compensation": 0
    },
    "ir_led": {
      "gpio_pin": 18,
      "brightness": 0.8,
      "pwm_frequency": 1000,
      "fade_in_ms": 100,
      "fade_out_ms": 100
    }
  },
  "detection": {
    "model_path": "./weights/beetle_detection_v1.pt",
    "confidence_threshold": 0.5,
    "nms_threshold": 0.4,
    "max_detections_per_frame": 10,
    "input_size": [640, 640],
    "class_names": ["beetle"]
  },
  "analysis": {
    "movement_threshold_pixels": 5.0,
    "time_window_minutes": 60,
    "outlier_detection_enabled": true,
    "outlier_threshold_sigma": 3.0,
    "smoothing_enabled": true,
    "smoothing_window_size": 5
  },
  "data_management": {
    "backup_enabled": true,
    "backup_schedule": "daily",
    "compression_enabled": true,
    "encryption_enabled": false
  }
}
```

---

## 5. データ品質管理

### 5.1 データ検証ルール

#### 5.1.1 検証ルール定義
```python
class DataValidationRules:
    """データ検証ルールクラス"""
    
    # 検出データ検証ルール
    DETECTION_RULES = {
        'timestamp': {
            'required': True,
            'type': 'datetime',
            'format': 'ISO8601',
            'range': {
                'min': datetime(2025, 1, 1),
                'max': datetime(2030, 12, 31)
            }
        },
        'insect_detected': {
            'required': True,
            'type': 'boolean'
        },
        'detection_count': {
            'required': True,
            'type': 'integer',
            'range': {'min': 0, 'max': 50}
        },
        'x_center': {
            'required_if': 'insect_detected == True',
            'type': 'float',
            'range': {'min': 0.0, 'max': 1920.0}
        },
        'y_center': {
            'required_if': 'insect_detected == True',
            'type': 'float',
            'range': {'min': 0.0, 'max': 1080.0}
        },
        'confidence': {
            'required_if': 'insect_detected == True',
            'type': 'float',
            'range': {'min': 0.0, 'max': 1.0}
        },
        'processing_time_ms': {
            'required': True,
            'type': 'float',
            'range': {'min': 0.0, 'max': 30000.0}  # 30秒以内
        }
    }
    
    # 統計データ検証ルール
    SUMMARY_RULES = {
        'summary_date': {
            'required': True,
            'type': 'date',
            'format': 'YYYY-MM-DD'
        },
        'total_detections': {
            'required': True,
            'type': 'integer',
            'range': {'min': 0, 'max': 2000}  # 1日最大2000検出
        },
        'total_movement_distance': {
            'required': True,
            'type': 'float',
            'range': {'min': 0.0, 'max': 100000.0}
        },
        'data_completeness_ratio': {
            'required': True,
            'type': 'float',
            'range': {'min': 0.0, 'max': 1.0}
        }
    }

class DataValidator:
    """データ検証実行クラス"""
    
    def __init__(self):
        self.rules = DataValidationRules()
        self.validation_errors = []
        
    def validate_detection_record(self, record: DetectionRecord) -> List[str]:
        """検出レコード検証
        
        Args:
            record: 検証対象レコード
            
        Returns:
            検証エラーリスト
        """
        errors = []
        
        # 必須項目チェック
        if not record.timestamp:
            errors.append("timestamp is required")
            
        if record.insect_detected is None:
            errors.append("insect_detected is required")
            
        # 条件付き必須項目チェック
        if record.insect_detected and not record.x_center:
            errors.append("x_center is required when insect_detected is True")
            
        # 範囲チェック
        if record.confidence and (record.confidence < 0.0 or record.confidence > 1.0):
            errors.append(f"confidence out of range: {record.confidence}")
            
        if record.processing_time_ms and record.processing_time_ms > 30000.0:
            errors.append(f"processing_time_ms too high: {record.processing_time_ms}ms")
            
        # データ整合性チェック
        if record.insect_detected and record.detection_count == 0:
            errors.append("detection_count should be > 0 when insect_detected is True")
            
        return errors
    
    def validate_csv_file(self, filepath: str) -> Dict[str, Any]:
        """CSVファイル検証
        
        Args:
            filepath: 検証対象ファイルパス
            
        Returns:
            検証結果サマリー
        """
        validation_result = {
            'filepath': filepath,
            'is_valid': True,
            'total_records': 0,
            'valid_records': 0,
            'error_records': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            df = pd.read_csv(filepath)
            validation_result['total_records'] = len(df)
            
            # 列存在チェック
            required_columns = ['timestamp', 'insect_detected', 'detection_count']
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                validation_result['errors'].append(
                    f"Missing required columns: {missing_columns}"
                )
                validation_result['is_valid'] = False
                return validation_result
            
            # レコード単位検証
            for index, row in df.iterrows():
                record_errors = self._validate_row(row)
                if record_errors:
                    validation_result['error_records'] += 1
                    validation_result['errors'].extend([
                        f"Row {index + 1}: {error}" for error in record_errors
                    ])
                else:
                    validation_result['valid_records'] += 1
            
            # 全体統計チェック
            self._validate_file_statistics(df, validation_result)
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"File processing error: {str(e)}")
            
        if validation_result['errors']:
            validation_result['is_valid'] = False
            
        return validation_result
    
    def _validate_row(self, row: pd.Series) -> List[str]:
        """行データ検証"""
        errors = []
        
        # タイムスタンプ検証
        try:
            pd.to_datetime(row['timestamp'])
        except:
            errors.append("Invalid timestamp format")
            
        # 数値範囲検証
        if 'confidence' in row and pd.notna(row['confidence']):
            if row['confidence'] < 0.0 or row['confidence'] > 1.0:
                errors.append(f"confidence out of range: {row['confidence']}")
        
        # 論理整合性検証
        if row.get('insect_detected', False) and row.get('detection_count', 0) == 0:
            errors.append("detection_count should be > 0 when insect detected")
            
        return errors
    
    def _validate_file_statistics(self, df: pd.DataFrame, 
                                result: Dict[str, Any]) -> None:
        """ファイル統計検証"""
        
        # 重複タイムスタンプチェック
        duplicate_timestamps = df['timestamp'].duplicated().sum()
        if duplicate_timestamps > 0:
            result['warnings'].append(
                f"{duplicate_timestamps} duplicate timestamps found"
            )
        
        # 時系列順序チェック
        timestamps = pd.to_datetime(df['timestamp'])
        if not timestamps.is_monotonic_increasing:
            result['warnings'].append("Timestamps are not in chronological order")
        
        # 検出率チェック
        if 'insect_detected' in df.columns:
            detection_rate = df['insect_detected'].mean()
            if detection_rate > 0.5:  # 50%以上の検出は異常
                result['warnings'].append(
                    f"High detection rate: {detection_rate:.1%}"
                )
```

### 5.2 データクリーニング

#### 5.2.1 異常値処理
```python
class DataCleaner:
    """データクリーニングクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.outlier_threshold = config.get('outlier_threshold_sigma', 3.0)
        self.movement_threshold = config.get('movement_threshold_pixels', 5.0)
        
    def clean_detection_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """検出データクリーニング
        
        Args:
            df: 検出データDataFrame
            
        Returns:
            クリーニング済みDataFrame
        """
        cleaned_df = df.copy()
        
        # 1. 重複レコード除去
        cleaned_df = self._remove_duplicates(cleaned_df)
        
        # 2. 異常値検出・除去
        cleaned_df = self._handle_outliers(cleaned_df)
        
        # 3. 欠損値処理
        cleaned_df = self._handle_missing_values(cleaned_df)
        
        # 4. データ型正規化
        cleaned_df = self._normalize_data_types(cleaned_df)
        
        # 5. 移動距離異常値フィルタ
        cleaned_df = self._filter_movement_outliers(cleaned_df)
        
        return cleaned_df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """重複レコード除去"""
        # タイムスタンプベースの重複除去
        df_cleaned = df.drop_duplicates(subset=['timestamp'], keep='first')
        
        removed_count = len(df) - len(df_cleaned)
        if removed_count > 0:
            logging.info(f"Removed {removed_count} duplicate records")
            
        return df_cleaned
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """異常値処理"""
        numeric_columns = ['x_center', 'y_center', 'confidence', 'processing_time_ms']
        
        for column in numeric_columns:
            if column in df.columns:
                # Z-score法による異常値検出
                z_scores = np.abs(stats.zscore(df[column].dropna()))
                outlier_mask = z_scores > self.outlier_threshold
                
                if outlier_mask.any():
                    outlier_count = outlier_mask.sum()
                    logging.warning(f"Found {outlier_count} outliers in {column}")
                    
                    # 異常値をNaNに置換（削除ではなく）
                    df.loc[df[column].notna() & outlier_mask, column] = np.nan
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """欠損値処理"""
        # 検出フラグがTrueなのに座標が欠損している場合の処理
        missing_coords_mask = (
            df['insect_detected'] == True
        ) & (
            df['x_center'].isna() | df['y_center'].isna()
        )
        
        if missing_coords_mask.any():
            # 検出フラグをFalseに変更
            df.loc[missing_coords_mask, 'insect_detected'] = False
            df.loc[missing_coords_mask, 'detection_count'] = 0
            
            logging.warning(
                f"Fixed {missing_coords_mask.sum()} records with missing coordinates"
            )
        
        return df
    
    def _normalize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """データ型正規化"""
        # タイムスタンプの正規化
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # ブール値の正規化
        if 'insect_detected' in df.columns:
            df['insect_detected'] = df['insect_detected'].astype(bool)
        
        # 数値型の正規化
        numeric_columns = ['x_center', 'y_center', 'confidence', 'processing_time_ms']
        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors='coerce')
        
        return df
    
    def _filter_movement_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """移動距離異常値フィルタ"""
        if len(df) < 2:
            return df
        
        # 連続する検出点間の距離を計算
        df_detected = df[df['insect_detected'] == True].copy()
        
        if len(df_detected) < 2:
            return df
        
        # 移動距離計算
        df_detected['prev_x'] = df_detected['x_center'].shift(1)
        df_detected['prev_y'] = df_detected['y_center'].shift(1)
        
        df_detected['movement_distance'] = np.sqrt(
            (df_detected['x_center'] - df_detected['prev_x'])**2 +
            (df_detected['y_center'] - df_detected['prev_y'])**2
        )
        
        # 異常な移動距離の検出（例：画面幅以上の移動）
        screen_diagonal = np.sqrt(1920**2 + 1080**2)  # 画面対角線
        abnormal_movement_mask = df_detected['movement_distance'] > screen_diagonal * 0.5
        
        if abnormal_movement_mask.any():
            abnormal_indices = df_detected[abnormal_movement_mask].index
            logging.warning(f"Found {len(abnormal_indices)} records with abnormal movement")
            
            # 異常な移動のレコードを検出なしに変更
            df.loc[abnormal_indices, 'insect_detected'] = False
            df.loc[abnormal_indices, 'detection_count'] = 0
            df.loc[abnormal_indices, ['x_center', 'y_center', 'confidence']] = np.nan
        
        return df
```

---

## 6. データライフサイクル管理

### 6.1 データ保持ポリシー

#### 6.1.1 保持期間定義
```python
class DataRetentionPolicy:
    """データ保持ポリシークラス"""
    
    # データ種別別保持期間（日数）
    RETENTION_PERIODS = {
        'detection_logs': 365,      # 検出ログ: 1年
        'detection_details': 90,    # 検出詳細: 3ヶ月
        'original_images': 90,      # 元画像: 3ヶ月
        'annotated_images': 30,     # 注釈画像: 1ヶ月
        'daily_summaries': 1095,    # 日次統計: 3年
        'hourly_summaries': 365,    # 時間別統計: 1年
        'system_logs': 180,         # システムログ: 6ヶ月
        'error_logs': 365,          # エラーログ: 1年
        'temp_files': 1,            # 一時ファイル: 1日
        'backup_daily': 30,         # 日次バックアップ: 1ヶ月
        'backup_weekly': 365        # 週次バックアップ: 1年
    }
    
    # 重要度別保持ポリシー
    IMPORTANCE_LEVELS = {
        'critical': 1095,   # 3年（統計・設定データ）
        'high': 365,        # 1年（検出ログ・エラーログ）
        'medium': 90,       # 3ヶ月（画像データ）
        'low': 30,          # 1ヶ月（一時データ）
        'temp': 1           # 1日（処理中データ）
    }
    
    @classmethod
    def get_retention_period(cls, data_type: str) -> int:
        """データ種別の保持期間取得
        
        Args:
            data_type: データ種別
            
        Returns:
            保持期間（日数）
        """
        return cls.RETENTION_PERIODS.get(data_type, 30)  # デフォルト30日
    
    @classmethod
    def is_expired(cls, file_path: str, data_type: str) -> bool:
        """ファイル期限切れ判定
        
        Args:
            file_path: ファイルパス
            data_type: データ種別
            
        Returns:
            期限切れかどうか
        """
        if not os.path.exists(file_path):
            return True
            
        # ファイル作成日時取得
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        retention_period = cls.get_retention_period(data_type)
        expiry_date = file_mtime + timedelta(days=retention_period)
        
        return datetime.now() > expiry_date

class DataLifecycleManager:
    """データライフサイクル管理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.retention_policy = DataRetentionPolicy()
        self.data_dirs = self._get_data_directories()
        
    def _get_data_directories(self) -> Dict[str, str]:
        """データディレクトリマッピング取得"""
        base_dir = self.config.get('data_base_dir', './data')
        
        return {
            'detection_logs': f"{base_dir}/raw/detection_logs",
            'detection_details': f"{base_dir}/raw/detection_details",
            'original_images': f"{base_dir}/raw/images/original",
            'annotated_images': f"{base_dir}/raw/images/annotated",
            'daily_summaries': f"{base_dir}/processed/daily_summaries",
            'hourly_summaries': f"{base_dir}/processed/hourly_summaries",
            'system_logs': f"{base_dir}/../logs/system",
            'error_logs': f"{base_dir}/../logs/error",
            'temp_files': f"{base_dir}/../temp",
            'backup_daily': f"{base_dir}/../backup/daily",
            'backup_weekly': f"{base_dir}/../backup/weekly"
        }
    
    def cleanup_expired_data(self) -> Dict[str, Any]:
        """期限切れデータクリーンアップ
        
        Returns:
            クリーンアップ結果
        """
        cleanup_result = {
            'start_time': datetime.now(),
            'total_files_checked': 0,
            'total_files_deleted': 0,
            'total_space_freed_mb': 0,
            'errors': [],
            'summary_by_type': {}
        }
        
        for data_type, directory in self.data_dirs.items():
            if not os.path.exists(directory):
                continue
                
            type_result = self._cleanup_directory(directory, data_type)
            cleanup_result['summary_by_type'][data_type] = type_result
            
            cleanup_result['total_files_checked'] += type_result['files_checked']
            cleanup_result['total_files_deleted'] += type_result['files_deleted']
            cleanup_result['total_space_freed_mb'] += type_result['space_freed_mb']
            cleanup_result['errors'].extend(type_result['errors'])
        
        cleanup_result['end_time'] = datetime.now()
        cleanup_result['duration_seconds'] = (
            cleanup_result['end_time'] - cleanup_result['start_time']
        ).total_seconds()
        
        # クリーンアップログ出力
        self._log_cleanup_result(cleanup_result)
        
        return cleanup_result
    
    def _cleanup_directory(self, directory: str, data_type: str) -> Dict[str, Any]:
        """ディレクトリ内クリーンアップ"""
        result = {
            'files_checked': 0,
            'files_deleted': 0,
            'space_freed_mb': 0,
            'errors': []
        }
        
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if not os.path.isfile(file_path):
                    continue
                
                result['files_checked'] += 1
                
                # 期限切れ判定
                if self.retention_policy.is_expired(file_path, data_type):
                    try:
                        # ファイルサイズ取得（削除前）
                        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                        
                        # ファイル削除
                        os.remove(file_path)
                        
                        result['files_deleted'] += 1
                        result['space_freed_mb'] += file_size_mb
                        
                        logging.info(f"Deleted expired file: {file_path}")
                        
                    except Exception as e:
                        error_msg = f"Failed to delete {file_path}: {str(e)}"
                        result['errors'].append(error_msg)
                        logging.error(error_msg)
                        
        except Exception as e:
            error_msg = f"Failed to process directory {directory}: {str(e)}"
            result['errors'].append(error_msg)
            logging.error(error_msg)
        
        return result
    
    def _log_cleanup_result(self, result: Dict[str, Any]) -> None:
        """クリーンアップ結果ログ出力"""
        logging.info("Data cleanup completed:")
        logging.info(f"  Duration: {result['duration_seconds']:.1f} seconds")
        logging.info(f"  Files checked: {result['total_files_checked']}")
        logging.info(f"  Files deleted: {result['total_files_deleted']}")
        logging.info(f"  Space freed: {result['total_space_freed_mb']:.1f} MB")
        
        if result['errors']:
            logging.warning(f"  Errors encountered: {len(result['errors'])}")
            
        # 種別別結果ログ
        for data_type, type_result in result['summary_by_type'].items():
            if type_result['files_deleted'] > 0:
                logging.info(
                    f"  {data_type}: {type_result['files_deleted']} files, "
                    f"{type_result['space_freed_mb']:.1f} MB"
                )
```

### 6.2 バックアップ・復旧

#### 6.2.1 バックアップ戦略
```python
class BackupManager:
    """バックアップ管理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backup_enabled = config.get('backup_enabled', True)
        self.compression_enabled = config.get('compression_enabled', True)
        self.encryption_enabled = config.get('encryption_enabled', False)
        
    def create_daily_backup(self, target_date: date = None) -> Dict[str, Any]:
        """日次バックアップ作成
        
        Args:
            target_date: バックアップ対象日付（Noneの場合は前日）
            
        Returns:
            バックアップ結果
        """
        if not self.backup_enabled:
            return {'status': 'disabled', 'message': 'Backup is disabled'}
        
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        backup_result = {
            'target_date': target_date,
            'start_time': datetime.now(),
            'status': 'success',
            'backup_filepath': '',
            'original_size_mb': 0,
            'compressed_size_mb': 0,
            'compression_ratio': 0,
            'files_included': [],
            'errors': []
        }
        
        try:
            # バックアップ対象ファイル収集
            target_files = self._collect_backup_files(target_date)
            backup_result['files_included'] = target_files
            
            if not target_files:
                backup_result['status'] = 'no_data'
                backup_result['message'] = 'No files to backup'
                return backup_result
            
            # バックアップファイル名生成
            backup_filename = f"backup_{target_date.strftime('%Y%m%d')}.tar.gz"
            backup_filepath = os.path.join(
                self.config.get('backup_dir', './backup/daily'),
                backup_filename
            )
            backup_result['backup_filepath'] = backup_filepath
            
            # バックアップディレクトリ作成
            os.makedirs(os.path.dirname(backup_filepath), exist_ok=True)
            
            # 元サイズ計算
            total_size = sum(os.path.getsize(f) for f in target_files if os.path.exists(f))
            backup_result['original_size_mb'] = total_size / (1024 * 1024)
            
            # tar.gz形式でバックアップ作成
            self._create_tar_backup(target_files, backup_filepath)
            
            # 圧縮サイズ取得
            compressed_size = os.path.getsize(backup_filepath)
            backup_result['compressed_size_mb'] = compressed_size / (1024 * 1024)
            backup_result['compression_ratio'] = (
                1 - compressed_size / total_size if total_size > 0 else 0
            )
            
            # 暗号化（有効な場合）
            if self.encryption_enabled:
                encrypted_filepath = self._encrypt_backup(backup_filepath)
                backup_result['backup_filepath'] = encrypted_filepath
            
            backup_result['end_time'] = datetime.now()
            backup_result['duration_seconds'] = (
                backup_result['end_time'] - backup_result['start_time']
            ).total_seconds()
            
            logging.info(f"Daily backup created: {backup_filepath}")
            logging.info(f"  Files: {len(target_files)}")
            logging.info(f"  Original size: {backup_result['original_size_mb']:.1f} MB")
            logging.info(f"  Compressed size: {backup_result['compressed_size_mb']:.1f} MB")
            logging.info(f"  Compression ratio: {backup_result['compression_ratio']:.1%}")
            
        except Exception as e:
            backup_result['status'] = 'error'
            backup_result['errors'].append(str(e))
            logging.error(f"Daily backup failed: {str(e)}")
        
        return backup_result
    
    def _collect_backup_files(self, target_date: date) -> List[str]:
        """バックアップ対象ファイル収集"""
        target_files = []
        date_str = target_date.strftime('%Y%m%d')
        
        # 検出ログファイル
        detection_log_path = f"./data/raw/detection_logs/detection_{date_str}.csv"
        if os.path.exists(detection_log_path):
            target_files.append(detection_log_path)
        
        # 検出詳細ファイル
        detail_log_path = f"./data/raw/detection_details/details_{date_str}.csv"
        if os.path.exists(detail_log_path):
            target_files.append(detail_log_path)
        
        # 統計ファイル
        daily_summary_path = f"./data/processed/daily_summaries/daily_summary_{date_str}.csv"
        if os.path.exists(daily_summary_path):
            target_files.append(daily_summary_path)
        
        hourly_summary_path = f"./data/processed/hourly_summaries/hourly_summary_{date_str}.csv"
        if os.path.exists(hourly_summary_path):
            target_files.append(hourly_summary_path)
        
        # 当日の画像ファイル（重要な検出のみ）
        image_dirs = [
            "./data/raw/images/original",
            "./data/raw/images/annotated"
        ]
        
        for image_dir in image_dirs:
            if os.path.exists(image_dir):
                for filename in os.listdir(image_dir):
                    if date_str in filename:
                        target_files.append(os.path.join(image_dir, filename))
        
        # 可視化ファイル
        viz_files = [
            f"./data/visualizations/charts/activity_chart_{date_str}.png",
            f"./data/visualizations/charts/movement_heatmap_{date_str}.png"
        ]
        
        for viz_file in viz_files:
            if os.path.exists(viz_file):
                target_files.append(viz_file)
        
        return target_files
    
    def _create_tar_backup(self, files: List[str], output_path: str) -> None:
        """tar.gz形式バックアップ作成"""
        import tarfile
        
        with tarfile.open(output_path, 'w:gz') as tar:
            for file_path in files:
                if os.path.exists(file_path):
                    # 相対パスでアーカイブに追加
                    arcname = os.path.relpath(file_path)
                    tar.add(file_path, arcname=arcname)
    
    def restore_backup(self, backup_filepath: str, 
                      restore_dir: str = None) -> Dict[str, Any]:
        """バックアップ復旧
        
        Args:
            backup_filepath: バックアップファイルパス
            restore_dir: 復旧先ディレクトリ（Noneの場合は元の場所）
            
        Returns:
            復旧結果
        """
        restore_result = {
            'backup_filepath': backup_filepath,
            'restore_dir': restore_dir,
            'start_time': datetime.now(),
            'status': 'success',
            'files_restored': [],
            'errors': []
        }
        
        try:
            if not os.path.exists(backup_filepath):
                raise FileNotFoundError(f"Backup file not found: {backup_filepath}")
            
            # 暗号化されている場合は復号化
            if backup_filepath.endswith('.enc'):
                backup_filepath = self._decrypt_backup(backup_filepath)
            
            # tar.gz展開
            import tarfile
            
            with tarfile.open(backup_filepath, 'r:gz') as tar:
                if restore_dir:
                    # 指定ディレクトリに復旧
                    tar.extractall(path=restore_dir)
                    restore_result['files_restored'] = tar.getnames()
                else:
                    # 元の場所に復旧
                    tar.extractall()
                    restore_result['files_restored'] = tar.getnames()
            
            restore_result['end_time'] = datetime.now()
            restore_result['duration_seconds'] = (
                restore_result['end_time'] - restore_result['start_time']
            ).total_seconds()
            
            logging.info(f"Backup restored successfully: {backup_filepath}")
            logging.info(f"  Files restored: {len(restore_result['files_restored'])}")
            
        except Exception as e:
            restore_result['status'] = 'error'
            restore_result['errors'].append(str(e))
            logging.error(f"Backup restore failed: {str(e)}")
        
        return restore_result
```

---

*文書バージョン: 1.0*  
*最終更新日: 2025-07-25*  
*承認者: 開発チーム*