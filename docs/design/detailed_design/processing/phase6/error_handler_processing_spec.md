# error_handler.py 処理説明書

**文書番号**: 12-003-PROC-010  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: error_handler.py 処理説明書  
**対象ファイル**: `error_handler.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
システム全体の統一的なエラー処理とリカバリー機能を提供するエラーハンドリング統合管理モジュール。

### 主要機能
- エラー分類・重要度管理とコンテキスト記録
- エラーロギング・ファイル出力・レポート生成
- 自動リトライ・フォールバック処理
- エラー統計・分析・トレンド分析
- リカバリー戦略管理・アラート通知連携
- デコレーターベースのエラーハンドリング

---

## 🔧 関数・メソッド仕様

### __init__(config)

**概要**: エラーハンドリング統合管理クラスの初期化

**処理内容**:
1. 設定の保存・ロガー設定
2. エラー記録管理（deque, defaultdict）の初期化
3. リカバリー戦略（RetryStrategy, RestartStrategy）の設定
4. 統計情報オブジェクトの初期化
5. エラーハンドラー登録辞書の初期化
6. スレッド同期用ロックの設定
7. エラーログディレクトリ・ファイルの作成
8. エラー専用ロギング設定（_setup_error_logging）

**入力インターフェース**:
```python
def __init__(self, config: Dict[str, Any]):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config | Dict[str, Any] | ○ | エラーハンドリング設定辞書 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### handle_error(exception, context, severity, category)

**概要**: エラーを処理し記録する中核メソッド

**処理内容**:
1. スレッドロック取得
2. エラーレコード作成（_generate_error_id, timestamp, traceback取得）
3. エラー記録処理（_record_error）
4. 重要度に応じたリカバリー処理（_attempt_recovery）
5. 致命的エラー時のアラート通知（_send_alert）
6. エラーレコードの返却

**入力インターフェース**:
```python
def handle_error(self, exception: Exception, context: ErrorContext, severity: ErrorSeverity = ErrorSeverity.ERROR, category: ErrorCategory = ErrorCategory.UNKNOWN) -> ErrorRecord:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| exception | Exception | ○ | 発生した例外オブジェクト |
| context | ErrorContext | ○ | エラーコンテキスト情報 |
| severity | ErrorSeverity | × | エラー重要度（デフォルト: ERROR） |
| category | ErrorCategory | × | エラーカテゴリ（デフォルト: UNKNOWN） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| error_record | ErrorRecord | 処理済みエラー記録 |

**使用例**:
```python
try:
    dangerous_operation()
except Exception as e:
    context = ErrorContext(module_name="detector", function_name="detect_image")
    error_handler.handle_error(e, context, ErrorSeverity.ERROR, ErrorCategory.DETECTION)
```

---

### _generate_error_id()

**概要**: 一意のエラーIDを生成

**処理内容**:
1. 現在時刻の取得・フォーマット（YYYYMMDDHHMMSS）
2. エラー履歴の件数取得
3. エラーID生成（ERR-{timestamp}-{count:04d}形式）

**入力インターフェース**:
```python
def _generate_error_id(self) -> str:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| error_id | str | 一意のエラーID（例: ERR-20250729120000-0001） |

---

### _record_error(error)

**概要**: エラーを記録・保存・ログ出力

**処理内容**:
1. メモリ内記録（error_history, error_counts, module_errors）
2. 統計情報更新（_update_statistics）
3. ファイル記録（_save_error_to_file）
4. ログ出力（重要度に応じたレベル）

**入力インターフェース**:
```python
def _record_error(self, error: ErrorRecord):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| error | ErrorRecord | ○ | 記録するエラーレコード |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 記録処理完了 |

---

### _update_statistics(error)

**概要**: 統計情報を更新

**処理内容**:
1. 総エラー数のインクリメント
2. 重要度別カウント更新
3. カテゴリー別カウント更新
4. モジュール別カウント更新
5. エラー率計算（時間あたりエラー数）

**入力インターフェース**:
```python
def _update_statistics(self, error: ErrorRecord):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| error | ErrorRecord | ○ | 統計対象エラーレコード |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 統計情報更新完了 |

---

### _attempt_recovery(error)

**概要**: エラーリカバリーを試行

**処理内容**:
1. 登録されたリカバリー戦略の順次確認
2. 適用可能な戦略の判定（can_handle）
3. リカバリー処理の実行（recover）
4. 成功時の解決フラグ・時刻・手法の記録
5. リカバリー処理中のエラーハンドリング

**入力インターフェース**:
```python
def _attempt_recovery(self, error: ErrorRecord):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| error | ErrorRecord | ○ | リカバリー対象エラーレコード |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | リカバリー処理完了 |

---

### get_statistics()

**概要**: エラー統計情報を取得

**処理内容**:
1. スレッドロック取得
2. 最頻出エラーの計算・ソート
3. リカバリー成功率の計算
4. 平均リカバリー時間の算出
5. 統計情報オブジェクトの返却

**入力インターフェース**:
```python
def get_statistics(self) -> ErrorStatistics:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| statistics | ErrorStatistics | エラー統計情報 |

**戻り値構造**:
```python
ErrorStatistics {
    total_errors: int,                    # 総エラー数
    errors_by_severity: Dict[str, int],   # 重要度別エラー数
    errors_by_category: Dict[str, int],   # カテゴリ別エラー数
    errors_by_module: Dict[str, int],     # モジュール別エラー数
    error_rate_per_hour: float,           # 時間あたりエラー率
    most_frequent_errors: List[Dict],     # 最頻出エラー（上位10件）
    recovery_success_rate: float,         # リカバリー成功率（%）
    average_recovery_time_seconds: float  # 平均リカバリー時間
}
```

---

### get_recent_errors(count)

**概要**: 最近のエラーを取得

**処理内容**:
1. スレッドロック取得
2. エラー履歴から指定件数の最新エラーを取得
3. リスト形式での返却

**入力インターフェース**:
```python
def get_recent_errors(self, count: int = 10) -> List[ErrorRecord]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| count | int | × | 取得件数（デフォルト: 10） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| errors | List[ErrorRecord] | 最新エラーリスト |

---

### get_errors_by_module(module_name)

**概要**: モジュール別のエラーを取得

**処理内容**:
1. スレッドロック取得
2. 指定モジュールのエラー履歴取得
3. エラーリストの返却

**入力インターフェース**:
```python
def get_errors_by_module(self, module_name: str) -> List[ErrorRecord]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| module_name | str | ○ | 対象モジュール名 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| errors | List[ErrorRecord] | モジュール別エラーリスト |

---

### export_error_report(output_path)

**概要**: エラーレポートをエクスポート

**処理内容**:
1. レポート辞書の作成（統計情報・最新エラー・未解決重大エラー）
2. JSONファイルの生成・保存
3. ファイルパスの返却

**入力インターフェース**:
```python
def export_error_report(self, output_path: Path) -> Path:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| output_path | Path | ○ | 出力ディレクトリパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| report_file | Path | 生成されたレポートファイルパス |

**使用例**:
```python
report_path = error_handler.export_error_report(Path("logs/reports"))
print(f"エラーレポート生成: {report_path}")
```

---

### register_handler(category, handler)

**概要**: カテゴリー別のエラーハンドラーを登録

**処理内容**:
1. 指定カテゴリのハンドラーリストに追加
2. カスタムエラー処理の拡張機能

**入力インターフェース**:
```python
def register_handler(self, category: ErrorCategory, handler: Callable):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| category | ErrorCategory | ○ | エラーカテゴリ |
| handler | Callable | ○ | エラーハンドラー関数 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 登録完了 |

---

## 📊 データ構造

### ErrorSeverity (Enum)

**概要**: エラー重要度レベルの列挙型

**値**:
| 重要度 | 値 | 説明 |
|-------|---|------|
| DEBUG | "debug" | デバッグ情報 |
| INFO | "info" | 情報メッセージ |
| WARNING | "warning" | 警告（処理は継続） |
| ERROR | "error" | エラー（部分的な失敗） |
| CRITICAL | "critical" | 致命的エラー（システム停止が必要） |

### ErrorCategory (Enum)

**概要**: エラーカテゴリーの列挙型

**値**:
| カテゴリ | 値 | 説明 |
|---------|---|------|
| HARDWARE | "hardware" | ハードウェア関連エラー |
| NETWORK | "network" | ネットワーク関連エラー |
| DETECTION | "detection" | 検出処理関連エラー |
| PROCESSING | "processing" | データ処理関連エラー |
| STORAGE | "storage" | ストレージ関連エラー |
| CONFIGURATION | "configuration" | 設定関連エラー |
| RESOURCE | "resource" | リソース不足エラー |
| PERMISSION | "permission" | 権限関連エラー |
| VALIDATION | "validation" | データ検証関連エラー |
| UNKNOWN | "unknown" | 不明なエラー |

### ErrorContext

**概要**: エラーコンテキスト情報

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| module_name | str | エラー発生モジュール名 |
| function_name | str | エラー発生関数名 |
| input_data | Optional[Dict[str, Any]] | 入力データ情報 |
| state_info | Optional[Dict[str, Any]] | 状態情報 |
| retry_count | int | リトライ回数 |
| max_retries | int | 最大リトライ回数 |
| recovery_attempted | bool | リカバリー試行フラグ |
| recovery_successful | bool | リカバリー成功フラグ |

### ErrorRecord

**概要**: エラー記録データ

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| error_id | str | 一意のエラーID |
| timestamp | str | エラー発生時刻（ISO形式） |
| severity | ErrorSeverity | エラー重要度 |
| category | ErrorCategory | エラーカテゴリ |
| error_type | str | エラー型名 |
| error_message | str | エラーメッセージ |
| traceback | str | スタックトレース |
| context | ErrorContext | エラーコンテキスト |
| resolved | bool | 解決済みフラグ |
| resolution_time | Optional[str] | 解決時刻 |
| resolution_method | Optional[str] | 解決手法 |
| impact_assessment | Optional[str] | 影響評価 |

---

## 🔄 処理フロー

### エラー処理フロー
```
例外発生
   ↓
handle_error呼び出し
   ↓
エラーレコード作成
   ├─ エラーID生成
   ├─ タイムスタンプ記録
   ├─ トレースバック取得
   └─ コンテキスト保存
   ↓
エラー記録処理（_record_error）
   ├─ メモリ内記録
   ├─ 統計情報更新
   ├─ ファイル保存
   └─ ログ出力
   ↓
リカバリー処理（重要度がERROR/CRITICAL時）
   ├─ 戦略選択
   ├─ リカバリー実行
   └─ 結果記録
   ↓
アラート通知（CRITICAL時）
   ↓
エラーレコード返却
```

### リカバリー戦略フロー
```
エラーレコード受信
   ↓
戦略適用判定（can_handle）
   ├─ RetryStrategy: ネットワーク・リソースエラー
   └─ RestartStrategy: ハードウェアエラー
   ↓
リカバリー実行（recover）
   ├─ RetryStrategy: 指数バックオフでリトライ
   └─ RestartStrategy: モジュール再起動要求
   ↓
成功時: 解決フラグ・時刻・手法記録
   ↓
失敗時: 次戦略へ移行または諦め
```

---

## 🛠️ デコレーター機能

### error_handler_decorator

**概要**: 関数にエラーハンドリングを自動適用するデコレーター

**使用例**:
```python
@error_handler_decorator(
    handler=error_handler,
    severity=ErrorSeverity.ERROR,
    category=ErrorCategory.DETECTION,
    max_retries=3
)
def detect_insect(image_path):
    # 検出処理（例外が発生する可能性）
    return detection_result
```

**機能**:
- 自動リトライ機能
- エラーコンテキストの自動生成
- 統一的なエラー処理

---

## 📝 実装メモ

### 注意事項
- スレッドセーフなエラー記録・統計更新
- メモリ効率的なエラー履歴管理（deque使用）
- ファイルI/Oエラーのハンドリング
- リカバリー処理中の例外処理

### 依存関係
- logging: 標準ログ出力・ファイル出力
- threading: スレッド同期・ロック制御
- collections: deque・defaultdict（効率的なデータ管理）
- pathlib: ファイルパス操作
- json: エラーレポートのシリアライゼーション

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |