# config_manager.py 処理説明書

**文書番号**: 12-003-PROC-004  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: config_manager.py 処理説明書  
**対象ファイル**: `config/config_manager.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-28  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
システム設定の読み込み・保存・検証・管理を行い、設定ファイルの操作とシステム設定オブジェクトの管理を提供する。

### 主要機能
- 設定ファイルの読み込み・保存
- システム設定の検証・更新
- デフォルト設定の生成
- 設定変更の追跡・ログ記録

---

## 🔧 関数・メソッド仕様

### ConfigManager.__init__()

**概要**: ConfigManagerクラスの初期化処理

**処理内容**:
1. 設定ファイルパスをPathlibオブジェクトに変換
2. 設定オブジェクトをNoneで初期化
3. ロガーインスタンスを取得
4. 設定ディレクトリが存在しない場合は作成

**入力インターフェース**:
```python
def __init__(self, config_path: str = "./config/system_config.json"):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config_path | str | × | 設定ファイルのパス（デフォルト: "./config/system_config.json"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | ConfigManager | 初期化されたConfigManagerオブジェクト |

**使用例**:
```python
config_manager = ConfigManager("./config/system_config.json")
```

### ConfigManager.load_config()

**概要**: 設定ファイルを読み込みSystemConfigurationオブジェクトを返す

**処理内容**:
1. 設定ファイルの存在確認
2. JSONファイルの読み込み
3. SystemConfiguration.load_from_file()を使用してオブジェクト化
4. 読み込み完了ログの出力

**入力インターフェース**:
```python
def load_config(self) -> SystemConfiguration:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| config | SystemConfiguration | 読み込まれたシステム設定 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| FileNotFoundError | 設定ファイルが存在しない場合 |
| json.JSONDecodeError | JSON形式が不正な場合 |
| ValueError | 設定値が不正な場合 |

**使用例**:
```python
config_manager = ConfigManager()
config = config_manager.load_config()
```

### ConfigManager.save_config()

**概要**: SystemConfigurationオブジェクトを設定ファイルに保存

**処理内容**:
1. 設定オブジェクトの検証実行
2. to_dict()で辞書形式に変換
3. JSON形式でファイルに書き込み
4. 保存完了ログの出力

**入力インターフェース**:
```python
def save_config(self, config: SystemConfiguration) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config | SystemConfiguration | ○ | 保存するシステム設定 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 保存完了後に処理終了 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| IOError | ファイル書き込みエラーの場合 |
| PermissionError | ファイルアクセス権限エラーの場合 |
| ValueError | 設定オブジェクトが不正な場合 |

**使用例**:
```python
config = SystemConfiguration()
config_manager.save_config(config)
```

### ConfigManager.get_default_config()

**概要**: デフォルト設定のSystemConfigurationオブジェクトを生成

**処理内容**:
1. SystemConfigurationのデフォルトコンストラクタを呼び出し
2. 基本的なシステム設定値を設定
3. validate_config()で検証を実行

**入力インターフェース**:
```python
def get_default_config(self) -> SystemConfiguration:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| default_config | SystemConfiguration | デフォルト設定オブジェクト |

**使用例**:
```python
config_manager = ConfigManager()
default_config = config_manager.get_default_config()
```

### ConfigManager.create_default_config_file()

**概要**: デフォルト設定ファイルを作成

**処理内容**:
1. get_default_config()でデフォルト設定を取得
2. save_config()でファイルに保存
3. 作成完了ログを出力

**入力インターフェース**:
```python
def create_default_config_file(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 作成完了後に処理終了 |

**使用例**:
```python
config_manager = ConfigManager()
config_manager.create_default_config_file()
```

### ConfigManager.update_config()

**概要**: 現在の設定を部分的に更新

**処理内容**:
1. 現在の設定を読み込み（なければデフォルト作成）
2. update_from_dict()で設定を更新
3. save_config()で更新後の設定を保存
4. 更新完了ログを出力

**入力インターフェース**:
```python
def update_config(self, updates: Dict[str, Any], updated_by: str = "system") -> SystemConfiguration:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| updates | Dict[str, Any] | ○ | 更新する設定項目の辞書 |
| updated_by | str | × | 更新者名（デフォルト: "system"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| updated_config | SystemConfiguration | 更新後の設定オブジェクト |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ValueError | 更新値が不正な場合 |

**使用例**:
```python
updates = {"detection_interval_seconds": 30, "log_level": "DEBUG"}
config_manager.update_config(updates, "admin")
```

### ConfigManager.validate_config_file()

**概要**: 設定ファイルの整合性を検証

**処理内容**:
1. 設定ファイルの存在確認
2. JSON形式の妥当性確認
3. 必須項目の存在確認
4. 各設定値の範囲・形式確認

**入力インターフェース**:
```python
def validate_config_file(self) -> Tuple[bool, List[str]]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| is_valid | bool | 検証結果（True: 正常、False: 異常） |
| error_messages | List[str] | エラーメッセージリスト |

**使用例**:
```python
is_valid, errors = config_manager.validate_config_file()
if not is_valid:
    print("設定エラー:", errors)
```

### ConfigManager.backup_config()

**概要**: 現在の設定ファイルをバックアップ

**処理内容**:
1. 現在の設定ファイルの存在確認
2. タイムスタンプ付きバックアップファイル名生成
3. ファイルのコピー実行
4. バックアップ完了ログ出力

**入力インターフェース**:
```python
def backup_config(self, backup_dir: Optional[str] = None) -> str:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| backup_dir | str | × | バックアップディレクトリ（デフォルト: "./config/backup"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| backup_path | str | 作成されたバックアップファイルのパス |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| FileNotFoundError | 元ファイルが存在しない場合 |
| IOError | バックアップファイル作成エラーの場合 |

**使用例**:
```python
backup_path = config_manager.backup_config("./backups")
```

---

## 📊 データ構造

### ConfigManager

**概要**: 設定管理を行うクラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| config_path | Path | 設定ファイルのパス |
| config | Optional[SystemConfiguration] | 現在の設定オブジェクト |
| logger | logging.Logger | ロガーインスタンス |

---

## 🔄 処理フロー

### 設定読み込みフロー
```
1. ConfigManager初期化
   ↓
2. load_config()実行
   ↓
3. ファイル存在確認
   ↓
4. JSON読み込み・パース
   ↓
5. SystemConfiguration作成
   ↓
6. 検証実行
```

### 設定更新フロー
```
1. update_config()実行
   ↓
2. 現在設定読み込み（またはデフォルト作成）
   ↓
3. 設定値更新
   ↓
4. 検証実行
   ↓
5. ファイル保存
```

### エラー処理フロー
```
設定エラー発生
   ↓
例外をキャッチ
   ↓
エラーログ出力
   ↓
デフォルト設定使用（または処理中断）
```

---

## 📝 実装メモ

### 注意事項
- Pathlibを使用してクロスプラットフォーム対応
- ディレクトリ作成時のパーミッション考慮
- 設定ファイルのアトミック書き込み（一時ファイル経由）
- バックアップ機能による設定変更の安全性確保

### 依存関係
- os（標準ライブラリ）
- json（標準ライブラリ）
- logging（標準ライブラリ）
- typing（標準ライブラリ）
- pathlib（標準ライブラリ）
- models.system_models（プロジェクト内モジュール）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-28 | 開発チーム | 初版作成 |