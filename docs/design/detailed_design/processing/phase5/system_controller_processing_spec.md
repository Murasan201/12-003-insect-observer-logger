# system_controller.py 処理説明書

**文書番号**: 12-002-PROC-008  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: system_controller.py 処理説明書  
**対象ファイル**: `system_controller.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
各モジュール間の連携制御と統合オーケストレーションを行うシステム統合管理モジュール。

### 主要機能
- モジュール間の依存関係管理
- 処理パイプライン制御
- システム状態管理・ヘルスチェック
- パフォーマンス監視・分析
- エラー統合管理・自動復旧
- 統合ワークフロー実行制御

---

## 🔧 関数・メソッド仕様

### __init__(config, hardware_controller, detector, detection_processor, activity_calculator, visualizer)

**概要**: システム統合管理クラスの初期化

**処理内容**:
1. ロガー設定
2. システム設定の保存
3. 各モジュールインスタンスの参照設定
4. エラーハンドリング・監視機能の初期化
5. システム状態・パフォーマンス指標の初期化
6. 検出履歴・パフォーマンス履歴の初期化
7. スレッド同期制御用ロック設定

**入力インターフェース**:
```python
def __init__(self, config: SystemConfiguration, hardware_controller: HardwareController, detector: InsectDetector, detection_processor: DetectionProcessor, activity_calculator: ActivityCalculator, visualizer: Visualizer):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config | SystemConfiguration | ○ | システム設定オブジェクト |
| hardware_controller | HardwareController | ○ | ハードウェア制御器 |
| detector | InsectDetector | ○ | 昆虫検出器 |
| detection_processor | DetectionProcessor | ○ | 検出処理器 |
| activity_calculator | ActivityCalculator | ○ | 活動量算出器 |
| visualizer | Visualizer | ○ | 可視化器 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### execute_detection_workflow(use_ir_led, save_results)

**概要**: 統合検出ワークフローの実行

**処理内容**:
1. 処理ロック取得・エラーコンテキスト設定
2. ハードウェア前処理（_prepare_hardware）
3. 検出実行（detector.detect_single_image）
4. 検出結果処理（detection_processor.process_detection_record）
5. 履歴更新・サイズ制限管理
6. パフォーマンス指標の更新
7. エラーハンドリング・統計更新

**入力インターフェース**:
```python
def execute_detection_workflow(self, use_ir_led: bool = True, save_results: bool = True) -> Optional[DetectionRecord]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| use_ir_led | bool | × | IR LED使用可否（デフォルト: True） |
| save_results | bool | × | 結果保存可否（デフォルト: True） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| record | Optional[DetectionRecord] | 処理済み検出記録（失敗時None） |

**使用例**:
```python
result = controller.execute_detection_workflow(use_ir_led=True, save_results=True)
if result:
    print(f"Detection completed: {result.detection_count} insects found")
```

---

### execute_analysis_workflow(date, generate_report)

**概要**: 統合分析ワークフローの実行

**処理内容**:
1. 指定日のデータ読み込み・検証
2. 活動量指標の算出（activity_calculator.calculate_activity_metrics）
3. 時間別サマリー生成（generate_hourly_summaries）
4. 可視化レポート生成（visualizer.export_visualization_report）
5. エラーハンドリング・ログ出力

**入力インターフェース**:
```python
def execute_analysis_workflow(self, date: str, generate_report: bool = True) -> Optional[ActivityMetrics]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| date | str | ○ | 分析対象日（YYYY-MM-DD形式） |
| generate_report | bool | × | レポート生成可否（デフォルト: True） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| metrics | Optional[ActivityMetrics] | 活動量指標（失敗時None） |

**使用例**:
```python
metrics = controller.execute_analysis_workflow("2025-07-29", generate_report=True)
```

---

### _prepare_hardware()

**概要**: ハードウェア前処理・状態確認

**処理内容**:
1. ハードウェア制御器の初期化状態確認
2. カメラ・LED各種ハードウェアの可用性チェック
3. 前処理エラーのログ出力
4. 成功可否の返却

**入力インターフェース**:
```python
def _prepare_hardware(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | ハードウェア準備成功可否 |

---

### _update_performance_metrics(workflow_time_ms)

**概要**: パフォーマンス指標の更新

**処理内容**:
1. 平均検出時間の更新
2. システムスループット計算（検出数/時間）
3. ハードウェア情報更新（CPU温度等）
4. 成功率・エラー率の計算
5. 統計情報の保存

**入力インターフェース**:
```python
def _update_performance_metrics(self, workflow_time_ms: float) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| workflow_time_ms | float | ○ | ワークフロー処理時間（ミリ秒） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 指標更新完了 |

---

### perform_health_check()

**概要**: システム健全性チェックの実行

**処理内容**:
1. エラーメッセージ・警告リストの初期化
2. 各モジュールの健全性チェック：
   - ハードウェア（_check_hardware_health）
   - 検出器（_check_detector_health）
   - 処理器（_check_processor_health）
   - 算出器（_check_calculator_health）
   - 可視化器（_check_visualizer_health）
3. 総合判定・稼働時間更新
4. 結果辞書の作成・返却

**入力インターフェース**:
```python
def perform_health_check(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| result | Dict[str, Any] | ヘルスチェック結果辞書 |

**戻り値構造**:
```python
{
    "overall_healthy": bool,           # 総合健全性
    "modules": {                       # モジュール別状態
        "hardware": str,
        "detector": str,
        "processor": str,
        "calculator": str,
        "visualizer": str
    },
    "errors": List[str],              # エラーメッセージリスト
    "warnings": List[str],            # 警告メッセージリスト
    "uptime_seconds": float,          # 稼働時間
    "last_check": str                 # 最終チェック時刻
}
```

**使用例**:
```python
health = controller.perform_health_check()
if not health["overall_healthy"]:
    print(f"System issues: {health['errors']}")
```

---

### _check_hardware_health()

**概要**: ハードウェア健全性チェック

**処理内容**:
1. ハードウェア制御器からシステム状態取得
2. カメラ初期化状態の確認
3. LED可用性の確認
4. CPU温度の閾値チェック（80℃以上で警告）
5. エラー・警告メッセージの生成

**入力インターフェース**:
```python
def _check_hardware_health(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| healthy | bool | ハードウェア健全性 |

---

### _check_detector_health()

**概要**: 検出器健全性チェック

**処理内容**:
1. 検出器の詳細状態取得
2. 初期化状態の確認
3. モデル読み込み状態の確認
4. エラー率の計算・評価（10%以上で警告）
5. ステータス更新・メッセージ生成

**入力インターフェース**:
```python
def _check_detector_health(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| healthy | bool | 検出器健全性 |

---

### _check_processor_health()

**概要**: 処理器健全性チェック

**処理内容**:
1. 検出処理器の統計情報取得
2. 処理エラー率の計算
3. 閾値チェック（5%以上で警告）
4. ステータス更新・メッセージ生成

**入力インターフェース**:
```python
def _check_processor_health(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| healthy | bool | 処理器健全性 |

---

### _check_calculator_health()

**概要**: 算出器健全性チェック

**処理内容**:
1. 活動量算出器の統計情報取得
2. 計算エラー率の算出
3. 閾値チェック（10%以上で警告）
4. ステータス更新・メッセージ生成

**入力インターフェース**:
```python
def _check_calculator_health(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| healthy | bool | 算出器健全性 |

---

### _check_visualizer_health()

**概要**: 可視化器健全性チェック

**処理内容**:
1. 可視化ライブラリ（matplotlib/plotly）の可用性確認
2. 出力ディレクトリの存在確認
3. エラー・警告メッセージの生成
4. ステータス更新

**入力インターフェース**:
```python
def _check_visualizer_health(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| healthy | bool | 可視化器健全性 |

---

### get_performance_report()

**概要**: パフォーマンスレポートの取得

**処理内容**:
1. 現在のパフォーマンス指標の取得
2. 履歴データからのトレンド分析
3. システム推奨事項の生成
4. 包括的なレポート辞書の作成

**入力インターフェース**:
```python
def get_performance_report(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| report | Dict[str, Any] | パフォーマンスレポート |

**戻り値構造**:
```python
{
    "current_metrics": {              # 現在の指標
        "avg_detection_time_ms": float,
        "detection_success_rate": float,
        "system_throughput": float,
        "cpu_temperature": float,
        "total_detections": int,
        "total_errors": int
    },
    "historical_data": {...},        # 履歴データ
    "recommendations": [...]          # システム推奨事項
}
```

---

## 📊 データ構造

### SystemHealthStatus

**概要**: システム健全性状態の管理

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| overall_healthy | bool | 総合健全性状態 |
| hardware_status | str | ハードウェア状態（healthy/camera_error/led_warning等） |
| detector_status | str | 検出器状態（healthy/not_initialized/model_error等） |
| processor_status | str | 処理器状態 |
| calculator_status | str | 算出器状態 |
| visualizer_status | str | 可視化器状態 |
| error_messages | List[str] | エラーメッセージリスト |
| warnings | List[str] | 警告メッセージリスト |
| last_check_time | str | 最終チェック時刻 |
| uptime_seconds | float | システム稼働時間 |

### PerformanceMetrics

**概要**: システムパフォーマンス指標

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| avg_detection_time_ms | float | 平均検出時間（ミリ秒） |
| avg_processing_time_ms | float | 平均処理時間（ミリ秒） |
| detection_success_rate | float | 検出成功率（0.0-1.0） |
| system_throughput | float | システムスループット（検出数/時間） |
| memory_usage_mb | float | メモリ使用量（MB） |
| cpu_temperature | float | CPU温度（℃） |
| total_detections | int | 総検出数 |
| total_errors | int | 総エラー数 |

---

## 🔄 処理フロー

### 統合検出ワークフローフロー
```
1. 処理ロック取得
   ↓
2. ハードウェア前処理
   ↓
3. 検出実行（detector）
   ↓
4. 結果処理（detection_processor）
   ↓
5. 履歴更新・統計更新
   ↓
6. パフォーマンス指標更新
   ↓
7. 処理ロック解放・結果返却
```

### システムヘルスチェックフロー
```
1. エラー・警告リスト初期化
   ↓
2. 各モジュール健全性チェック
   ├─ ハードウェア
   ├─ 検出器
   ├─ 処理器
   ├─ 算出器
   └─ 可視化器
   ↓
3. 総合判定・稼働時間更新
   ↓
4. 結果辞書作成・返却
```

### エラー処理フロー
```
例外発生
   ↓
エラーハンドラー連携
   ↓
エラー分類・重要度判定
   ↓
ログ出力・統計更新
   ↓
復旧処理実行（可能な場合）
   ↓
処理継続or停止判定
```

---

## 📝 実装メモ

### 注意事項
- スレッドセーフな処理（processing_lock使用）
- 各モジュールの依存関係を考慮した順序制御
- エラー率の閾値管理によるシステム健全性監視
- パフォーマンス履歴のメモリ使用量制限

### 依存関係
- config.config_manager: システム設定管理
- hardware_controller: ハードウェア統合制御
- insect_detector: 昆虫検出機能
- detection_processor: 検出結果処理
- activity_calculator: 活動量算出
- visualization: 可視化機能
- error_handler: エラーハンドリング統合
- monitoring: システム監視機能

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |