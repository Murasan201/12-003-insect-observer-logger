# detection_processor.py 処理説明書

**文書番号**: 12-003-PROC-202  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: detection_processor.py 処理説明書  
**対象ファイル**: `detection_processor.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
昆虫検出結果の後処理・フィルタリング・分析を行い、検出品質の向上と統計データの生成を提供する。

### 主要機能
- 検出結果の品質評価・フィルタリング
- 重複検出の除去
- 検出データの統計分析
- CSVログ出力
- 検出履歴管理

---

## 🔧 関数・メソッド仕様

### ProcessingSettings.__post_init__()

**概要**: ProcessingSettings データクラスの初期化後処理

**処理内容**:
1. 信頼度閾値の範囲チェック（0.0-1.0）
2. サイズ制限値の妥当性チェック
3. 重複検出閾値の範囲チェック
4. 品質閾値の範囲チェック

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
| ValueError | 設定値が不正な範囲の場合 |

### DetectionProcessor.__init__()

**概要**: 検出結果処理クラスの初期化処理

**処理内容**:
1. ロガーインスタンスを取得
2. 処理設定の保存
3. データ検証器の初期化
4. 処理統計オブジェクトの初期化
5. 検出履歴リストの初期化

**入力インターフェース**:
```python
def __init__(self, settings: ProcessingSettings):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| settings | ProcessingSettings | ○ | 処理設定オブジェクト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | DetectionProcessor | 初期化された処理オブジェクト |

**使用例**:
```python
settings = ProcessingSettings(min_confidence=0.7)
processor = DetectionProcessor(settings)
```

### DetectionProcessor.process_detections()

**概要**: 検出結果の統合的な後処理

**処理内容**:
1. 入力検出結果の検証
2. 信頼度フィルタリング
3. サイズフィルタリング
4. 重複検出の除去
5. 品質評価・統計更新

**入力インターフェース**:
```python
def process_detections(self, detections: List[DetectionResult]) -> List[DetectionResult]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 生の検出結果リスト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filtered_detections | List[DetectionResult] | フィルタリング済み検出結果 |

**使用例**:
```python
raw_detections = detector.detect_from_image(image)
filtered = processor.process_detections(raw_detections)
```

### DetectionProcessor.filter_by_confidence()

**概要**: 信頼度による検出結果フィルタリング

**処理内容**:
1. 設定された信頼度閾値の確認
2. 各検出結果の信頼度チェック
3. 閾値以上の検出結果のみ抽出
4. フィルタリング統計の更新
5. フィルタリング済みリストの返却

**入力インターフェース**:
```python
def filter_by_confidence(self, detections: List[DetectionResult]) -> List[DetectionResult]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 入力検出結果リスト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filtered | List[DetectionResult] | 信頼度フィルタリング済みリスト |

**使用例**:
```python
high_confidence = processor.filter_by_confidence(detections)
```

### DetectionProcessor.filter_by_size()

**概要**: サイズによる検出結果フィルタリング

**処理内容**:
1. 設定されたサイズ制限の確認
2. 各検出結果のバウンディングボックスサイズ計算
3. サイズ範囲内の検出結果のみ抽出
4. 異常サイズ検出の記録
5. フィルタリング統計の更新

**入力インターフェース**:
```python
def filter_by_size(self, detections: List[DetectionResult]) -> List[DetectionResult]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 入力検出結果リスト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filtered | List[DetectionResult] | サイズフィルタリング済みリスト |

**使用例**:
```python
size_filtered = processor.filter_by_size(detections)
```

### DetectionProcessor.remove_duplicates()

**概要**: 重複検出の除去

**処理内容**:
1. 検出結果のIoU（Intersection over Union）計算
2. 重複閾値を超えるペアの特定
3. 信頼度の高い検出結果を保持
4. 重複除去統計の更新
5. 重複除去済みリストの返却

**入力インターフェース**:
```python
def remove_duplicates(self, detections: List[DetectionResult]) -> List[DetectionResult]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 入力検出結果リスト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| unique_detections | List[DetectionResult] | 重複除去済みリスト |

**使用例**:
```python
unique = processor.remove_duplicates(detections)
```

### DetectionProcessor.calculate_iou()

**概要**: 2つの検出結果のIoU計算

**処理内容**:
1. 各検出結果のバウンディングボックス座標計算
2. 交差領域の計算
3. 合計領域の計算
4. IoU値の算出
5. IoU値の返却

**入力インターフェース**:
```python
def calculate_iou(self, detection1: DetectionResult, detection2: DetectionResult) -> float:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detection1 | DetectionResult | ○ | 検出結果1 |
| detection2 | DetectionResult | ○ | 検出結果2 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| iou | float | IoU値（0.0-1.0） |

**使用例**:
```python
iou = processor.calculate_iou(detection1, detection2)
if iou > 0.7:
    print("重複検出")
```

### DetectionProcessor.evaluate_quality()

**概要**: 検出品質の評価

**処理内容**:
1. 信頼度分布の分析
2. 検出サイズ分布の分析
3. 空間的分布の分析
4. 品質スコアの計算
5. 品質メトリクスの生成

**入力インターフェース**:
```python
def evaluate_quality(self, detections: List[DetectionResult]) -> Dict[str, float]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 検出結果リスト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| quality_metrics | Dict[str, float] | 品質評価メトリクス |

**使用例**:
```python
metrics = processor.evaluate_quality(detections)
print(f"平均信頼度: {metrics['avg_confidence']}")
```

### DetectionProcessor.create_detection_record()

**概要**: 検出結果からDetectionRecordの作成

**処理内容**:
1. 検出結果リストの分析
2. 統計情報の計算（検出数・最高/平均信頼度）
3. DetectionRecordオブジェクトの作成
4. タイムスタンプ・IDの設定
5. 記録の返却

**入力インターフェース**:
```python
def create_detection_record(self, detections: List[DetectionResult], 
                           timestamp: Optional[datetime] = None) -> DetectionRecord:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 検出結果リスト |
| timestamp | Optional[datetime] | × | 記録タイムスタンプ（None: 現在時刻） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| record | DetectionRecord | 作成された検出記録 |

**使用例**:
```python
record = processor.create_detection_record(detections)
```

### DetectionProcessor.save_to_csv()

**概要**: 検出結果のCSV保存

**処理内容**:
1. 保存ディレクトリの確認・作成
2. CSVファイル名の生成
3. ヘッダー行の作成
4. 検出データの書き込み
5. 保存完了の確認

**入力インターフェース**:
```python
def save_to_csv(self, detections: List[DetectionResult], 
               base_dir: str = "./logs", 
               filename: Optional[str] = None) -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 検出結果リスト |
| base_dir | str | × | 保存ベースディレクトリ |
| filename | Optional[str] | × | ファイル名（None: 自動生成） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| saved_path | str | 保存されたCSVファイルパス |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| IOError | ファイル保存エラーの場合 |

**使用例**:
```python
csv_path = processor.save_to_csv(detections, "./output")
```

### DetectionProcessor.load_from_csv()

**概要**: CSVファイルから検出結果の読み込み

**処理内容**:
1. CSVファイルの存在確認
2. pandasでの読み込み
3. データ型変換・検証
4. DetectionResultオブジェクトの復元
5. 検出結果リストの返却

**入力インターフェース**:
```python
def load_from_csv(self, csv_path: str) -> List[DetectionResult]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| csv_path | str | ○ | CSVファイルパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| detections | List[DetectionResult] | 読み込まれた検出結果リスト |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| FileNotFoundError | CSVファイルが存在しない場合 |
| ValueError | データ形式が不正な場合 |

**使用例**:
```python
detections = processor.load_from_csv("./logs/detection_20250728.csv")
```

### DetectionProcessor.analyze_temporal_patterns()

**概要**: 時系列パターンの分析

**処理内容**:
1. 検出履歴の時系列データ作成
2. 時間別検出頻度の計算
3. ピーク活動時間の特定
4. 活動パターンの分析
5. 分析結果辞書の生成

**入力インターフェース**:
```python
def analyze_temporal_patterns(self, detections: List[DetectionResult], 
                             time_window_hours: int = 24) -> Dict[str, Any]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 検出結果リスト |
| time_window_hours | int | × | 分析時間窓（時間） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| patterns | Dict[str, Any] | 時系列パターン分析結果 |

**使用例**:
```python
patterns = processor.analyze_temporal_patterns(detections, 48)
```

### DetectionProcessor.generate_hourly_summary()

**概要**: 時間別活動サマリーの生成

**処理内容**:
1. 検出結果の時間別グループ化
2. 各時間の統計計算
3. HourlyActivitySummaryオブジェクトの作成
4. 時間別サマリーリストの生成
5. サマリーの返却

**入力インターフェース**:
```python
def generate_hourly_summary(self, detections: List[DetectionResult], 
                           target_date: datetime) -> List[HourlyActivitySummary]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detections | List[DetectionResult] | ○ | 検出結果リスト |
| target_date | datetime | ○ | 対象日付 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| hourly_summaries | List[HourlyActivitySummary] | 時間別サマリーリスト |

**使用例**:
```python
summaries = processor.generate_hourly_summary(detections, datetime.now())
```

### DetectionProcessor.get_processing_statistics()

**概要**: 処理統計情報の取得

**処理内容**:
1. 累積処理統計の集計
2. フィルタリング効果の分析
3. 処理性能メトリクスの計算
4. 統計辞書の生成
5. 統計情報の返却

**入力インターフェース**:
```python
def get_processing_statistics(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| statistics | Dict[str, Any] | 処理統計辞書 |

**使用例**:
```python
stats = processor.get_processing_statistics()
print(f"フィルタリング率: {stats['filter_rate']:.2%}")
```

### DetectionProcessor.reset_statistics()

**概要**: 処理統計のリセット

**処理内容**:
1. 統計カウンターの初期化
2. 処理履歴のクリア
3. メモリ使用量の最適化
4. リセット完了ログの出力

**入力インターフェース**:
```python
def reset_statistics(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | リセット完了後に処理終了 |

**使用例**:
```python
processor.reset_statistics()
```

---

## 📊 データ構造

### ProcessingSettings

**概要**: 検出後処理設定を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| min_confidence | float | 最小信頼度閾値 |
| max_confidence | float | 最大信頼度閾値 |
| min_size | Tuple[float, float] | 最小サイズ（幅, 高さ） |
| max_size | Tuple[float, float] | 最大サイズ（幅, 高さ） |
| duplicate_threshold | float | 重複検出IoU閾値 |
| quality_threshold | float | 品質閾値 |
| enable_size_filter | bool | サイズフィルタ有効フラグ |
| enable_confidence_filter | bool | 信頼度フィルタ有効フラグ |
| enable_duplicate_filter | bool | 重複除去フィルタ有効フラグ |
| save_filtered_data | bool | フィルタ済みデータ保存フラグ |

### ProcessingStats

**概要**: 処理統計情報を表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| total_processed | int | 総処理件数 |
| total_filtered_out | int | 総フィルタアウト件数 |
| confidence_filtered | int | 信頼度フィルタアウト件数 |
| size_filtered | int | サイズフィルタアウト件数 |
| duplicate_filtered | int | 重複除去件数 |
| quality_score_avg | float | 平均品質スコア |

### DetectionProcessor

**概要**: 検出後処理実行クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| logger | logging.Logger | ロガーインスタンス |
| settings | ProcessingSettings | 処理設定オブジェクト |
| validator | DataValidator | データ検証器 |
| stats | ProcessingStats | 処理統計オブジェクト |
| detection_history | List[DetectionResult] | 検出履歴リスト |

---

## 🔄 処理フロー

### 統合後処理フロー
```
1. process_detections()実行
   ↓
2. 信頼度フィルタリング
   ↓
3. サイズフィルタリング
   ↓
4. 重複除去
   ↓
5. 品質評価・統計更新
```

### CSV保存フロー
```
1. save_to_csv()実行
   ↓
2. ディレクトリ確認・作成
   ↓
3. ファイル名生成
   ↓
4. CSVヘッダー作成
   ↓
5. データ書き込み・保存
```

### 時系列分析フロー
```
1. analyze_temporal_patterns()実行
   ↓
2. 時系列データ作成
   ↓
3. 時間別グループ化
   ↓
4. パターン分析
   ↓
5. 分析結果生成
```

### エラー処理フロー
```
処理エラー発生
   ↓
例外キャッチ・ログ出力
   ↓
エラー統計更新
   ↓
部分的結果返却（可能な場合）
```

---

## 📝 実装メモ

### 注意事項
- 大量検出結果の効率的な処理
- IoU計算の最適化（ベクトル化）
- メモリ効率的な重複除去
- CSV保存時の文字エンコーディング
- 時系列分析でのタイムゾーン考慮

### 依存関係
- logging（標準ライブラリ）
- csv（標準ライブラリ）
- typing（標準ライブラリ）
- numpy（外部ライブラリ）
- pandas（外部ライブラリ）
- dataclasses（標準ライブラリ）
- pathlib（標準ライブラリ）
- datetime（標準ライブラリ）
- collections（標準ライブラリ）
- json（標準ライブラリ）
- models.detection_models（プロジェクト内モジュール）
- models.activity_models（プロジェクト内モジュール）
- utils.data_validator（プロジェクト内モジュール）
- utils.file_naming（プロジェクト内モジュール）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |