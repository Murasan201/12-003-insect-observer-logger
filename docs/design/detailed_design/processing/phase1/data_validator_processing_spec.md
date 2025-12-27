# data_validator.py 処理説明書

**文書番号**: 12-003-PROC-005  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: data_validator.py 処理説明書  
**対象ファイル**: `utils/data_validator.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
システム内で使用されるデータの検証機能を提供し、データ品質管理と整合性チェックを行う。

### 主要機能
- データ検証ルールの定義
- 各種データタイプの検証実行
- CSV・DataFrame形式データの検証
- 検出結果・活動量データの検証

---

## 🔧 関数・メソッド仕様

### DataValidator.__init__()

**概要**: DataValidatorクラスの初期化処理

**処理内容**:
1. ロガーインスタンスを取得
2. 検証ルールオブジェクトを初期化
3. 検証統計カウンタを初期化

**入力インターフェース**:
```python
def __init__(self):
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | DataValidator | 初期化されたDataValidatorオブジェクト |

**使用例**:
```python
validator = DataValidator()
```

### DataValidator.validate_detection_result()

**概要**: DetectionResultオブジェクトの検証

**処理内容**:
1. 座標値の範囲チェック（0以上、画面内）
2. サイズ値の正数チェック
3. 信頼度の範囲チェック（0.0-1.0）
4. クラスIDの妥当性チェック
5. タイムスタンプ形式チェック

**入力インターフェース**:
```python
def validate_detection_result(self, detection: DetectionResult) -> Tuple[bool, List[str]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detection | DetectionResult | ○ | 検証対象の検出結果 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| is_valid | bool | 検証結果（True: 正常、False: 異常） |
| error_messages | List[str] | エラーメッセージリスト |

**使用例**:
```python
validator = DataValidator()
detection = DetectionResult(100.0, 150.0, 50.0, 40.0, 0.85, 0, "2025-07-28T10:30:00")
is_valid, errors = validator.validate_detection_result(detection)
```

### DataValidator.validate_csv_data()

**概要**: CSV形式データ（pandas DataFrame）の検証

**処理内容**:
1. 必須列の存在確認
2. データ型の妥当性チェック
3. 値の範囲チェック
4. 欠損値・重複値チェック
5. 日時形式の整合性チェック

**入力インターフェース**:
```python
def validate_csv_data(self, df: pd.DataFrame, data_type: str = "detection") -> Tuple[bool, List[str]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| df | pd.DataFrame | ○ | 検証対象のDataFrame |
| data_type | str | × | データタイプ（"detection", "activity"等） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| is_valid | bool | 検証結果（True: 正常、False: 異常） |
| error_messages | List[str] | エラーメッセージリスト |

**使用例**:
```python
validator = DataValidator()
df = pd.read_csv("detection_data.csv")
is_valid, errors = validator.validate_csv_data(df, "detection")
```

### DataValidator.validate_activity_data()

**概要**: 活動量データの検証

**処理内容**:
1. 総検出回数の非負数チェック
2. 移動距離の非負数チェック
3. 活動継続時間の妥当性チェック
4. ピーク活動時間の形式チェック
5. 時間別データの整合性チェック

**入力インターフェース**:
```python
def validate_activity_data(self, activity_summary: DailyActivitySummary) -> Tuple[bool, List[str]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| activity_summary | DailyActivitySummary | ○ | 検証対象の活動量サマリー |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| is_valid | bool | 検証結果（True: 正常、False: 異常） |
| error_messages | List[str] | エラーメッセージリスト |

**使用例**:
```python
validator = DataValidator()
activity_summary = DailyActivitySummary(...)
is_valid, errors = validator.validate_activity_data(activity_summary)
```

### DataValidator.validate_image_data()

**概要**: 画像データの検証

**処理内容**:
1. 画像データの存在確認
2. 画像形状の妥当性チェック（3次元配列）
3. チャンネル数の確認（RGB: 3チャンネル）
4. データ型の確認（uint8）
5. 解像度の妥当性チェック

**入力インターフェース**:
```python
def validate_image_data(self, image: np.ndarray) -> Tuple[bool, List[str]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| image | np.ndarray | ○ | 検証対象の画像データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| is_valid | bool | 検証結果（True: 正常、False: 異常） |
| error_messages | List[str] | エラーメッセージリスト |

**使用例**:
```python
validator = DataValidator()
image = cv2.imread("image.jpg")
is_valid, errors = validator.validate_image_data(image)
```

### DataValidator.validate_timestamp()

**概要**: タイムスタンプ文字列の検証

**処理内容**:
1. ISO8601形式の確認
2. 日時の妥当性チェック
3. タイムゾーン情報の確認
4. 範囲チェック（過去・未来の制限）

**入力インターフェース**:
```python
def validate_timestamp(self, timestamp: str) -> Tuple[bool, List[str]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| timestamp | str | ○ | 検証対象のタイムスタンプ文字列 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| is_valid | bool | 検証結果（True: 正常、False: 異常） |
| error_messages | List[str] | エラーメッセージリスト |

**使用例**:
```python
validator = DataValidator()
timestamp = "2025-07-28T10:30:00+09:00"
is_valid, errors = validator.validate_timestamp(timestamp)
```

### DataValidator.clean_detection_data()

**概要**: 検出データのクリーニング処理

**処理内容**:
1. 不正な値を持つレコードの除去
2. 重複レコードの削除
3. 欠損値の補完または除去
4. 異常値の検出・処理
5. クリーニング後データの再検証

**入力インターフェース**:
```python
def clean_detection_data(self, df: pd.DataFrame, 
                        remove_duplicates: bool = True, 
                        handle_missing: str = "drop") -> pd.DataFrame:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| df | pd.DataFrame | ○ | クリーニング対象のDataFrame |
| remove_duplicates | bool | × | 重複削除フラグ（デフォルト: True） |
| handle_missing | str | × | 欠損値処理方法（"drop", "fill"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| cleaned_df | pd.DataFrame | クリーニング後のDataFrame |

**使用例**:
```python
validator = DataValidator()
df = pd.read_csv("raw_data.csv")
cleaned_df = validator.clean_detection_data(df, remove_duplicates=True)
```

### DataValidator.generate_validation_report()

**概要**: 検証結果レポートの生成

**処理内容**:
1. 検証統計情報の集計
2. エラー種別ごとの分析
3. データ品質スコアの算出
4. 改善提案の生成
5. レポート形式でのまとめ

**入力インターフェース**:
```python
def generate_validation_report(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| report | Dict[str, Any] | 検証結果レポート辞書 |

**使用例**:
```python
validator = DataValidator()
# 複数の検証を実行後...
report = validator.generate_validation_report()
```

---

## 📊 データ構造

### DataValidationRules

**概要**: データ検証ルール定義クラス

**主要ルール定義**:
| ルール分類 | 説明 |
|----------|------|
| DETECTION_RULES | 検出データ検証ルール |
| ACTIVITY_RULES | 活動量データ検証ルール |
| IMAGE_RULES | 画像データ検証ルール |
| TIMESTAMP_RULES | タイムスタンプ検証ルール |

### DataValidator

**概要**: データ検証実行クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| rules | DataValidationRules | 検証ルールオブジェクト |
| validation_stats | Dict[str, int] | 検証統計カウンタ |

---

## 🔄 処理フロー

### データ検証フロー
```
1. DataValidator初期化
   ↓
2. validate_*()メソッド実行
   ↓
3. 検証ルール適用
   ↓
4. エラーメッセージ生成
   ↓
5. 検証結果返却
```

### データクリーニングフロー
```
1. 生データ読み込み
   ↓
2. 初回検証実行
   ↓
3. clean_detection_data()実行
   ↓
4. 不正データ除去・補完
   ↓
5. 再検証実行
```

### エラー処理フロー
```
検証エラー検出
   ↓
エラーメッセージ生成
   ↓
統計カウンタ更新
   ↓
ログ出力
   ↓
検証結果として返却
```

---

## 📝 実装メモ

### 注意事項
- pandasのデータ型判定は厳密に実行
- numpyの配列形状チェックでメモリ効率を考慮
- 大量データ処理時のメモリ使用量に注意
- 検証ルールは設定ファイルから読み込み可能にする

### 依存関係
- pandas（外部ライブラリ）
- numpy（外部ライブラリ）
- datetime（標準ライブラリ）
- typing（標準ライブラリ）
- logging（標準ライブラリ）
- models.detection_models（プロジェクト内モジュール）
- models.activity_models（プロジェクト内モジュール）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |