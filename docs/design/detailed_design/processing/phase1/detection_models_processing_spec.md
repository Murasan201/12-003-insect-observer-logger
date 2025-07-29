# detection_models.py 処理説明書

**文書番号**: 12-002-PROC-001  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: detection_models.py 処理説明書  
**対象ファイル**: `models/detection_models.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
昆虫検出に関連するデータ構造を定義し、YOLOv8からの検出結果やCSV出力用のレコード形式を提供する。

### 主要機能
- YOLOv8検出結果のデータクラス定義
- CSV出力用の詳細検出レコード定義
- 複数検出時の個別詳細データ定義
- データ検証・変換機能

---

## 🔧 関数・メソッド仕様

### DetectionResult.__post_init__()

**概要**: DetectionResultデータクラスの初期化後検証処理

**処理内容**:
1. 検出結果データの妥当性検証を実行

**入力インターフェース**:
```python
def __post_init__(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 検証完了後に処理終了 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ValueError | データ検証失敗時 |

### DetectionResult.to_dict()

**概要**: DetectionResultオブジェクトを辞書形式に変換

**処理内容**:
1. 全属性を辞書のキー・値ペアに変換
2. 辞書オブジェクトを返却

**入力インターフェース**:
```python
def to_dict(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| result_dict | Dict[str, Any] | 検出結果の辞書表現 |

**使用例**:
```python
detection = DetectionResult(100.0, 150.0, 50.0, 40.0, 0.85, 0, "2025-07-28T10:30:00")
result_dict = detection.to_dict()
```

### DetectionResult.to_csv_row()

**概要**: CSV出力用の文字列形式に変換

**処理内容**:
1. 各属性をCSV形式の文字列に変換
2. カンマ区切りの行文字列を生成

**入力インターフェース**:
```python
def to_csv_row(self) -> str:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| csv_row | str | CSV形式の行文字列 |

**使用例**:
```python
detection = DetectionResult(100.0, 150.0, 50.0, 40.0, 0.85, 0, "2025-07-28T10:30:00")
csv_row = detection.to_csv_row()
```

### DetectionResult.validate()

**概要**: 検出結果データの妥当性検証

**処理内容**:
1. 座標値の範囲チェック（負の値でないこと）
2. サイズ値の範囲チェック（正の値であること）
3. 信頼度の範囲チェック（0.0-1.0の範囲）
4. クラスIDの妥当性チェック（非負整数）

**入力インターフェース**:
```python
def validate(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 検証成功時は何も返さない |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ValueError | 座標・サイズ・信頼度・クラスIDが不正な値の場合 |

### DetectionRecord.calculate_area()

**概要**: バウンディングボックスの面積を計算

**処理内容**:
1. width * height で面積を算出
2. 小数点以下2桁で丸める

**入力インターフェース**:
```python
def calculate_area(self) -> float:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| area | float | バウンディングボックスの面積（ピクセル^2） |

**使用例**:
```python
record = DetectionRecord(...)
area = record.calculate_area()
```

### DetectionRecord.to_csv_header()

**概要**: CSV出力用のヘッダー行を生成（クラスメソッド）

**処理内容**:
1. DetectionRecordの全フィールド名を取得
2. CSV形式のヘッダー文字列を生成

**入力インターフェース**:
```python
@classmethod
def to_csv_header(cls) -> str:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| header | str | CSV形式のヘッダー行 |

**使用例**:
```python
header = DetectionRecord.to_csv_header()
```

---

## 📊 データ構造

### DetectionResult

**概要**: YOLOv8検出結果を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| x_center | float | 中心X座標（ピクセル） |
| y_center | float | 中心Y座標（ピクセル） |
| width | float | バウンディングボックス幅（ピクセル） |
| height | float | バウンディングボックス高さ（ピクセル） |
| confidence | float | 検出信頼度（0.0-1.0） |
| class_id | int | クラスID（0: beetle等） |
| timestamp | str | 検出実行時刻のISO8601文字列 |

### DetectionRecord

**概要**: CSV出力用の詳細検出レコード

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| record_id | str | 一意のレコードID（UUID） |
| detection_date | date | 検出実行日 |
| detection_time | time | 検出実行時刻 |
| detected_flag | bool | 昆虫検出有無フラグ |
| detection_count | int | 検出個体数 |
| max_confidence | float | 最高信頼度 |
| avg_confidence | float | 平均信頼度 |
| detections | List[DetectionDetail] | 個別検出詳細リスト |

### DetectionDetail

**概要**: 複数検出時の個別詳細データ

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| detection_id | str | 検出ID |
| bbox_x_center | float | バウンディングボックス中心X座標 |
| bbox_y_center | float | バウンディングボックス中心Y座標 |
| bbox_width | float | バウンディングボックス幅 |
| bbox_height | float | バウンディングボックス高さ |
| confidence_score | float | 信頼度スコア |
| class_name | str | クラス名（"beetle"等） |

---

## 🔄 処理フロー

### メイン処理フロー
```
1. DetectionResultオブジェクト生成
   ↓
2. __post_init__による自動検証
   ↓
3. to_dict() / to_csv_row()による形式変換
   ↓
4. DetectionRecordへの集約（必要に応じて）
```

### エラー処理フロー
```
データ検証エラー発生
   ↓
ValueError例外をスロー
   ↓
呼び出し元でエラーハンドリング
```

---

## 📝 実装メモ

### 注意事項
- データクラスの@dataclassデコレータにより自動的にコンストラクタが生成される
- __post_init__メソッドが初期化後に自動実行される
- 全てのデータ検証は例外ベースで実行される

### 依存関係
- dataclasses（標準ライブラリ）
- datetime（標準ライブラリ）
- typing（標準ライブラリ）
- uuid（標準ライブラリ）
- numpy（外部ライブラリ）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |