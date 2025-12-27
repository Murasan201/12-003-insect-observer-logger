# file_naming.py 処理説明書

**文書番号**: 12-003-PROC-006  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: file_naming.py 処理説明書  
**対象ファイル**: `utils/file_naming.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
システム内で使用するファイルの命名規則を統一管理し、一貫性のあるファイル名生成・解析機能を提供する。

### 主要機能
- 各種ファイルの命名規則定義
- 日付・時刻ベースのファイル名生成
- ファイル名パターンの解析・検証
- ディレクトリ構造の管理

---

## 🔧 関数・メソッド仕様

### FileNamingConvention.generate_detection_log_filename()

**概要**: 検出ログファイル名を生成

**処理内容**:
1. 指定日付をDATE_FORMAT形式に変換
2. DETECTION_LOG_PATTERNに日付を埋め込み
3. ファイル名文字列を生成

**入力インターフェース**:
```python
@classmethod
def generate_detection_log_filename(cls, target_date: date) -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| target_date | date | ○ | 対象日付 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filename | str | 生成されたファイル名 |

**使用例**:
```python
from datetime import date
target_date = date(2025, 7, 28)
filename = FileNamingConvention.generate_detection_log_filename(target_date)
# 結果: "detection_20250728.csv"
```

### FileNamingConvention.generate_image_filename()

**概要**: 画像ファイル名を生成

**処理内容**:
1. 指定日時をDATETIME_FORMAT形式に変換
2. シーケンス番号を3桁0埋めに変換
3. ファイルタイプに応じたパターンを選択
4. ファイル名文字列を生成

**入力インターフェース**:
```python
@classmethod
def generate_image_filename(cls, timestamp: datetime, sequence: int, 
                          image_type: str = "original") -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| timestamp | datetime | ○ | 撮影日時 |
| sequence | int | ○ | シーケンス番号 |
| image_type | str | × | 画像タイプ（"original", "annotated", "thumbnail"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filename | str | 生成されたファイル名 |

**使用例**:
```python
from datetime import datetime
timestamp = datetime(2025, 7, 28, 14, 30, 45)
filename = FileNamingConvention.generate_image_filename(timestamp, 5, "annotated")
# 結果: "20250728_143045_005_annotated.png"
```

### FileNamingConvention.generate_chart_filename()

**概要**: チャート・可視化ファイル名を生成

**処理内容**:
1. 指定日付をDATE_FORMAT形式に変換
2. チャートタイプに応じたパターンを選択
3. ファイル名文字列を生成

**入力インターフェース**:
```python
@classmethod
def generate_chart_filename(cls, target_date: date, chart_type: str) -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| target_date | date | ○ | 対象日付 |
| chart_type | str | ○ | チャートタイプ（"activity", "heatmap", "hourly", "trajectory", "dashboard"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filename | str | 生成されたファイル名 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ValueError | サポートされていないchart_typeが指定された場合 |

**使用例**:
```python
from datetime import date
target_date = date(2025, 7, 28)
filename = FileNamingConvention.generate_chart_filename(target_date, "activity")
# 結果: "activity_chart_20250728.png"
```

### FileNamingConvention.parse_filename()

**概要**: ファイル名から情報を抽出・解析

**処理内容**:
1. ファイル名パターンとの正規表現マッチング
2. 日付・時刻・シーケンス番号の抽出
3. ファイルタイプの判定
4. 解析結果辞書の生成

**入力インターフェース**:
```python
@classmethod
def parse_filename(cls, filename: str) -> Optional[Dict[str, Any]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| filename | str | ○ | 解析対象のファイル名 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| info | Optional[Dict[str, Any]] | 解析結果辞書（解析失敗時はNone） |

**使用例**:
```python
filename = "detection_20250728.csv"
info = FileNamingConvention.parse_filename(filename)
# 結果: {"type": "detection_log", "date": date(2025, 7, 28), "extension": "csv"}
```

### FileNamingConvention.validate_filename()

**概要**: ファイル名の妥当性を検証

**処理内容**:
1. ファイル名パターンとの照合
2. 日付・時刻の妥当性チェック
3. 文字数・文字種制限の確認
4. ファイル拡張子の適合性確認

**入力インターフェース**:
```python
@classmethod
def validate_filename(cls, filename: str, expected_type: str = None) -> Tuple[bool, List[str]]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| filename | str | ○ | 検証対象のファイル名 |
| expected_type | str | × | 期待するファイルタイプ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| is_valid | bool | 検証結果（True: 正常、False: 異常） |
| error_messages | List[str] | エラーメッセージリスト |

**使用例**:
```python
filename = "detection_20250728.csv"
is_valid, errors = FileNamingConvention.validate_filename(filename, "detection_log")
```

### FileNamingConvention.get_file_date_range()

**概要**: 指定期間のファイル名リストを生成

**処理内容**:
1. 開始日から終了日までの日付リストを生成
2. 各日付に対してファイル名を生成
3. ファイル名リストを返却

**入力インターフェース**:
```python
@classmethod
def get_file_date_range(cls, start_date: date, end_date: date, 
                       file_type: str) -> List[str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| start_date | date | ○ | 開始日付 |
| end_date | date | ○ | 終了日付 |
| file_type | str | ○ | ファイルタイプ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filenames | List[str] | 生成されたファイル名リスト |

**使用例**:
```python
from datetime import date
start = date(2025, 7, 25)
end = date(2025, 7, 28)
filenames = FileNamingConvention.get_file_date_range(start, end, "detection_log")
```

### FileNamingConvention.create_directory_structure()

**概要**: 推奨ディレクトリ構造を作成

**処理内容**:
1. ベースディレクトリの存在確認
2. 各種データ用サブディレクトリの作成
3. 権限設定の適用
4. 作成結果の報告

**入力インターフェース**:
```python
@classmethod
def create_directory_structure(cls, base_path: str) -> Dict[str, str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| base_path | str | ○ | ベースディレクトリパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| directory_map | Dict[str, str] | 作成されたディレクトリのマップ |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| PermissionError | ディレクトリ作成権限がない場合 |
| OSError | ファイルシステムエラーの場合 |

**使用例**:
```python
base_path = "/path/to/project"
directories = FileNamingConvention.create_directory_structure(base_path)
```

### FileNamingConvention.cleanup_old_files()

**概要**: 古いファイルのクリーンアップ

**処理内容**:
1. 指定ディレクトリ内のファイル一覧取得
2. ファイル名から日付を抽出
3. 保持期間を超えたファイルの特定
4. ファイルの削除実行

**入力インターフェース**:
```python
@classmethod
def cleanup_old_files(cls, directory: str, file_type: str, 
                     retention_days: int) -> Dict[str, int]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| directory | str | ○ | 対象ディレクトリ |
| file_type | str | ○ | ファイルタイプ |
| retention_days | int | ○ | 保持期間（日数） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| cleanup_result | Dict[str, int] | クリーンアップ結果統計 |

**使用例**:
```python
result = FileNamingConvention.cleanup_old_files("./logs", "detection_log", 30)
# 結果: {"deleted": 5, "kept": 25, "errors": 0}
```

---

## 📊 データ構造

### FileNamingConvention

**概要**: ファイル命名規則を管理するクラス

**主要定数**:
| 定数名 | 値 | 説明 |
|-------|---|------|
| DATE_FORMAT | "%Y%m%d" | 日付フォーマット |
| DATETIME_FORMAT | "%Y%m%d_%H%M%S" | 日時フォーマット |
| DETECTION_LOG_PATTERN | "detection_{date}.csv" | 検出ログファイルパターン |
| ORIGINAL_IMAGE_PATTERN | "{datetime}_{sequence:03d}.jpg" | 元画像ファイルパターン |

**ディレクトリ構造定義**:
| ディレクトリタイプ | パス | 用途 |
|------------------|------|------|
| logs | ./logs | ログファイル |
| data | ./data | データファイル |
| images | ./images | 画像ファイル |
| charts | ./charts | チャート・可視化ファイル |
| backup | ./backup | バックアップファイル |

---

## 🔄 処理フロー

### ファイル名生成フロー
```
1. 日付・時刻情報取得
   ↓
2. 指定フォーマットで文字列変換
   ↓
3. パターンテンプレートに埋め込み
   ↓
4. ファイル名文字列生成
```

### ファイル名解析フロー
```
1. ファイル名受け取り
   ↓
2. 正規表現パターンマッチング
   ↓
3. 日付・時刻・シーケンス抽出
   ↓
4. 解析結果辞書作成
```

### クリーンアップフロー
```
1. ディレクトリスキャン
   ↓
2. ファイル名解析
   ↓
3. 保持期間判定
   ↓
4. 古いファイル削除
   ↓
5. 結果レポート生成
```

---

## 📝 実装メモ

### 注意事項
- ファイル名の一意性を保証するためシーケンス番号を使用
- プラットフォーム固有の文字制限を考慮
- 長いファイル名によるパス長制限に注意
- ファイル削除時の権限・ロック状態の確認

### 依存関係
- os（標準ライブラリ）
- re（標準ライブラリ）
- datetime（標準ライブラリ）
- typing（標準ライブラリ）
- pathlib（標準ライブラリ）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |