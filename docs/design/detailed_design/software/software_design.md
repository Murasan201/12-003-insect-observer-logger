# ソフトウェア設計書

**文書番号**: 12-002-SW-001  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: ソフトウェア設計書  
**バージョン**: 1.0  
**作成日**: 2025-07-25  
**作成者**: 開発チーム  

---

## 1. 文書概要

### 1.1 目的
本文書は昆虫自動観察システムのソフトウェア構成、各モジュールの詳細設計、インターフェース仕様、および実装方針を定義する。

### 1.2 適用範囲
- ソフトウェアアーキテクチャ設計
- モジュール詳細設計
- データフロー設計
- API・インターフェース仕様
- エラーハンドリング設計
- 性能・品質要件

### 1.3 関連文書
- システムアーキテクチャ設計書（system_architecture_design.md）
- ハードウェア設計書（hardware_design.md）
- 要件定義書（12-002）

---

## 2. ソフトウェアアーキテクチャ

### 2.1 アーキテクチャ概要図

```
┌─────────────────────────────────────────────────────────────────┐
│                  昆虫観察ソフトウェアシステム                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │                 │  │                 │  │                 │  │
│  │ プレゼンテーション層│  │  ビジネスロジック層│  │   データアクセス層│  │
│  │ Presentation    │  │  Business Logic │  │  Data Access    │  │
│  │     Layer       │  │     Layer       │  │     Layer       │  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │   コマンド   │ │  │ │    統合     │ │  │ │   CSV       │ │  │
│  │ │ ライン      │ │  │ │   制御      │ │  │ │ ファイル     │ │  │
│  │ │ インターフェース│ │  │ │  (main.py) │ │  │ │   I/O       │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  │                 │  │        │        │  │                 │  │
│  │ ┌─────────────┐ │  │        ▼        │  │ ┌─────────────┐ │  │
│  │ │   ログ      │ │◄─┼─┌─────────────┐ │  │ │   画像      │ │  │
│  │ │  出力       │ │  │ │   検出      │ │──┼─│ ファイル     │ │  │
│  │ │ インターフェース│ │  │ │  制御      │ │  │ │   I/O       │ │  │
│  │ └─────────────┘ │  │ │(detector.py)│ │  │ └─────────────┘ │  │
│  │                 │  │ └─────────────┘ │  │                 │  │
│  │ ┌─────────────┐ │  │        │        │  │ ┌─────────────┐ │  │
│  │ │   グラフ     │ │◄─┘        ▼        │  │ │  設定       │ │  │
│  │ │  可視化      │ │    ┌─────────────┐ │  │ │ ファイル     │ │  │
│  │ │ インターフェース│ │    │   活動量    │ │──┼─│   I/O       │ │  │
│  │ └─────────────┘ │    │   算出      │ │  │ └─────────────┘ │  │
│  │                 │    │(calculator. │ │  │                 │  │
│  └─────────────────┘    │    py)      │ │  └─────────────────┘  │
│                         └─────────────┘ │                       │
│                                         │                       │
├─────────────────────────────────────────┴───────────────────────┤
│                     インフラストラクチャ層                        │
│                   Infrastructure Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │                 │  │                 │  │                 │  │
│  │ ハードウェア制御  │  │   外部ライブラリ  │  │  システム       │  │
│  │  Hardware       │  │   External      │  │  Services       │  │
│  │  Controller     │  │   Libraries     │  │                 │  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │  カメラ     │ │  │ │ ultralytics │ │  │ │   ログ      │ │  │
│  │ │  制御       │ │  │ │ (YOLOv8)    │ │  │ │  システム    │ │  │
│  │ │(picamera2)  │ │  │ └─────────────┘ │  │ │ (logging)   │ │  │
│  │ └─────────────┘ │  │                 │  │ └─────────────┘ │  │
│  │                 │  │ ┌─────────────┐ │  │                 │  │
│  │ ┌─────────────┐ │  │ │   OpenCV    │ │  │ ┌─────────────┐ │  │
│  │ │  GPIO       │ │  │ │ (cv2)       │ │  │ │   OS        │ │  │
│  │ │  制御       │ │  │ └─────────────┘ │  │ │ サービス     │ │  │
│  │ │(RPi.GPIO)   │ │  │                 │  │ │ (datetime)  │ │  │
│  │ └─────────────┘ │  │ ┌─────────────┐ │  │ └─────────────┘ │  │
│  │                 │  │ │ matplotlib  │ │  │                 │  │
│  │                 │  │ │ (グラフ生成) │ │  │                 │  │
│  │                 │  │ └─────────────┘ │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 層別責務定義

| 層名 | 責務 | 主要コンポーネント |
|------|------|-------------------|
| **プレゼンテーション層** | ユーザーインターフェース、出力制御 | CLI、ログ出力、グラフ表示 |
| **ビジネスロジック層** | アプリケーション制御、業務処理 | 統合制御、検出処理、活動量算出 |
| **データアクセス層** | データ永続化、ファイルI/O | CSV操作、画像保存、設定管理 |
| **インフラストラクチャ層** | システムリソース、外部連携 | ハードウェア制御、ライブラリ |

---

## 3. モジュール詳細設計

### 3.1 統合制御モジュール (main.py)

#### 3.1.1 モジュール概要
```
モジュール名: main.py
役割: システム全体の統合制御とライフサイクル管理
責務:
├── システム初期化・終了処理
├── 定期実行スケジューリング
├── 各モジュール間の連携制御
├── エラーハンドリングと復旧処理
└── システム状態監視
```

#### 3.1.2 クラス設計
```python
class InsectObserverSystem:
    """昆虫観察システムのメインコントローラー"""
    
    def __init__(self, config_path: str):
        """システム初期化
        
        Args:
            config_path (str): 設定ファイルパス
        """
        self.config = None
        self.detector = None
        self.calculator = None
        self.hardware_controller = None
        self.logger = None
        self.running = False
        
    def initialize_system(self) -> bool:
        """システム初期化処理
        
        Returns:
            bool: 初期化成功可否
        """
        
    def run_main_loop(self) -> None:
        """メインループ実行"""
        
    def perform_detection_cycle(self) -> Dict[str, Any]:
        """検出サイクル実行
        
        Returns:
            Dict[str, Any]: 検出結果
        """
        
    def perform_daily_analysis(self) -> None:
        """日次分析処理実行"""
        
    def shutdown_system(self) -> None:
        """システム終了処理"""
        
    def handle_error(self, error: Exception, context: str) -> None:
        """エラーハンドリング
        
        Args:
            error (Exception): 発生したエラー
            context (str): エラー発生コンテキスト
        """
```

#### 3.1.3 処理フロー
```
main.py 処理フロー
├── 1. システム初期化
│   ├── 設定ファイル読み込み
│   ├── ログシステム初期化
│   ├── ハードウェア初期化
│   ├── 検出モジュール初期化
│   └── 活動量算出モジュール初期化
├── 2. メインループ実行
│   ├── タイマー設定 (60秒間隔)
│   ├── 検出サイクル実行
│   │   ├── LED点灯制御
│   │   ├── 画像撮影
│   │   ├── 昆虫検出
│   │   ├── 結果ログ記録
│   │   └── LED消灯制御
│   ├── 日次処理判定
│   └── エラー監視・復旧
├── 3. 日次分析処理
│   ├── 1日分データ読み込み
│   ├── 活動量算出実行
│   ├── グラフ生成
│   └── 統計レポート作成
└── 4. システム終了処理
    ├── リソース解放
    ├── 最終ログ出力
    └── ハードウェア安全停止
```

### 3.2 検出制御モジュール (insect_detector.py)

#### 3.1.1 モジュール概要
```
モジュール名: insect_detector.py  
役割: 昆虫検出処理の実行と制御
責務:
├── カメラ制御・画像撮影
├── IR LED照明制御
├── YOLOv8モデル推論実行
├── 検出結果の処理・出力
└── 検出品質の評価
```

#### 3.2.2 クラス設計
```python
class InsectDetector:
    """昆虫検出処理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """検出器初期化
        
        Args:
            config (Dict[str, Any]): 設定パラメータ
        """
        self.config = config
        self.model = None
        self.camera = None
        self.hardware_controller = None
        self.detection_count = 0
        
    def initialize_model(self, model_path: str) -> bool:
        """YOLOv8モデル初期化
        
        Args:
            model_path (str): モデルファイルパス
            
        Returns:
            bool: 初期化成功可否
        """
        
    def capture_image(self) -> Optional[np.ndarray]:
        """画像撮影実行
        
        Returns:
            Optional[np.ndarray]: 撮影画像 (BGR形式)
        """
        
    def detect_insects(self, image: np.ndarray) -> List[DetectionResult]:
        """昆虫検出実行
        
        Args:
            image (np.ndarray): 入力画像
            
        Returns:
            List[DetectionResult]: 検出結果リスト
        """
        
    def process_detection_results(self, 
                                results: List[DetectionResult],
                                image: np.ndarray) -> Dict[str, Any]:
        """検出結果処理
        
        Args:
            results (List[DetectionResult]): 検出結果
            image (np.ndarray): 元画像
            
        Returns:
            Dict[str, Any]: 処理済み結果
        """
        
    def save_detection_image(self, image: np.ndarray, 
                           results: List[DetectionResult],
                           timestamp: str) -> str:
        """検出画像保存
        
        Args:
            image (np.ndarray): 元画像
            results (List[DetectionResult]): 検出結果
            timestamp (str): タイムスタンプ
            
        Returns:
            str: 保存ファイルパス
        """

@dataclass
class DetectionResult:
    """検出結果データクラス"""
    x_center: float
    y_center: float
    width: float
    height: float
    confidence: float
    class_id: int
    timestamp: str
```

#### 3.2.3 検出処理アルゴリズム
```
検出処理アルゴリズム
├── 1. 前処理
│   ├── IR LED点灯 (850nm, PWM制御)
│   ├── カメラ露出調整 (自動)
│   ├── 画像撮影 (1920×1080)
│   └── IR LED消灯
├── 2. 画像前処理
│   ├── 解像度正規化 (640×640)
│   ├── 色空間変換 (BGR→RGB)
│   ├── 正規化 (0-1スケール)
│   └── バッチ次元追加
├── 3. 推論実行
│   ├── YOLOv8モデル推論
│   ├── 信頼度閾値フィルタ (>0.5)
│   ├── NMS (Non-Maximum Suppression)
│   └── 座標変換 (正規化→ピクセル)
├── 4. 後処理
│   ├── 検出結果検証
│   ├── バウンディングボックス描画
│   ├── 検出画像保存 (PNG形式)
│   └── メタデータ記録
└── 5. 結果出力
    ├── CSV形式ログ出力
    ├── 統計情報更新
    └── エラー状態確認
```

### 3.3 活動量算出モジュール (activity_calculator.py)

#### 3.3.1 モジュール概要
```
モジュール名: activity_calculator.py
役割: 昆虫活動量の算出と可視化
責務:
├── 検出データの時系列分析
├── 移動距離・活動量の算出
├── 統計的指標の計算
├── グラフ・チャートの生成
└── 分析レポートの作成
```

#### 3.3.2 クラス設計
```python
class ActivityCalculator:
    """活動量算出クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """算出器初期化
        
        Args:
            config (Dict[str, Any]): 設定パラメータ
        """
        self.config = config
        self.data_processor = None
        self.visualizer = None
        
    def load_detection_data(self, date: str) -> pd.DataFrame:
        """検出データ読み込み
        
        Args:
            date (str): 対象日付 (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: 検出データ
        """
        
    def calculate_movement_distance(self, 
                                  data: pd.DataFrame) -> List[float]:
        """移動距離算出
        
        Args:
            data (pd.DataFrame): 時系列検出データ
            
        Returns:
            List[float]: 時間別移動距離
        """
        
    def calculate_activity_metrics(self, 
                                 data: pd.DataFrame) -> ActivityMetrics:
        """活動量指標算出
        
        Args:
            data (pd.DataFrame): 検出データ
            
        Returns:
            ActivityMetrics: 活動量指標
        """
        
    def generate_activity_chart(self, 
                              metrics: ActivityMetrics,
                              output_path: str) -> str:
        """活動量チャート生成
        
        Args:
            metrics (ActivityMetrics): 活動量指標
            output_path (str): 出力パス
            
        Returns:
            str: 生成ファイルパス
        """
        
    def generate_movement_heatmap(self, 
                                data: pd.DataFrame,
                                output_path: str) -> str:
        """移動軌跡ヒートマップ生成
        
        Args:
            data (pd.DataFrame): 位置データ
            output_path (str): 出力パス
            
        Returns:
            str: 生成ファイルパス
        """

@dataclass  
class ActivityMetrics:
    """活動量指標データクラス"""
    total_detections: int
    total_distance: float
    avg_activity_per_hour: float
    peak_activity_time: str
    activity_duration: float
    movement_patterns: List[str]
```

#### 3.3.3 算出アルゴリズム
```
活動量算出アルゴリズム
├── 1. データ前処理
│   ├── CSV データ読み込み
│   ├── 欠損値・異常値処理
│   ├── 時系列データソート
│   └── 検出フラグフィルタリング
├── 2. 移動距離算出
│   ├── 連続検出点間距離計算
│   │   └── distance = √((x₂-x₁)² + (y₂-y₁)²)
│   ├── 閾値による外れ値除去
│   ├── 時間窓別集計 (1時間単位)
│   └── 累積距離算出
├── 3. 活動量指標算出
│   ├── 総検出回数
│   ├── 総移動距離
│   ├── 時間別平均活動量
│   ├── ピーク活動時間帯
│   ├── 活動継続時間
│   └── 移動パターン分類
├── 4. 統計分析
│   ├── 基本統計量 (平均・分散・四分位)
│   ├── 活動リズム分析
│   ├── 移動傾向分析
│   └── 異常活動検出
└── 5. 結果出力
    ├── 統計サマリーCSV出力
    ├── 時系列グラフ生成
    ├── ヒートマップ生成
    └── 分析レポート作成
```

#### 3.3.4 アルゴリズム解説（書籍向け補足）

昆虫の活動量算出は、複雑に見える数式を使いますが、実際は身近な計算の組み合わせです。プログラミング学習者向けに、概念から実装まで段階的に解説します。

##### 概念説明（文系読者向け）

**活動量とは何か**
昆虫の「活動量」とは、人間の「1日の歩数」や「移動距離」と同じ概念です。昆虫がどのくらい動き回ったかを数値で表現します。

**測定の仕組み**
1. **位置の記録**: 1分ごとに昆虫の位置を撮影・記録
2. **移動の計算**: 前の位置と今の位置の距離を測定
3. **1日の合計**: すべての移動距離を足し算

**身近な例**
- スマートフォンの歩数計が歩数と移動距離を計算するのと同じ
- カーナビが「目的地まで500m」と表示するときの距離計算
- 地図上で定規を使って2点間の距離を測るのと同じ原理

##### 数式の導入と意味

**なぜ数式が必要か**
コンピューターは画面上の位置を「座標」で管理します。昆虫の位置も (x, y) という数値の組み合わせとして記録されます。

**2点間の距離を求める公式（ピタゴラスの定理）**
```
距離 = √((x₂-x₁)² + (y₂-y₁)²)
```

**数式の意味**
- `x₁, y₁`: 前回の昆虫の位置
- `x₂, y₂`: 今回の昆虫の位置
- `√`: ルート（平方根）
- この公式で「直線距離」が計算できる

**具体例**
```
前回の位置: (100, 200)
今回の位置: (130, 260)

距離 = √((130-100)² + (260-200)²)
     = √(30² + 60²)
     = √(900 + 3600)
     = √4500
     = 67.1 ピクセル
```

##### 実装コードとの対応関係

**Pythonでの実装**
```python
def calculate_movement_distance(self, detection_data: pd.DataFrame) -> List[float]:
    """移動距離算出実装"""
    
    # 1. 前回の位置を取得（1行上のデータ）
    detected_data['prev_x'] = detected_data['x_center'].shift(1)
    detected_data['prev_y'] = detected_data['y_center'].shift(1)
    
    # 2. ピタゴラスの定理で距離を計算
    detected_data['movement_distance'] = np.sqrt(
        (detected_data['x_center'] - detected_data['prev_x'])**2 +
        (detected_data['y_center'] - detected_data['prev_y'])**2
    )
    
    # 3. 異常値を除去（画面サイズ以上の移動は除外）
    screen_diagonal = np.sqrt(1920**2 + 1080**2)  # 画面対角線
    detected_data = detected_data[
        detected_data['movement_distance'] < screen_diagonal * 0.5
    ]
    
    return detected_data['movement_distance'].tolist()
```

**コードの流れ**
1. **shift(1)**: 1行前のデータを取得（前回の位置）
2. **np.sqrt()**: ルート計算（ピタゴラスの定理）
3. **異常値チェック**: 現実的でない大きな移動を除外

##### 処理結果の活用

**得られるデータ**
```python
# 1日分の移動距離リスト（例）
movement_distances = [0, 67.1, 23.4, 89.2, 12.8, ...]

# 統計情報の計算
total_distance = sum(movement_distances)      # 総移動距離
average_distance = np.mean(movement_distances) # 平均移動距離
max_distance = max(movement_distances)        # 最大移動距離
```

**可視化での活用**
- 時間別の活動量をグラフ化
- 移動パターンをヒートマップで表示
- 昆虫の行動特性を数値で分析

**実用例**
```
結果: 「この昆虫は夜10時頃が最も活発で、1日で画面上を500ピクセル分移動しました」
→ プログラムが自動的に昆虫の生活パターンを発見
```

この算出アルゴリズムにより、プログラミング初心者でも昆虫の行動を定量的に分析するシステムを構築できます。

### 3.4 ハードウェア制御モジュール (hardware_controller.py)

#### 3.4.1 モジュール概要
```
モジュール名: hardware_controller.py
役割: ハードウェアデバイスの制御
責務:
├── カメラデバイス制御
├── GPIO・IR LED制御
├── ハードウェア状態監視
├── デバイスエラーハンドリング
└── リソース管理
```

#### 3.4.2 クラス設計
```python
class HardwareController:
    """ハードウェア制御クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """制御器初期化
        
        Args:
            config (Dict[str, Any]): ハードウェア設定
        """
        self.config = config
        self.camera = None
        self.gpio_initialized = False
        self.led_pwm = None
        
    def initialize_camera(self) -> bool:
        """カメラ初期化
        
        Returns:
            bool: 初期化成功可否
        """
        
    def initialize_gpio(self) -> bool:
        """GPIO初期化
        
        Returns:
            bool: 初期化成功可否
        """
        
    def capture_image(self, 
                     resolution: Tuple[int, int] = (1920, 1080),
                     format: str = 'bgr') -> Optional[np.ndarray]:
        """画像撮影
        
        Args:
            resolution (Tuple[int, int]): 解像度
            format (str): 画像フォーマット
            
        Returns:
            Optional[np.ndarray]: 撮影画像
        """
        
    def control_ir_led(self, brightness: float) -> None:
        """IR LED制御
        
        Args:
            brightness (float): 明度 (0.0-1.0)
        """
        
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態取得
        
        Returns:
            Dict[str, Any]: システム状態情報
        """
        
    def cleanup_resources(self) -> None:
        """リソース解放"""

class CameraController:
    """カメラ専用制御クラス"""
    
    def __init__(self):
        self.picam2 = None
        self.config = None
        
    def setup_camera(self, config: Dict[str, Any]) -> bool:
        """カメラセットアップ"""
        
    def capture_still(self) -> np.ndarray:
        """静止画撮影"""
        
    def adjust_exposure(self, scene_brightness: float) -> None:
        """露出調整"""

class GPIOController:
    """GPIO専用制御クラス"""
    
    def __init__(self):
        self.pwm_instances = {}
        
    def setup_pwm(self, pin: int, frequency: int) -> bool:
        """PWM設定"""
        
    def set_pwm_duty_cycle(self, pin: int, duty_cycle: float) -> None:
        """PWMデューティサイクル設定"""
        
    def cleanup_gpio(self) -> None:
        """GPIO清掃"""
```

### 3.5 設定管理モジュール (config.py)

#### 3.5.1 モジュール概要
```
モジュール名: config.py
役割: システム設定の管理
責務:
├── 設定ファイル読み込み・保存
├── 設定値の検証・デフォルト値設定
├── 環境別設定管理
├── 動的設定変更対応
└── 設定変更履歴管理
```

#### 3.5.2 設定項目定義
```python
@dataclass
class SystemConfig:
    """システム設定クラス"""
    
    # システム基本設定
    detection_interval: int = 60  # 検出間隔（秒）
    log_level: str = "INFO"
    data_retention_days: int = 30
    
    # ハードウェア設定
    camera_resolution: Tuple[int, int] = (1920, 1080)
    camera_fps: int = 30
    ir_led_pin: int = 18
    ir_led_brightness: float = 0.8
    
    # 検出設定
    model_path: str = "./weights/beetle_detection.pt"
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    max_detections: int = 10
    
    # データ設定
    data_dir: str = "./data"
    log_dir: str = "./logs"
    output_dir: str = "./output"
    
    # 活動量算出設定
    movement_threshold: float = 5.0  # ピクセル
    time_window: int = 3600  # 1時間（秒）
    outlier_threshold: float = 3.0  # 標準偏差

class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_path: str = "./config/system_config.json"):
        self.config_path = config_path
        self.config = SystemConfig()
        
    def load_config(self) -> SystemConfig:
        """設定ファイル読み込み"""
        
    def save_config(self, config: SystemConfig) -> None:
        """設定ファイル保存"""
        
    def validate_config(self, config: SystemConfig) -> List[str]:
        """設定値検証"""
        
    def get_env_config(self) -> Dict[str, Any]:
        """環境変数設定取得"""
```

---

## 4. データフロー設計

### 4.1 データフロー図

```
データフロー全体図

[カメラ撮影] 
      │
      ▼ (np.ndarray)
[画像前処理]
      │
      ▼ (processed_image)
[YOLOv8推論]
      │
      ▼ (DetectionResult[])
[検出結果処理] ───┐
      │          │
      ▼          ▼ (detection_image)
[CSVログ記録]  [画像保存]
      │          │
      ▼          ▼
[ログファイル]  [PNG画像]
      │
      ▼ (daily_data)
[データ読み込み]
      │
      ▼ (pd.DataFrame)
[活動量算出]
      │
      ▼ (ActivityMetrics)
[グラフ生成] ───┐
      │        │
      ▼        ▼ (chart_image)
[統計CSV]    [PNG グラフ]
```

### 4.2 データ変換仕様

#### 4.2.1 画像データ変換
```python
# 画像データ変換パイプライン
def image_processing_pipeline(raw_image: np.ndarray) -> np.ndarray:
    """画像処理パイプライン
    
    Args:
        raw_image: カメラからの生画像 (H×W×3, BGR)
        
    Returns:
        processed_image: 処理済み画像 (640×640×3, RGB, 0-1正規化)
    """
    # 1. 色空間変換 BGR → RGB
    rgb_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
    
    # 2. リサイズ (アスペクト比保持)
    resized_image = letterbox_resize(rgb_image, (640, 640))
    
    # 3. 正規化 (0-255 → 0-1)
    normalized_image = resized_image.astype(np.float32) / 255.0
    
    return normalized_image

def letterbox_resize(image: np.ndarray, 
                    target_size: Tuple[int, int]) -> np.ndarray:
    """アスペクト比保持リサイズ"""
    # アスペクト比計算・パディング処理
    pass
```

#### 4.2.2 検出結果変換
```python
def convert_yolo_output(predictions: torch.Tensor, 
                       image_shape: Tuple[int, int]) -> List[DetectionResult]:
    """YOLO出力を検出結果に変換
    
    Args:
        predictions: YOLO推論結果テンソル
        image_shape: 元画像サイズ (H, W)
        
    Returns:
        検出結果リスト
    """
    results = []
    
    for pred in predictions:
        # 座標変換 (正規化 → ピクセル)
        x_center = pred[0] * image_shape[1]
        y_center = pred[1] * image_shape[0]
        width = pred[2] * image_shape[1]
        height = pred[3] * image_shape[0]
        confidence = pred[4]
        class_id = int(pred[5])
        
        result = DetectionResult(
            x_center=x_center,
            y_center=y_center,
            width=width,
            height=height,
            confidence=confidence,
            class_id=class_id,
            timestamp=datetime.now().isoformat()
        )
        results.append(result)
    
    return results
```

### 4.3 データ検証・品質管理

#### 4.3.1 入力データ検証
```python
class DataValidator:
    """データ検証クラス"""
    
    @staticmethod
    def validate_image(image: np.ndarray) -> bool:
        """画像データ検証"""
        if image is None:
            return False
        if len(image.shape) != 3:
            return False
        if image.shape[2] != 3:  # BGRチャンネル
            return False
        if image.dtype != np.uint8:
            return False
        return True
    
    @staticmethod
    def validate_detection_result(result: DetectionResult) -> bool:
        """検出結果検証"""
        if result.confidence < 0.0 or result.confidence > 1.0:
            return False
        if result.x_center < 0 or result.y_center < 0:
            return False
        if result.width <= 0 or result.height <= 0:
            return False
        return True
    
    @staticmethod
    def validate_csv_data(df: pd.DataFrame) -> List[str]:
        """CSVデータ検証"""
        errors = []
        
        required_columns = ['timestamp', 'x_center', 'y_center', 
                          'confidence', 'detected_flag']
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # データ型チェック
        if not pd.api.types.is_numeric_dtype(df['x_center']):
            errors.append("x_center must be numeric")
        
        # 範囲チェック
        if (df['confidence'] < 0).any() or (df['confidence'] > 1).any():
            errors.append("confidence must be in range [0, 1]")
        
        return errors
```

---

## 5. API・インターフェース設計

### 5.1 モジュール間API

#### 5.1.1 検出器API
```python
class DetectorAPI:
    """検出器向けAPI"""
    
    def detect_insects_async(self, 
                           callback: Callable[[List[DetectionResult]], None]
                          ) -> None:
        """非同期検出実行
        
        Args:
            callback: 結果受信コールバック関数
        """
        
    def get_detection_status(self) -> Dict[str, Any]:
        """検出状態取得
        
        Returns:
            検出器状態情報
        """
        
    def update_detection_config(self, config: Dict[str, Any]) -> bool:
        """検出設定更新
        
        Args:
            config: 新しい設定
            
        Returns:
            更新成功可否
        """
```

#### 5.1.2 活動量算出API
```python
class CalculatorAPI:
    """活動量算出器向けAPI"""
    
    def calculate_daily_activity(self, 
                               date: str,
                               callback: Callable[[ActivityMetrics], None]
                              ) -> None:
        """日次活動量算出
        
        Args:
            date: 対象日付
            callback: 結果受信コールバック
        """
        
    def generate_report(self, 
                       start_date: str,
                       end_date: str) -> str:
        """期間レポート生成
        
        Args:
            start_date: 開始日付
            end_date: 終了日付
            
        Returns:
            レポートファイルパス
        """
```

### 5.2 外部インターフェース

#### 5.2.1 コマンドラインインターフェース
```python
class CLIInterface:
    """コマンドライン制御インターフェース"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="昆虫自動観察システム"
        )
        self.setup_arguments()
    
    def setup_arguments(self) -> None:
        """引数設定"""
        self.parser.add_argument(
            '--config', '-c',
            type=str,
            default='./config/system_config.json',
            help='設定ファイルパス'
        )
        
        self.parser.add_argument(
            '--mode', '-m',
            choices=['continuous', 'single', 'analysis'],
            default='continuous',
            help='動作モード'
        )
        
        self.parser.add_argument(
            '--date', '-d',
            type=str,
            help='分析対象日付 (YYYY-MM-DD)'
        )
        
        self.parser.add_argument(
            '--log-level', '-l',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='ログレベル'
        )
    
    def parse_args(self) -> argparse.Namespace:
        """引数解析"""
        return self.parser.parse_args()

# 使用例
if __name__ == "__main__":
    # 連続動作モード
    python main.py --mode continuous --config ./config/system_config.json
    
    # 単発検出モード  
    python main.py --mode single --log-level DEBUG
    
    # 分析モード
    python main.py --mode analysis --date 2025-07-25
```

#### 5.2.2 設定ファイルインターフェース
```json
{
  "system": {
    "detection_interval": 60,
    "log_level": "INFO",
    "data_retention_days": 30
  },
  "hardware": {
    "camera": {
      "resolution": [1920, 1080],
      "fps": 30,
      "auto_exposure": true
    },
    "ir_led": {
      "pin": 18,
      "brightness": 0.8,
      "pwm_frequency": 1000
    }
  },
  "detection": {
    "model_path": "./weights/beetle_detection.pt",
    "confidence_threshold": 0.5,
    "nms_threshold": 0.4,
    "max_detections": 10
  },
  "data": {
    "base_dir": "./data",
    "log_dir": "./logs",
    "output_dir": "./output",
    "backup_enabled": true
  },
  "analysis": {
    "movement_threshold": 5.0,
    "time_window": 3600,
    "outlier_threshold": 3.0
  }
}
```

---

## 6. エラーハンドリング設計

### 6.1 エラー分類体系

```
エラー分類階層
├── SystemError (システムエラー)
│   ├── InitializationError (初期化エラー)
│   ├── ConfigurationError (設定エラー)
│   └── ResourceError (リソースエラー)
├── HardwareError (ハードウェアエラー)
│   ├── CameraError (カメラエラー)
│   ├── GPIOError (GPIO エラー)
│   └── LEDError (LED エラー)
├── DetectionError (検出エラー)
│   ├── ModelLoadError (モデル読み込みエラー)
│   ├── InferenceError (推論エラー)
│   └── PostProcessError (後処理エラー)
├── DataError (データエラー)
│   ├── FileIOError (ファイル I/O エラー)
│   ├── ValidationError (検証エラー)
│   └── FormatError (フォーマットエラー)
└── NetworkError (ネットワークエラー)
    ├── ConnectionError (接続エラー)
    └── TimeoutError (タイムアウトエラー)
```

### 6.2 エラーハンドリング実装

#### 6.2.1 カスタム例外クラス
```python
class InsectObserverError(Exception):
    """基底例外クラス"""
    pass

class HardwareError(InsectObserverError):
    """ハードウェア関連エラー"""
    
    def __init__(self, device: str, message: str):
        self.device = device
        self.message = message
        super().__init__(f"{device}: {message}")

class DetectionError(InsectObserverError):
    """検出関連エラー"""
    
    def __init__(self, phase: str, details: str):
        self.phase = phase
        self.details = details
        super().__init__(f"Detection {phase}: {details}")

class DataError(InsectObserverError):
    """データ関連エラー"""
    
    def __init__(self, operation: str, filepath: str, reason: str):
        self.operation = operation
        self.filepath = filepath
        self.reason = reason
        super().__init__(f"{operation} failed for {filepath}: {reason}")
```

#### 6.2.2 エラーハンドリング戦略
```python
class ErrorHandler:
    """エラーハンドリングクラス"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.retry_counts = {}
        self.max_retries = 3
        
    def handle_error(self, 
                    error: Exception, 
                    context: str, 
                    recoverable: bool = True) -> bool:
        """エラーハンドリング
        
        Args:
            error: 発生したエラー
            context: エラー発生コンテキスト
            recoverable: 復旧可能かどうか
            
        Returns:
            復旧成功可否
        """
        error_key = f"{context}:{type(error).__name__}"
        
        # ログ出力
        self.logger.error(f"Error in {context}: {error}")
        
        if not recoverable:
            self.logger.critical(f"Unrecoverable error: {error}")
            return False
            
        # リトライ処理
        retry_count = self.retry_counts.get(error_key, 0)
        if retry_count < self.max_retries:
            self.retry_counts[error_key] = retry_count + 1
            self.logger.info(f"Retrying {context} ({retry_count + 1}/{self.max_retries})")
            return True
        else:
            self.logger.error(f"Max retries exceeded for {context}")
            return False
    
    def reset_retry_count(self, context: str, error_type: str) -> None:
        """リトライカウンタリセット"""
        error_key = f"{context}:{error_type}"
        if error_key in self.retry_counts:
            del self.retry_counts[error_key]
```

### 6.3 復旧・フェイルセーフ機能

#### 6.3.1 自動復旧機能
```python
class RecoveryManager:
    """復旧管理クラス"""
    
    def __init__(self, system_controller):
        self.system_controller = system_controller
        self.recovery_strategies = {
            'CameraError': self.recover_camera,
            'GPIOError': self.recover_gpio,
            'ModelLoadError': self.recover_model,
            'FileIOError': self.recover_file_system
        }
    
    def attempt_recovery(self, error_type: str) -> bool:
        """復旧試行
        
        Args:
            error_type: エラータイプ
            
        Returns:
            復旧成功可否
        """
        if error_type in self.recovery_strategies:
            return self.recovery_strategies[error_type]()
        return False
    
    def recover_camera(self) -> bool:
        """カメラ復旧処理"""
        try:
            # カメラデバイス再初期化
            self.system_controller.hardware_controller.cleanup_camera()
            time.sleep(2)
            return self.system_controller.hardware_controller.initialize_camera()
        except Exception as e:
            self.logger.error(f"Camera recovery failed: {e}")
            return False
    
    def recover_gpio(self) -> bool:
        """GPIO復旧処理"""
        try:
            # GPIO クリーンアップ・再初期化
            self.system_controller.hardware_controller.cleanup_gpio()
            time.sleep(1)
            return self.system_controller.hardware_controller.initialize_gpio()
        except Exception as e:
            self.logger.error(f"GPIO recovery failed: {e}")
            return False
```

#### 6.3.2 セーフモード機能
```python
class SafeMode:
    """セーフモード制御クラス"""
    
    def __init__(self, system_controller):
        self.system_controller = system_controller
        self.safe_mode_active = False
        
    def activate_safe_mode(self, reason: str) -> None:
        """セーフモード有効化
        
        Args:
            reason: セーフモード移行理由
        """
        self.safe_mode_active = True
        self.logger.warning(f"Safe mode activated: {reason}")
        
        # 安全な状態に移行
        self.disable_hardware()
        self.enable_monitoring_only()
        
    def disable_hardware(self) -> None:
        """ハードウェア無効化"""
        try:
            # IR LED消灯
            self.system_controller.hardware_controller.control_ir_led(0.0)
            # カメラ停止
            self.system_controller.hardware_controller.stop_camera()
        except Exception as e:
            self.logger.error(f"Hardware disable failed: {e}")
    
    def enable_monitoring_only(self) -> None:
        """監視のみモード有効化"""
        # 最小限の機能のみ動作
        # - ログ出力継続
        # - システム状態監視継続  
        # - 復旧監視継続
        pass
```

---

## 7. 性能・品質要件

### 7.1 性能要件

#### 7.1.1 応答性能要件
| 処理 | 目標時間 | 最大許容時間 | 測定条件 |
|-----|---------|-------------|---------|
| システム起動 | ≤30秒 | ≤60秒 | 初回起動時 |
| 単発検出処理 | ≤5秒 | ≤10秒 | 1920×1080画像 |
| 画像撮影 | ≤1秒 | ≤2秒 | 標準解像度 |
| YOLOv8推論 | ≤3秒 | ≤5秒 | CPU推論 |
| CSV書き込み | ≤0.1秒 | ≤0.5秒 | 1レコード |
| 日次分析処理 | ≤60秒 | ≤300秒 | 1440レコード/日 |

#### 7.1.2 スループット要件
```
処理能力要件
├── 検出処理: 60秒間隔で24時間連続実行
├── 同時並行処理: 検出 + ログ記録 + 状態監視
├── データ処理量: 最大1440件/日の検出データ
├── ファイルI/O: 最大100MB/日のデータ書き込み
└── メモリ使用量: 最大2GB (Raspberry Pi総メモリの25%)
```

#### 7.1.3 性能監視実装
```python
class PerformanceMonitor:
    """性能監視クラス"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        
    def start_timer(self, operation: str) -> None:
        """処理開始時刻記録"""
        self.start_times[operation] = time.time()
        
    def end_timer(self, operation: str) -> float:
        """処理終了・所要時間記録"""
        if operation not in self.start_times:
            return 0.0
            
        elapsed_time = time.time() - self.start_times[operation]
        
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(elapsed_time)
        
        del self.start_times[operation]
        return elapsed_time
    
    def get_performance_stats(self, operation: str) -> Dict[str, float]:
        """性能統計取得"""
        if operation not in self.metrics:
            return {}
            
        times = self.metrics[operation]
        return {
            'count': len(times),
            'mean': np.mean(times),
            'median': np.median(times),
            'std': np.std(times),
            'min': np.min(times),
            'max': np.max(times)
        }

# 使用例
@performance_monitor
def detect_insects(self, image: np.ndarray) -> List[DetectionResult]:
    """性能監視付き検出処理"""
    # 実際の処理
    pass
```

### 7.2 品質要件

#### 7.2.1 信頼性要件
```
信頼性指標
├── 可用性: 99.0% (年間ダウンタイム <87.6時間)
├── MTBF: 720時間 (30日間無故障動作)
├── MTTR: 30分 (平均復旧時間)
├── 検出精度: 真陽性率 ≥80%, 偽陽性率 ≤10%
└── データ整合性: 99.9% (データ欠損率 <0.1%)
```

#### 7.2.2 保守性要件
```python
class MaintenanceSupport:
    """保守支援クラス"""
    
    def __init__(self):
        self.health_checker = HealthChecker()
        self.diagnostic = DiagnosticTool()
        
    def run_health_check(self) -> Dict[str, str]:
        """ヘルスチェック実行
        
        Returns:
            各コンポーネントの健全性状態
        """
        results = {}
        
        # ハードウェア状態確認
        results['camera'] = self.check_camera_health()
        results['gpio'] = self.check_gpio_health()
        results['storage'] = self.check_storage_health()
        
        # ソフトウェア状態確認  
        results['processes'] = self.check_process_health()
        results['memory'] = self.check_memory_health()
        results['logs'] = self.check_log_health()
        
        return results
    
    def generate_diagnostic_report(self) -> str:
        """診断レポート生成
        
        Returns:
            レポートファイルパス
        """
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.get_system_info(),
            'health_status': self.run_health_check(),
            'performance_metrics': self.get_performance_metrics(),
            'error_history': self.get_recent_errors(),
            'recommendations': self.generate_recommendations()
        }
        
        report_path = f"./reports/diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        return report_path
```

---

## 8. テスト設計

### 8.0 テストモジュール

#### 8.0.1 カメラ検出テストモジュール (test_camera_detection.py)

**概要**  
リアルタイムカメラ入力による物体検出機能の単体テストを行うスタンドアロンモジュール。

**目的**  
- YOLOv8モデルのリアルタイム性能検証
- カメラハードウェアとの統合確認
- 検出精度とフレームレートの評価
- CPUベース処理の性能限界測定

**使用方法**
```bash
# 基本的な使用方法
python test_camera_detection.py

# カスタムモデルでのテスト
python test_camera_detection.py --model weights/best.pt

# 異なるカメラIDの指定（複数カメラ接続時）
python test_camera_detection.py --camera 1

# 信頼度閾値の調整
python test_camera_detection.py --conf 0.5

# 全パラメータ指定
python test_camera_detection.py --model weights/custom_model.pt --camera 0 --conf 0.3
```

**コマンドラインオプション**
| オプション | 説明 | デフォルト値 | 備考 |
|-----------|------|-------------|------|
| --model | YOLOv8モデルファイルパス | yolov8n.pt | .ptファイルまたはUltralytics提供モデル名 |
| --camera | カメラデバイスID | 0 | 0: デフォルトカメラ、1以降: 追加カメラ |
| --conf | 検出信頼度閾値 | 0.25 | 0.0～1.0の範囲、低いほど多く検出 |

**出力情報**
1. **リアルタイム表示**
   - 検出結果を含む注釈付き映像
   - フレーム番号、処理時間、FPS情報
   - バウンディングボックスとクラス名・信頼度

2. **コンソール出力**
   - 各フレームの検出結果詳細
   - 処理時間とFPS
   - エラーメッセージ（発生時）

3. **終了時サマリー**
   - 総フレーム数
   - 平均処理時間
   - 平均FPS

**実装仕様**
```python
# 主要機能
- カメラ初期化とフレーム取得
- YOLOv8モデルによるリアルタイム推論
- 検出結果の可視化（OpenCV使用）
- 性能メトリクスの計算と表示
- キーボード入力による終了制御（'q'キー）

# エラーハンドリング
- カメラオープン失敗時の適切な終了
- モデル読み込みエラーの検出
- フレーム取得失敗時の継続処理
```

**テストシナリオ例**
1. **基本動作確認**
   ```bash
   # デフォルト設定での動作確認
   python test_camera_detection.py
   ```

2. **カスタムモデル性能評価**
   ```bash
   # 昆虫検出専用モデルでのテスト
   python test_camera_detection.py --model weights/beetle_detector.pt --conf 0.4
   ```

3. **複数カメラ切り替えテスト**
   ```bash
   # USBカメラでのテスト（カメラID: 1）
   python test_camera_detection.py --camera 1
   ```

**注意事項**
- Raspberry Pi上でのCPU処理のため、フレームレートは制限される
- カメラ解像度により処理時間が変動する
- 長時間実行時はCPU温度に注意が必要
- 十分な照明環境での使用を推奨

#### 8.0.2 実用カメラテストモジュール群

**概要**  
Raspberry Pi Camera Module 3とYOLOv8の互換性問題を解決した実用的なテストモジュール群。

**開発されたモジュール**

1. **test_libcamera_yolo.py** - ファイルベース検出モジュール
   - libcamera-stillを使用した画像撮影
   - YOLOv8による物体検出処理
   - 連続撮影・検出をサポート
   - 安定した動作を保証

2. **test_simple_realtime.py** - リアルタイム表示モジュール **（推奨）**
   - デスクトップ環境でのリアルタイム表示
   - libcamera-stillの高速連続実行
   - OpenCVによる検出結果の可視化
   - 2-5 FPS での安定動作

3. **test_realtime_display.py** - 高性能ストリーミングモジュール
   - libcamera-vidのストリーミング処理
   - より高いFPSが可能
   - 実装が複雑だが高性能

**技術的解決事項**
- Raspberry Pi Camera Module 3のlibcameraスタック対応
- OpenCVとの互換性問題の回避
- numpy互換性エラーの解決
- システムPython環境での安定動作

**実行環境要件**
- システムPython環境（仮想環境使用不可）
- デスクトップ環境またはX11転送
- ultralytics パッケージのシステムレベルインストール

**動作確認済み構成**
- **ハードウェア**: Raspberry Pi + Camera Module 3 NoIR (imx708_noir)
- **OS**: Raspberry Pi OS (Debian 12ベース)
- **Python**: 3.11
- **YOLOv8**: ultralytics 8.3.173
- **OpenCV**: 4.12.0 (システム: 4.6.0)

**パフォーマンス実測値**
- 平均推論時間: 400-700ms (CPU処理)
- 実用FPS: 2-5 FPS
- 検出精度: 標準YOLOv8n性能
- メモリ使用量: 安定

#### 8.0.3 昆虫検出専用テストモジュール (test_insect_detection.py)

**概要**  
ファインチューニング済みYOLOv8モデルを使用した昆虫（カブトムシ）専用の高精度検出システム。

**主な特徴**
- **専用モデル**: Hugging Face `Murasan/beetle-detection-yolov8` を使用
- **高精度検出**: mAP@0.5: 97.63%, mAP@0.5:0.95: 89.56%
- **専用クラス**: 'beetle' クラスのみ特化検出
- **包括的ログシステム**: CSV・JSON両形式でのデータ記録
- **自動画像保存**: 検出時の画像を自動で保存
- **リアルタイム統計**: 検出率、平均処理時間、活動パターン分析

**技術仕様**
```python
# 基本設定
モデルファイル: weights/best.pt (6.0MB)
検出クラス: ['beetle']
信頼度閾値: 0.4 (昆虫検出に最適化)
解像度: 640x480 (デフォルト)
目標FPS: 3 (CPU処理に適合)
```

**ログ出力形式**
1. **CSV形式** (`insect_detection_YYYYMMDD.csv`)
   ```csv
   timestamp,detected,beetle_count,confidence_max,confidence_avg,processing_time_ms
   2025-08-03T17:58:51.232402,1,1,0.476,0.476,389.8
   ```

2. **JSON形式** (`insect_detection_YYYYMMDD.json`)
   ```json
   {
     "timestamp": "2025-08-03T17:58:51.232402",
     "detected": 1,
     "beetle_count": 1,
     "processing_time_ms": 389.8,
     "detections": [{
       "class": "beetle",
       "confidence": 0.476,
       "bbox": [221, 7, 633, 480],
       "center": [427, 243],
       "size": [411, 472]
     }]
   }
   ```

**使用方法**
```bash
# 基本実行
python test_insect_detection.py

# カスタム設定
python test_insect_detection.py --conf 0.3 --fps 2
python test_insect_detection.py --size 1280x720 --display-size 1200x900
python test_insect_detection.py --no-save  # 検出画像保存無効
```

**出力ファイル**
- `insect_detection_logs/` - ログファイル
- `insect_detections/` - 検出画像 (`beetle_XXXXXX_HHMMSS.jpg`)

**統計表示機能**
- リアルタイム検出統計
- セッション終了時のサマリー表示
- 'r'キーによる統計表示
- 's'キーによるスクリーンショット保存

**パフォーマンス実測値**
- 平均推論時間: 300-400ms (CPU処理)
- 実用FPS: 2-3 FPS (昆虫検出専用)
- 検出精度: 高精度（ファインチューニング済み）
- メモリ使用量: 安定

**動作確認済み環境**
- **実行確認**: デスクトップ環境で正常動作
- **検出精度**: 実際の昆虫画像で検証済み
- **ログ機能**: CSV/JSON形式で正常記録
- **画像保存**: 検出時の自動保存動作確認

#### 8.0.4 昆虫データ分析ユーティリティ (analyze_insect_data.py)

**概要**  
`test_insect_detection.py`で収集した昆虫検出データの分析・可視化を行うユーティリティ。

**主な機能**
- **統計分析**: 検出率、活動パターン、時間別分析
- **可視化**: 活動タイムライン、検出密度ヒートマップ
- **レポート生成**: Markdownフォーマットの分析レポート

**出力ファイル**
- 活動分析グラフ: `insect_activity_analysis_*.png`
- 検出密度ヒートマップ: `insect_detection_heatmap_*.png`
- 分析レポート: `insect_detection_report_*.md`

**使用方法**
```bash
# 最新ログの分析
python analyze_insect_data.py

# 特定日の分析
python analyze_insect_data.py --date 2025-08-03

# グラフ生成なし
python analyze_insect_data.py --no-plots
```

### 8.1 テスト戦略

#### 8.1.1 テストレベル定義
```
テスト階層
├── 単体テスト (Unit Test)
│   ├── 各クラス・関数の個別テスト
│   ├── モック・スタブ使用
│   ├── カバレッジ: 80%以上
│   └── 自動実行・継続的テスト
├── 統合テスト (Integration Test)
│   ├── モジュール間連携テスト
│   ├── API インターフェーステスト
│   ├── データフローテスト
│   └── ハードウェア連携テスト
├── システムテスト (System Test)
│   ├── エンドツーエンドテスト
│   ├── 性能テスト
│   ├── 信頼性テスト
│   └── 負荷テスト
└── 受入テスト (Acceptance Test)
    ├── 要件適合性テスト
    ├── 運用シナリオテスト
    ├── ユーザビリティテスト
    └── 実環境テスト
```

#### 8.1.2 テストケース設計
```python
import unittest
from unittest.mock import Mock, patch
import numpy as np

class TestInsectDetector(unittest.TestCase):
    """検出器テストクラス"""
    
    def setUp(self):
        """テスト前準備"""
        self.config = {
            'model_path': './test_data/test_model.pt',
            'confidence_threshold': 0.5
        }
        self.detector = InsectDetector(self.config)
        
    def test_model_initialization(self):
        """モデル初期化テスト"""
        # 正常ケース
        self.assertTrue(self.detector.initialize_model(self.config['model_path']))
        
        # 異常ケース - ファイル不存在
        with self.assertRaises(FileNotFoundError):
            self.detector.initialize_model('./nonexistent_model.pt')
    
    @patch('cv2.imread')
    def test_image_preprocessing(self, mock_imread):
        """画像前処理テスト"""
        # テスト用画像データ作成
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = test_image
        
        # 前処理実行
        processed = self.detector.preprocess_image(test_image)
        
        # 結果検証
        self.assertEqual(processed.shape, (640, 640, 3))
        self.assertTrue(processed.dtype == np.float32)
        self.assertTrue(0 <= processed.min() <= processed.max() <= 1)
    
    def test_detection_result_validation(self):
        """検出結果検証テスト"""
        # 正常な検出結果
        valid_result = DetectionResult(
            x_center=320, y_center=240, width=50, height=40,
            confidence=0.85, class_id=0, timestamp='2025-07-25T10:30:00'
        )
        self.assertTrue(DataValidator.validate_detection_result(valid_result))
        
        # 異常な検出結果 - 信頼度範囲外
        invalid_result = DetectionResult(
            x_center=320, y_center=240, width=50, height=40,
            confidence=1.5, class_id=0, timestamp='2025-07-25T10:30:00'
        )
        self.assertFalse(DataValidator.validate_detection_result(invalid_result))

class TestActivityCalculator(unittest.TestCase):
    """活動量算出器テストクラス"""
    
    def setUp(self):
        """テスト前準備"""
        self.calculator = ActivityCalculator({})
        
        # テストデータ作成
        self.test_data = pd.DataFrame({
            'timestamp': pd.date_range('2025-07-25 00:00:00', periods=24, freq='H'),
            'x_center': np.random.normal(320, 50, 24),
            'y_center': np.random.normal(240, 30, 24),
            'confidence': np.random.uniform(0.5, 1.0, 24),
            'detected_flag': [1] * 24
        })
    
    def test_movement_distance_calculation(self):
        """移動距離算出テスト"""
        distances = self.calculator.calculate_movement_distance(self.test_data)
        
        # 結果検証
        self.assertEqual(len(distances), len(self.test_data) - 1)
        self.assertTrue(all(d >= 0 for d in distances))
        
    def test_activity_metrics_calculation(self):
        """活動量指標算出テスト"""
        metrics = self.calculator.calculate_activity_metrics(self.test_data)
        
        # 結果検証
        self.assertIsInstance(metrics, ActivityMetrics)
        self.assertEqual(metrics.total_detections, 24)
        self.assertGreater(metrics.total_distance, 0)

class TestIntegration(unittest.TestCase):
    """統合テストクラス"""
    
    @patch('hardware_controller.HardwareController')
    def test_end_to_end_detection(self, mock_hardware):
        """エンドツーエンド検出テスト"""
        # モック設定
        mock_hardware.capture_image.return_value = np.random.randint(
            0, 255, (1080, 1920, 3), dtype=np.uint8
        )
        
        # システム初期化
        system = InsectObserverSystem('./test_config.json')
        system.initialize_system()
        
        # 検出実行
        result = system.perform_detection_cycle()
        
        # 結果検証
        self.assertIn('detections', result)
        self.assertIn('timestamp', result)
        self.assertIn('processing_time', result)

# テスト実行
if __name__ == '__main__':
    unittest.main()
```

### 8.2 性能テスト

#### 8.2.1 負荷テスト実装
```python
import time
import threading
import psutil
from concurrent.futures import ThreadPoolExecutor

class PerformanceTest:
    """性能テストクラス"""
    
    def __init__(self, system):
        self.system = system
        self.metrics = []
        
    def run_load_test(self, duration_hours: int = 24) -> Dict[str, Any]:
        """負荷テスト実行
        
        Args:
            duration_hours: テスト継続時間
            
        Returns:
            テスト結果
        """
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        
        # 監視スレッド開始
        monitor_thread = threading.Thread(target=self._monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        detection_count = 0
        error_count = 0
        
        while time.time() < end_time:
            try:
                # 検出実行
                cycle_start = time.time()
                result = self.system.perform_detection_cycle()
                cycle_time = time.time() - cycle_start
                
                detection_count += 1
                self.metrics.append({
                    'timestamp': time.time(),
                    'cycle_time': cycle_time,
                    'memory_usage': psutil.virtual_memory().percent,
                    'cpu_usage': psutil.cpu_percent(),
                    'detections': len(result.get('detections', []))
                })
                
                # 次のサイクルまで待機
                time.sleep(max(0, 60 - cycle_time))
                
            except Exception as e:
                error_count += 1
                self.system.logger.error(f"Load test error: {e}")
                
        return {
            'duration': time.time() - start_time,
            'total_detections': detection_count,
            'total_errors': error_count,
            'error_rate': error_count / detection_count if detection_count > 0 else 0,
            'avg_cycle_time': np.mean([m['cycle_time'] for m in self.metrics]),
            'max_memory_usage': max([m['memory_usage'] for m in self.metrics]),
            'avg_cpu_usage': np.mean([m['cpu_usage'] for m in self.metrics])
        }
    
    def _monitor_system(self):
        """システム監視"""
        while True:
            # システムリソース監視
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.system.logger.warning(f"High memory usage: {memory.percent}%")
                
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 95:
                self.system.logger.warning(f"High CPU usage: {cpu}%")
                
            time.sleep(10)
```

---

## 9. シンプル観測モジュール (simple_observer.py)

### 9.1 モジュール概要

#### 9.1.1 目的と役割
```
モジュール名: simple_observer.py
役割: 既存検出器を活用したシンプルな継続観測
対象ユーザー: 簡単操作を求める初心者・研究者
設計方針: 既存システム無変更、最小限の設定、直感的操作
```

#### 9.1.2 アーキテクチャ位置づけ
```
┌─────────────────────────────────────────┐
│          シンプル観測システム           │
├─────────────────────────────────────────┤
│ simple_observer.py (新規追加)           │
│  ↓ 内部呼び出し                        │
│ insect_detector.py (既存・無変更)       │
│  ↓ 利用                                │
│ hardware_controller.py (既存・無変更)   │
└─────────────────────────────────────────┘
```

### 9.2 クラス設計

#### 9.2.1 SimpleObserver クラス
```python
class SimpleObserver:
    """シンプル昆虫観測クラス
    
    既存のInsectDetectorを利用して継続的な観測を実行し、
    結果をCSV形式で保存する軽量観測システム。
    """
    
    def __init__(self, interval: int = 60, 
                 duration: Optional[int] = None,
                 output_dir: str = "./simple_logs"):
        """初期化
        
        Args:
            interval: 観測間隔（秒）
            duration: 観測時間（秒、Noneで無制限）
            output_dir: 出力ディレクトリパス
        """
        
    def initialize(self) -> bool:
        """観測システム初期化
        
        Returns:
            bool: 初期化成功可否
        """
        
    def start_observation(self) -> None:
        """観測開始・メインループ実行"""
        
    def _perform_single_observation(self) -> Optional[Dict[str, Any]]:
        """単一観測実行
        
        Returns:
            Optional[Dict[str, Any]]: 観測結果データ
        """
        
    def _save_observation_to_csv(self, data: Dict[str, Any]) -> None:
        """観測結果CSV保存"""
        
    def stop(self) -> None:
        """観測停止・リソースクリーンアップ"""
        
    def get_status(self) -> Dict[str, Any]:
        """現在状態取得
        
        Returns:
            Dict[str, Any]: 状態情報辞書
        """
```

### 9.3 データ設計

#### 9.3.1 CSV出力フォーマット
```python
@dataclass
class ObservationRecord:
    """観測記録データクラス"""
    timestamp: str              # 観測時刻 (ISO形式)
    detection_count: int        # 検出昆虫数
    has_detection: bool         # 検出有無フラグ
    confidence_avg: float       # 平均信頼度
    x_center_avg: float         # X座標平均値
    y_center_avg: float         # Y座標平均値
    processing_time_ms: float   # 処理時間 (ミリ秒)
    observation_number: int     # 観測連番
```

#### 9.3.2 CSV出力例
```csv
timestamp,detection_count,has_detection,confidence_avg,x_center_avg,y_center_avg,processing_time_ms,observation_number
2025-07-29T20:30:05.123456,2,True,0.785,425.3,320.8,1205.3,1
2025-07-29T20:31:05.456789,0,False,0.0,0.0,0.0,890.1,2
2025-07-29T20:32:05.789012,1,True,0.923,680.1,240.5,1150.8,3
```

### 9.4 実行フロー設計

#### 9.4.1 メイン処理フロー
```
[アプリケーション開始]
        │
        ▼
    ┌─────────┐
    │ 初期化   │ ←── ・CSV設定
    │ 処理    │     ・検出器初期化
    └─────────┘     ・ログ設定
        │
        ▼
    ┌─────────┐
    │ 観測     │ ←── interval秒間隔での実行
    │ ループ   │     duration時間まで継続
    └─────────┘
        │
        ▼
    ┌─────────┐
    │ 単一     │ ←── ・insect_detector呼び出し
    │ 観測     │     ・結果データ集計
    └─────────┘     ・CSV保存
        │
        ▼
    ┌─────────┐
    │ 停止     │ ←── ・リソース解放
    │ 処理     │     ・統計表示
    └─────────┘
```

#### 9.4.2 エラーハンドリング
```python
def _error_handling_strategy():
    """エラー処理戦略
    
    1. 個別観測失敗: ログ出力後、次回観測継続
    2. 初期化失敗: アプリケーション終了
    3. CSV書き込み失敗: エラーログ出力、観測継続
    4. ユーザー中断 (Ctrl+C): 安全停止処理
    5. システムリソース不足: 警告ログ、継続試行
    """
```

### 9.5 インターフェース設計

#### 9.5.1 コマンドライン引数
```bash
python simple_observer.py [OPTIONS]

OPTIONS:
  --interval INTEGER    観測間隔（秒） [default: 60]
  --duration INTEGER    観測時間（秒） [default: unlimited]
  --output-dir TEXT     出力ディレクトリ [default: ./simple_logs]
  --help               ヘルプ表示
```

#### 9.5.2 出力ファイル
```
output_directory/
├── observations_YYYYMMDD_HHMMSS.csv  # 観測データ
├── observer_YYYYMMDD_HHMMSS.log      # 実行ログ
└── detection_images/                 # 検出画像 (既存機能)
    ├── detection_YYYYMMDD_HHMMSS_001.png
    └── detection_YYYYMMDD_HHMMSS_002.png
```

### 9.6 性能・品質要件

#### 9.6.1 性能要件
| 項目 | 要件値 | 測定条件 |
|------|--------|----------|
| 観測間隔精度 | ±2秒以内 | 60秒間隔設定時 |
| メモリ使用量 | 100MB以下 | 24時間連続実行時 |
| CSV書き込み時間 | 10ms以下 | 1レコード書き込み |
| 起動時間 | 10秒以内 | モデル読み込み含む |

#### 9.6.2 信頼性要件
```python
reliability_requirements = {
    "検出器初期化失敗許容率": "0%",
    "個別観測失敗許容率": "5%以下",
    "CSV書き込み失敗許容率": "1%以下",
    "24時間連続稼働成功率": "99%以上",
    "データ整合性": "100%"
}
```

### 9.7 設定管理

#### 9.7.1 検出器設定
```python
DETECTOR_SETTINGS = {
    "model_path": "./weights/beetle_detection.pt",
    "confidence_threshold": 0.5,
    "device": "cpu",
    "save_detection_images": True,
    "save_detection_logs": False  # CSV形式で独自保存
}
```

#### 9.7.2 観測設定
```python
OBSERVATION_SETTINGS = {
    "default_interval": 60,        # デフォルト観測間隔（秒）
    "max_duration": 86400 * 7,     # 最大観測時間（1週間）
    "csv_flush_interval": 1,       # CSV書き込み頻度
    "log_level": "INFO",           # ログレベル
    "enable_ir_led": True          # IR LED使用可否
}
```

### 9.8 拡張性設計

#### 9.8.1 将来拡張ポイント
```python
future_extensions = {
    "複数観測間隔": "時間帯別の観測間隔設定",
    "データフィルタリング": "信頼度による自動フィルタ",
    "リアルタイム可視化": "Web UI での観測状況表示",
    "アラート機能": "異常検出時の通知機能",
    "バックアップ機能": "自動データバックアップ"
}
```

#### 9.8.2 モジュール分離性
```
SimpleObserver (独立性確保)
├── 既存システムへの影響: なし
├── 単独実行可能性: あり
├── 設定変更による影響範囲: 限定的
└── 将来的な機能追加: 容易
```

---

## 10. Camera Test Scripts (tests/)

### 10.1 テストスクリプト概要

#### 10.1.1 目的と役割
tests/ディレクトリに配置された専用テストスクリプト群：
- Camera Module 3 Wide NoIR専用の検出・ロギング機能
- 本番システムとは独立したテスト環境
- オートフォーカス・マニュアルフォーカス対応
- 詳細な位置情報ログとCSV出力

#### 10.1.2 対象スクリプト
```
tests/
├── test_camera_detection_picamera2_fixed.py  # リアルタイム検出テスト
├── test_logging_picamera2.py                 # データロギングテスト
└── images/                                   # 検出画像保存先
    insect_detection_logs/                    # ログファイル保存先
```

### 10.2 test_camera_detection_picamera2_fixed.py

#### 10.2.1 機能仕様
```python
def test_camera_detection_fixed(
    model_path: str = 'yolov8n.pt',
    confidence: float = 0.25,
    width: int = 1536,
    height: int = 864,
    show_display: bool = True,
    focus_distance: float = 20.0  # 0でオートフォーカス
):
```

**主要機能:**
- Camera Module 3 Wide専用フォーカス制御（LensPosition 0-32範囲対応）
- オートフォーカス・マニュアルフォーカス切り替え
- YOLOv8による昆虫検出（カスタムモデル対応）
- リアルタイム画面表示（FPS・信頼度・位置情報）
- シャープネス最適化機能

#### 10.2.2 フォーカス制御設計
```python
def distance_to_lens_position(distance_cm, max_lens=32.0):
    """Camera Module 3 Wide用レンズ位置変換
    
    距離マッピング:
    - 5cm  -> 32.0 (最近接)
    - 20cm -> 10.0 (昆虫観察推奨)
    - 50cm -> 4.0
    - 100cm-> 0.0 (無限遠)
    """
```

**オートフォーカス実装:**
```python
if focus_distance == 0:
    picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
    time.sleep(2.0)  # 安定化待機
else:
    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
    picam2.set_controls({"LensPosition": float(target_lens_pos)})
```

#### 10.2.3 使用方法
```bash
# オートフォーカス（推奨）
python test_camera_detection_picamera2_fixed.py --model ../weights/best.pt --auto-focus

# マニュアルフォーカス
python test_camera_detection_picamera2_fixed.py --model ../weights/best.pt --distance 20

# ヘッドレスモード
python test_camera_detection_picamera2_fixed.py --model ../weights/best.pt --auto-focus --no-display
```

### 10.3 test_logging_picamera2.py

#### 10.3.1 機能仕様
```python
def test_logging_with_detection(
    model_path: str = 'weights/best.pt',
    confidence: float = 0.25,
    width: int = 1536,
    height: int = 864,
    focus_distance: float = 20.0,  # 0でオートフォーカス
    interval: int = 10,
    duration: int = 60,
    save_images: bool = False,
    output_dir: str = None
):
```

**主要機能:**
- 定期的な昆虫検出とデータロギング
- CSV形式での詳細位置情報記録
- オプションでの検出画像自動保存
- メタデータのJSON出力
- エラーハンドリング付き連続観測

#### 10.3.2 CSV出力データ構造
```csv
timestamp,observation_number,detection_count,has_detection,
class_names,confidence_values,bbox_coordinates,
center_x,center_y,bbox_width,bbox_height,area,
processing_time_ms,image_saved,image_filename
```

**データ項目詳細:**
```python
csv_data = {
    'timestamp': '2025-08-30T15:06:09.551232',
    'observation_number': 1,
    'detection_count': 1,
    'has_detection': True,
    'class_names': 'beetle',
    'confidence_values': '0.667',
    'bbox_coordinates': '(851,0,1387,391)',
    'center_x': '1119.1',    # バウンディングボックス中心X座標
    'center_y': '195.3',     # バウンディングボックス中心Y座標
    'bbox_width': '536.3',   # バウンディングボックス幅
    'bbox_height': '390.7',  # バウンディングボックス高さ
    'area': '209499.1',      # バウンディングボックス面積
    'processing_time_ms': '1669.2',
    'image_saved': False,
    'image_filename': ''
}
```

#### 10.3.3 メタデータ管理
```json
{
  "start_time": "2025-08-30T15:06:00.000000",
  "camera_module": "Camera Module 3 Wide NoIR",
  "focus_mode": "auto",
  "focus_distance_cm": null,
  "model_path": "weights/best.pt",
  "confidence_threshold": 0.25,
  "resolution": "1536x864",
  "interval_seconds": 10,
  "duration_seconds": 60,
  "save_images": false,
  "csv_file": "insect_detection_log_20250830_150600.csv"
}
```

#### 10.3.4 使用方法
```bash
# オートフォーカス・短時間テスト
python test_logging_picamera2.py --model ../weights/best.pt --auto-focus --interval 10 --duration 60

# 画像保存付き長時間観察
python test_logging_picamera2.py --model ../weights/best.pt --auto-focus --interval 30 --duration 3600 --save-images

# マニュアルフォーカス
python test_logging_picamera2.py --model ../weights/best.pt --distance 20 --interval 5 --duration 120
```

### 10.4 技術的特徴

#### 10.4.1 Camera Module 3 Wide対応
```python
# 特殊なLensPosition範囲（0-32）への対応
lens_controls = picam2.camera_controls.get("LensPosition")
if lens_controls:
    lp_min, lp_max, lp_default = lens_controls  # 0.0, 32.0, 1.0
else:
    lp_min, lp_max, lp_default = 0.0, 32.0, 1.0
```

#### 10.4.2 オートフォーカス実装の利点
```
オートフォーカスモード:
├── 利点: 距離測定不要、動的対応、画質大幅改善
├── 欠点: フォーカス不安定の可能性、処理遅延
└── 推奨用途: 一般的な昆虫観察、初期テスト
```

#### 10.4.3 詳細位置情報の活用
```python
# 移動追跡分析
movement_analysis = {
    'horizontal_movement': abs(current_x - previous_x),
    'vertical_movement': abs(current_y - previous_y),
    'size_change': abs(current_area - previous_area),
    'confidence_trend': confidence_values[-5:]  # 直近5回の信頼度
}
```

### 10.5 品質・性能仕様

#### 10.5.1 処理時間要件
```
- 初回検出: ~1500ms（モデル初期化含む）
- 通常検出: 300-400ms（CPU環境）
- フォーカス調整: 2000ms（オートフォーカス初期化）
- CSV書き込み: <1ms（即座にflush実行）
```

#### 10.5.2 データ品質保証
```python
# CSV書き込み保証
try:
    csv_writer.writerow(row)
    csv_file.flush()  # 確実な書き込み
except Exception as csv_error:
    print(f"[ERROR] Failed to save CSV: {csv_error}")
```

#### 10.5.3 エラー処理設計
```python
error_handling = {
    'フレーム取得失敗': '警告ログ出力・短時間リトライ',
    'CSV書き込み失敗': 'エラーメッセージ・観測継続',
    'モデル推論エラー': 'エラーログ・空データ記録',
    'カメラ初期化失敗': '即座に終了・エラーリターン'
}
```

### 10.6 運用・保守

#### 10.6.1 ファイル出力管理
```
tests/
├── insect_detection_logs/           # CSV・JSONログ
│   ├── insect_detection_log_YYYYMMDD_HHMMSS.csv
│   └── metadata_YYYYMMDD_HHMMSS.json
└── images/                          # 検出画像（オプション）
    └── detection_YYYYMMDD_HHMMSS_mmm.jpg
```

#### 10.6.2 ログローテーション
```python
# タイムスタンプベースのファイル命名
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_filename = f"insect_detection_log_{timestamp}.csv"
metadata_filename = f"metadata_{timestamp}.json"
```

#### 10.6.3 データ分析例
```python
# CSVデータ分析サンプル
import pandas as pd

df = pd.read_csv('insect_detection_log_20250830_150600.csv')
analysis = {
    'detection_rate': df['has_detection'].mean(),
    'avg_confidence': df[df['has_detection']]['confidence_values'].mean(),
    'movement_pattern': df[['center_x', 'center_y']].diff().abs().mean(),
    'size_distribution': df[df['has_detection']]['area'].describe()
}
```

### 10.7 本番環境用スクリプト

#### 10.7.1 本番環境用ファイル
```
tests/ディレクトリ内のファイルは本番環境用:
├── test_logging_left_half.py         # 本番用長時間ロギングスクリプト
├── test_camera_left_half_realtime.py # リアルタイム監視・調整用
├── test_camera_detection_picamera2_fixed.py  # 全画面検出用
└── test_logging_picamera2.py         # 全画面ロギング用

※「test_」という名前だが、これらは本番環境で使用する最終版スクリプト
```

#### 10.7.2 本番環境での成功パラメータ（実証済み）
```bash
# 9時間長時間観察の実証済み成功コマンド
nohup python3 test_logging_left_half.py \
  --auto-focus \
  --conf 0.4 \
  --exposure -0.5 \
  --contrast 2 \
  --brightness -0.05 \
  --interval 60 \
  --duration 32400 \
  --save-images > logging_9h.log 2>&1 &
```

**成功パラメータの詳細:**
| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `--conf` | 0.4 | 信頼度閾値（赤外線環境で最適） |
| `--exposure` | -0.5 | 露出補正（白飛び防止） |
| `--contrast` | 2 | コントラスト（赤外線画像の鮮明化） |
| `--brightness` | -0.05 | わずかな明度調整 |
| `--interval` | 60 | 1分間隔での観測 |
| `--duration` | 32400 | 9時間（32400秒）継続 |

#### 10.7.3 本番環境の特徴
```
実証済み環境条件:
├── Camera Module 3 Wide NoIR使用
├── 赤外線ライトのみ（可視光不要）
├── 左半分検出エリア（餌場に集中）
├── 2304x1296解像度（最大広角）
└── 長時間安定動作（9時間連続確認済み）
```

#### 10.7.4 左半分検出スクリプトの特徴
```python
# test_logging_left_half.py の主な機能
1. 画面左半分のみを検出対象とする
2. 誤検出を大幅に削減（土や葉を無視）
3. 餌エリアに焦点を当てた効率的な観察
4. CSV出力に検出エリア情報を追加
5. 本番環境での長時間安定稼働を実証
```

### 10.8 将来拡張計画

#### 10.8.1 機能拡張ポイント
```
計画中の拡張:
├── 複数昆虫同時追跡
├── 活動パターン自動分析
├── Web UI での実時間監視
├── アラート・通知機能
└── 機械学習による行動分類
```

#### 10.8.2 システム統合
```
統合可能性:
├── main.pyとの連携: 可能（独立性保持）
├── simple_observer.pyとの統合: 検討中
├── CLI機能への組み込み: 将来対応
└── Web APIとしての公開: 拡張可能
```

---

*文書バージョン: 1.3*  
*最終更新日: 2025-09-02*  
*更新内容: 本番環境用スクリプト情報と成功パラメータ追加*  
*承認者: 開発チーム*