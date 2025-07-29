# system_models.py 処理説明書

**文書番号**: 12-002-PROC-003  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: system_models.py 処理説明書  
**対象ファイル**: `models/system_models.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
システム設定・ログ・状態管理に関連するデータ構造を定義し、システム全体の動作パラメータやログ記録の管理を提供する。

### 主要機能
- システム設定データクラス定義
- システムログレコードデータクラス定義
- 設定データの検証・保存・読み込み機能
- ログレコードの生成・フォーマット機能

---

## 🔧 関数・メソッド仕様

### SystemConfiguration.validate_config()

**概要**: システム設定データの妥当性検証

**処理内容**:
1. 検出間隔が正の値であることをチェック
2. カメラ解像度が有効な値であることをチェック
3. 信頼度閾値が0.0-1.0の範囲内であることをチェック
4. その他の数値パラメータの範囲チェック

**入力インターフェース**:
```python
def validate_config(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 検証成功時は何も返さない |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ValueError | 設定値が不正な範囲または形式の場合 |

**使用例**:
```python
config = SystemConfiguration()
config.validate_config()
```

### SystemConfiguration.to_dict()

**概要**: SystemConfigurationオブジェクトを辞書形式に変換

**処理内容**:
1. 全属性を辞書のキー・値ペアに変換
2. datetime属性をISO8601文字列に変換
3. 辞書オブジェクトを返却

**入力インターフェース**:
```python
def to_dict(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| config_dict | Dict[str, Any] | システム設定の辞書表現 |

**使用例**:
```python
config = SystemConfiguration()
config_dict = config.to_dict()
```

### SystemConfiguration.save_to_file()

**概要**: 設定データをJSONファイルに保存

**処理内容**:
1. to_dict()で設定データを辞書に変換
2. JSON形式でファイルに書き込み
3. 保存完了ログを出力

**入力インターフェース**:
```python
def save_to_file(self, file_path: str) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| file_path | str | ○ | 保存先ファイルパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 保存完了後に処理終了 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| IOError | ファイル書き込みエラーの場合 |
| PermissionError | ファイルアクセス権限エラーの場合 |

**使用例**:
```python
config = SystemConfiguration()
config.save_to_file("./config/system_config.json")
```

### SystemConfiguration.load_from_file()

**概要**: JSONファイルから設定データを読み込み（クラスメソッド）

**処理内容**:
1. 指定されたJSONファイルを読み込み
2. 辞書データをSystemConfigurationオブジェクトに変換
3. validate_config()で検証を実行

**入力インターフェース**:
```python
@classmethod
def load_from_file(cls, file_path: str) -> 'SystemConfiguration':
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| file_path | str | ○ | 読み込み元ファイルパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| config | SystemConfiguration | 読み込まれた設定オブジェクト |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| FileNotFoundError | ファイルが存在しない場合 |
| json.JSONDecodeError | JSON形式が不正な場合 |
| ValueError | 設定値が不正な場合 |

**使用例**:
```python
config = SystemConfiguration.load_from_file("./config/system_config.json")
```

### SystemConfiguration.update_from_dict()

**概要**: 辞書データから設定を更新

**処理内容**:
1. 渡された辞書の各キー・値を属性に設定
2. last_updatedを現在時刻に更新
3. validate_config()で検証を実行

**入力インターフェース**:
```python
def update_from_dict(self, config_dict: Dict[str, Any], updated_by: str = "system") -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config_dict | Dict[str, Any] | ○ | 更新する設定辞書 |
| updated_by | str | × | 更新者名（デフォルト: "system"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 更新完了後に処理終了 |

**使用例**:
```python
config = SystemConfiguration()
config.update_from_dict({"detection_interval_seconds": 30}, "admin")
```

### SystemLogRecord.create_log()

**概要**: ログレコードを生成（クラスメソッド）

**処理内容**:
1. 現在時刻をタイムスタンプとして設定
2. 一意のログIDを生成
3. SystemLogRecordオブジェクトを作成

**入力インターフェース**:
```python
@classmethod
def create_log(cls, level: str, message: str, module: str = "system", 
               details: Optional[Dict[str, Any]] = None) -> 'SystemLogRecord':
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| level | str | ○ | ログレベル（INFO, WARNING, ERROR等） |
| message | str | ○ | ログメッセージ |
| module | str | × | 発生モジュール名（デフォルト: "system"） |
| details | Dict[str, Any] | × | 詳細情報辞書 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| log_record | SystemLogRecord | 生成されたログレコード |

**使用例**:
```python
log = SystemLogRecord.create_log("INFO", "システム初期化完了", "main")
```

### SystemLogRecord.to_formatted_string()

**概要**: ログレコードをフォーマット済み文字列に変換

**処理内容**:
1. タイムスタンプ、レベル、モジュール、メッセージを整形
2. 詳細情報がある場合は追加で出力
3. 統一フォーマットの文字列を生成

**入力インターフェース**:
```python
def to_formatted_string(self) -> str:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| formatted_log | str | フォーマット済みログ文字列 |

**使用例**:
```python
log = SystemLogRecord.create_log("INFO", "システム初期化完了")
formatted = log.to_formatted_string()
```

---

## 📊 データ構造

### SystemConfiguration

**概要**: システム全体の動作パラメータを管理するデータクラス

**主要属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| config_version | str | 設定バージョン |
| last_updated | datetime | 最終更新時刻 |
| updated_by | str | 更新者 |
| detection_interval_seconds | int | 検出間隔（秒） |
| log_level | str | ログレベル |
| data_retention_days | int | データ保持期間（日） |
| camera_resolution_width | int | カメラ解像度幅 |
| camera_resolution_height | int | カメラ解像度高さ |
| confidence_threshold | float | 信頼度閾値 |
| movement_threshold_pixels | float | 移動判定閾値（ピクセル） |

### SystemLogRecord

**概要**: システムログレコードを表現するデータクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| log_id | str | 一意のログID（UUID） |
| timestamp | datetime | ログ記録時刻 |
| level | str | ログレベル |
| module | str | 発生モジュール名 |
| message | str | ログメッセージ |
| details | Dict[str, Any] | 詳細情報辞書 |

---

## 🔄 処理フロー

### 設定管理フロー
```
1. SystemConfigurationオブジェクト生成
   ↓
2. load_from_file()で設定ファイル読み込み
   ↓
3. validate_config()で設定検証
   ↓
4. update_from_dict()で設定更新（必要に応じて）
   ↓
5. save_to_file()で設定保存
```

### ログ記録フロー
```
1. SystemLogRecord.create_log()でログ生成
   ↓
2. to_formatted_string()でフォーマット
   ↓
3. ファイルまたはコンソールに出力
```

### エラー処理フロー
```
設定エラー発生
   ↓
ValueError例外をスロー
   ↓
エラーログを記録
   ↓
デフォルト設定で継続またはシステム停止
```

---

## 📝 実装メモ

### 注意事項
- datetime.now()のデフォルト値は実行時に評価される
- JSON保存時はdatetimeオブジェクトを文字列に変換する必要がある
- 設定ファイルの読み書きは排他制御を考慮する

### 依存関係
- dataclasses（標準ライブラリ）
- datetime（標準ライブラリ）
- typing（標準ライブラリ）
- uuid（標準ライブラリ）
- json（標準ライブラリ）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |