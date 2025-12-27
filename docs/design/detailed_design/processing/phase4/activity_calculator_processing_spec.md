# activity_calculator.py 処理説明書

**文書番号**: 12-003-PROC-004  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: activity_calculator.py 処理説明書  
**対象ファイル**: `activity_calculator.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
昆虫の活動量・移動パターンの算出と可視化を行うモジュール。検出された昆虫の位置データから移動距離や活動統計を算出する。

### 主要機能
- 検出データの時系列分析
- 移動距離・活動量の算出
- 統計的指標の計算（平均・分散・四分位）
- 行動パターン分析
- データ品質評価・異常値除去
- 時間帯別活動サマリー生成

---

## 🔧 関数・メソッド仕様

### __init__(settings, data_dir)

**概要**: 活動量算出器の初期化処理

**処理内容**:
1. ロガー設定
2. 算出設定の初期化（デフォルト値適用）
3. データディレクトリパス設定
4. 統計・状態管理オブジェクト初期化
5. データ検証器の初期化
6. キャッシュ辞書の初期化

**入力インターフェース**:
```python
def __init__(self, settings: Optional[CalculationSettings] = None, data_dir: str = "./logs"):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| settings | CalculationSettings | × | 活動量算出設定（デフォルト値使用可） |
| data_dir | str | × | データディレクトリパス（デフォルト: "./logs"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### load_detection_data(date)

**概要**: 指定日の検出データをCSVファイルから読み込み、前処理を実行

**処理内容**:
1. CSVファイル名生成（detection_log_YYYYMMDD.csv形式）
2. ファイル存在確認
3. pandas DataFrameとしてCSV読み込み
4. データ検証実行
5. 前処理（_preprocess_data）実行

**入力インターフェース**:
```python
def load_detection_data(self, date: str) -> Optional[pd.DataFrame]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| date | str | ○ | 対象日付（YYYY-MM-DD形式） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| df | Optional[pd.DataFrame] | 検出データ（失敗時None） |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| FileNotFoundError | CSVファイルが存在しない |
| pd.ParserError | CSVファイル形式不正 |

**使用例**:
```python
df = calculator.load_detection_data("2025-07-29")
```

---

### _preprocess_data(df)

**概要**: 検出データの前処理（データクリーニング・フィルタリング）

**処理内容**:
1. タイムスタンプのdatetime型変換
2. 信頼度による検出データフィルタリング
3. 検出回数が0より大きいレコードのみ抽出
4. 座標データ（x_center, y_center）の有効性確認
5. 無効座標・NaN値の除去
6. タイムスタンプ順ソート

**入力インターフェース**:
```python
def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| df | pd.DataFrame | ○ | 生の検出データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| df | pd.DataFrame | 前処理済み検出データ |

---

### calculate_movement_distance(data)

**概要**: 時系列検出データから移動距離を算出

**処理内容**:
1. 前回位置列（prev_x, prev_y）の追加
2. 時間差分の計算（分単位）
3. 各時点での移動距離計算（ユークリッド距離）
4. 移動速度による異常値検出・除去
5. 最小移動距離閾値の適用
6. 外れ値除去処理（Z-score法）
7. データ平滑化処理（移動平均）

**入力インターフェース**:
```python
def calculate_movement_distance(self, data: pd.DataFrame) -> List[float]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 時系列検出データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| movements | List[float] | 時間別移動距離リスト |

**使用例**:
```python
movements = calculator.calculate_movement_distance(df)
```

---

### _remove_outliers(data)

**概要**: Z-score法による外れ値除去処理

**処理内容**:
1. データ配列のZ-score計算
2. 閾値を超える外れ値の検出
3. 外れ値をNaNに置換
4. 線形補間による欠損値補完
5. 外れ値除去統計の更新

**入力インターフェース**:
```python
def _remove_outliers(self, data: List[float]) -> List[float]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | List[float] | ○ | 移動距離データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| cleaned_data | List[float] | 外れ値除去済みデータ |

---

### _smooth_data(data)

**概要**: 移動平均によるデータ平滑化処理

**処理内容**:
1. pandasシリーズ変換
2. 移動平均（rolling）の計算
3. 中央配置・最小期間設定
4. リスト形式で結果返却

**入力インターフェース**:
```python
def _smooth_data(self, data: List[float]) -> List[float]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | List[float] | ○ | 生の移動距離データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| smoothed | List[float] | 平滑化済みデータ |

---

### calculate_activity_metrics(data)

**概要**: 活動量指標の算出（総移動距離・統計値・活動パターン）

**処理内容**:
1. 移動距離リストの算出
2. 基本統計計算（総検出数・総移動距離）
3. 時間パターン分析（_analyze_temporal_patterns）
4. 統計指標計算（平均・標準偏差・四分位）
5. ActivityMetricsオブジェクトの生成
6. 処理統計の更新

**入力インターフェース**:
```python
def calculate_activity_metrics(self, data: pd.DataFrame) -> Optional[ActivityMetrics]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 検出データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| metrics | Optional[ActivityMetrics] | 活動量指標（失敗時None） |

**使用例**:
```python
metrics = calculator.calculate_activity_metrics(df)
```

---

## 📊 データ構造

### CalculationSettings

**概要**: 活動量算出の設定パラメータ

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| movement_threshold | float | 最小移動距離閾値（pixels） |
| time_window_minutes | int | 時間窓サイズ（分） |
| outlier_threshold | float | 外れ値除去閾値（標準偏差） |
| smoothing_window | int | 移動平均ウィンドウサイズ |
| min_detection_confidence | float | 最低検出信頼度 |
| max_movement_speed | float | 最大移動速度（pixels/minute） |
| enable_outlier_removal | bool | 外れ値除去有効フラグ |
| enable_smoothing | bool | 平滑化有効フラグ |

### CalculationStats

**概要**: 算出処理の統計情報

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| total_records_processed | int | 処理済みレコード数 |
| valid_movements_calculated | int | 有効移動計算数 |
| outliers_removed | int | 除去された外れ値数 |
| data_quality_score | float | データ品質スコア |
| processing_time_ms | float | 処理時間（ミリ秒） |

---

## 🔄 処理フロー

### メイン処理フロー
```
1. データ読み込み（load_detection_data）
   ↓
2. データ前処理（_preprocess_data）
   ↓
3. 移動距離算出（calculate_movement_distance）
   ↓
4. 活動量指標算出（calculate_activity_metrics）
   ↓
5. 結果返却（ActivityMetrics）
```

### エラー処理フロー
```
処理エラー発生
   ↓
ログ出力
   ↓
統計カウンタ更新
   ↓
None/空データ返却
```

---

## 📝 実装メモ

### 注意事項
- 座標データの単位はピクセル（解像度依存）
- 移動速度チェックで異常な瞬間移動を検出・除去
- 外れ値除去は線形補間で欠損値を補完
- 統計計算には最小データ数の要件あり

### 依存関係
- pandas: データフレーム操作・時系列分析
- numpy: 数値計算・統計処理
- scipy: 統計関数・外れ値検出
- models.activity_models: 結果データクラス
- utils.data_validator: データ検証機能

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |