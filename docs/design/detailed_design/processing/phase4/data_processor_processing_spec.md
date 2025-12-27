# data_processor.py 処理説明書

**文書番号**: 12-003-PROC-005  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: data_processor.py 処理説明書  
**対象ファイル**: `data_processor.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
時系列検出データの分析・変換・集約処理を行うモジュール。データの品質向上と統計的処理の前処理を担当する。

### 主要機能
- 時系列データの前処理・クリーニング
- 統計的データ変換・正規化
- 異常値検出・補正（Z-score、IQR、Isolation Forest）
- データ集約・サンプリング
- 特徴量抽出・エンジニアリング
- 欠損値補間・データ平滑化

---

## 🔧 関数・メソッド仕様

### __init__(settings)

**概要**: データ処理器の初期化処理

**処理内容**:
1. ロガー設定
2. 処理設定の初期化（デフォルト値適用）
3. 集約関数リストの設定
4. 統計・状態管理オブジェクト初期化
5. データ検証器の初期化
6. 正規化スケーラー辞書の初期化
7. scikit-learn可用性チェック

**入力インターフェース**:
```python
def __init__(self, settings: Optional[ProcessingSettings] = None):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| settings | ProcessingSettings | × | データ処理設定（デフォルト値使用可） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### process_detection_data(data, target_columns)

**概要**: 検出データの包括的処理メイン関数

**処理内容**:
1. 入力データ検証・コピー作成
2. 処理対象カラムの自動選択（未指定時）
3. 時系列データ準備（_prepare_timeseries）
4. 欠損値処理（_handle_missing_values）
5. 異常値検出・処理（_handle_outliers）
6. データ平滑化（_apply_smoothing）
7. データ正規化（_normalize_features）
8. 特徴量抽出（_extract_features）
9. 処理統計の更新

**入力インターフェース**:
```python
def process_detection_data(self, data: pd.DataFrame, target_columns: Optional[List[str]] = None) -> pd.DataFrame:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 検出データ |
| target_columns | Optional[List[str]] | × | 処理対象カラム（自動選択可） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| processed_data | pd.DataFrame | 処理済みデータ |

**使用例**:
```python
processed_df = processor.process_detection_data(raw_df, ['x_center', 'y_center'])
```

---

### _auto_select_columns(data)

**概要**: 処理対象カラムの自動選択

**処理内容**:
1. 数値型カラムの抽出
2. 優先カラム（座標・サイズ・信頼度）の選択
3. その他数値カラムの追加
4. 除外カラム（detection_count等）の排除

**入力インターフェース**:
```python
def _auto_select_columns(self, data: pd.DataFrame) -> List[str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 入力データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| selected | List[str] | 選択されたカラム名リスト |

---

### _prepare_timeseries(data)

**概要**: 時系列データの準備・ソート処理

**処理内容**:
1. timestampカラムの存在確認
2. datetime型への変換
3. タイムスタンプ順ソート
4. インデックス再設定
5. 時系列インデックス設定

**入力インターフェース**:
```python
def _prepare_timeseries(self, data: pd.DataFrame) -> pd.DataFrame:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 生データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| data | pd.DataFrame | 時系列準備済みデータ |

---

### _handle_missing_values(data, columns)

**概要**: 欠損値の検出・補間処理

**処理内容**:
1. 各カラムの欠損値数カウント
2. 補間方法の選択（時系列・通常データ）
3. 線形補間・時系列補間の実行
4. 端点欠損値の前後埋め
5. 補間統計の更新

**入力インターフェース**:
```python
def _handle_missing_values(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 入力データ |
| columns | List[str] | ○ | 処理対象カラム |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| data | pd.DataFrame | 欠損値補間済みデータ |

---

### _handle_outliers(data, columns)

**概要**: 異常値の検出・処理

**処理内容**:
1. 各カラムでの異常値検出（_detect_outliers）
2. 異常値数のカウント・ログ出力
3. 処理方法に応じた異常値処理：
   - remove: 異常値行の削除
   - interpolate: 異常値をNaNに変換後補間
   - clip: 上下限値でクリッピング
4. 処理統計の更新

**入力インターフェース**:
```python
def _handle_outliers(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 入力データ |
| columns | List[str] | ○ | 処理対象カラム |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| data | pd.DataFrame | 異常値処理済みデータ |

---

### _detect_outliers(series)

**概要**: 異常値検出アルゴリズム実行

**処理内容**:
1. 検出方法の選択：
   - zscore: Z-score法による統計的異常値検出
   - iqr: 四分位範囲（IQR）による検出
   - isolation: Isolation Forest機械学習手法
2. 各手法による異常値マスク生成
3. NaN位置を考慮したマスク調整

**入力インターフェース**:
```python
def _detect_outliers(self, series: pd.Series) -> pd.Series:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| series | pd.Series | ○ | 検査対象データ系列 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| outlier_mask | pd.Series | 異常値位置のブールマスク |

---

### _apply_smoothing(data, columns)

**概要**: データ平滑化処理

**処理内容**:
1. 平滑化方法の選択：
   - moving_average: 移動平均フィルタ
   - savgol: Savitzky-Golay フィルタ
   - gaussian: ガウシアンフィルタ
2. 各カラムへの平滑化適用
3. 平滑化統計の更新

**入力インターフェース**:
```python
def _apply_smoothing(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 入力データ |
| columns | List[str] | ○ | 平滑化対象カラム |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| data | pd.DataFrame | 平滑化済みデータ |

---

### _normalize_features(data, columns)

**概要**: 特徴量正規化処理

**処理内容**:
1. 正規化方法の選択：
   - minmax: Min-Max正規化（0-1スケール）
   - standard: 標準化（平均0、標準偏差1）
   - robust: ロバスト正規化（中央値・四分位範囲）
2. スケーラーの初期化・学習
3. データ変換の実行
4. スケーラーのキャッシュ保存

**入力インターフェース**:
```python
def _normalize_features(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 入力データ |
| columns | List[str] | ○ | 正規化対象カラム |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| data | pd.DataFrame | 正規化済みデータ |

---

## 📊 データ構造

### ProcessingSettings

**概要**: データ処理の設定パラメータ

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| resampling_interval | str | リサンプリング間隔（"1T"=1分） |
| interpolation_method | str | 補間方法（linear, cubic, nearest） |
| max_gap_minutes | int | 最大補間ギャップ（分） |
| outlier_detection_method | str | 異常値検出方法（zscore, iqr, isolation） |
| outlier_threshold | float | 異常値閾値 |
| outlier_action | str | 異常値処理方法（remove, interpolate, clip） |
| apply_smoothing | bool | 平滑化適用フラグ |
| smoothing_window | int | 平滑化ウィンドウサイズ |
| smoothing_method | str | 平滑化方法 |
| normalization_method | str | 正規化方法 |
| feature_scaling | bool | 特徴量スケーリング有効フラグ |

### ProcessingStats

**概要**: データ処理の統計情報

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| total_records_processed | int | 処理済みレコード数 |
| outliers_detected | int | 検出された異常値数 |
| outliers_corrected | int | 補正された異常値数 |
| missing_values_filled | int | 補間された欠損値数 |
| data_points_smoothed | int | 平滑化されたデータ点数 |
| processing_time_seconds | float | 処理時間（秒） |
| data_quality_improvement | float | データ品質改善度 |

---

## 🔄 処理フロー

### メイン処理フロー
```
1. データ入力・検証
   ↓
2. 対象カラム選択
   ↓
3. 時系列データ準備
   ↓
4. 欠損値補間
   ↓
5. 異常値検出・処理
   ↓
6. データ平滑化
   ↓
7. 特徴量正規化
   ↓
8. 特徴量抽出
   ↓
9. 処理済みデータ出力
```

### 異常値処理フロー
```
異常値検出（Z-score/IQR/Isolation Forest）
   ↓
検出結果評価
   ↓
処理方法分岐
├─ remove: 行削除
├─ interpolate: NaN変換→補間
└─ clip: 上下限クリッピング
   ↓
統計更新・ログ出力
```

---

## 📝 実装メモ

### 注意事項
- 時系列データは必ずタイムスタンプでソート
- 異常値処理後は必ず補間処理を実行
- 正規化スケーラーは再利用のためキャッシュ
- 大量データでは処理時間・メモリ使用量に注意

### 依存関係
- pandas: データフレーム操作・時系列処理
- numpy: 数値計算・統計処理
- scipy: 信号処理・統計関数・補間
- sklearn: 機械学習・前処理（正規化・異常値検出）
- utils.data_validator: データ検証機能

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |