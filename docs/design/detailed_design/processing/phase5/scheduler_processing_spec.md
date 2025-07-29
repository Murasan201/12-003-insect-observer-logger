# scheduler.py 処理説明書

**文書番号**: 12-002-PROC-009  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: scheduler.py 処理説明書  
**対象ファイル**: `scheduler.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
定期的な検出・分析処理のスケジューリングと実行管理を行うスケジューラー管理モジュール。

### 主要機能
- 定期検出処理のスケジューリング
- 日次分析処理の自動実行
- タスクキューとジョブ管理
- スケジュール動的変更・一時停止
- 障害時の自動復旧・リトライ
- パフォーマンス統計・監視

---

## 🔧 関数・メソッド仕様

### __init__(detection_interval, analysis_time)

**概要**: スケジューラー管理クラスの初期化

**処理内容**:
1. ロガー設定
2. 検出間隔・分析時刻の設定
3. タスク管理辞書の初期化
4. スケジューラー状態管理の初期化
5. 統計情報オブジェクトの初期化
6. スレッド管理・同期イベントの設定

**入力インターフェース**:
```python
def __init__(self, detection_interval: int = 300, analysis_time: str = "23:00"):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detection_interval | int | × | 検出間隔（秒、デフォルト: 300秒=5分） |
| analysis_time | str | × | 日次分析時刻（HH:MM形式、デフォルト: "23:00"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### schedule_detection(detection_function)

**概要**: 定期検出処理のスケジューリング

**処理内容**:
1. 検出タスクの作成（ScheduledTask）
2. 次回実行時刻の計算（現在時刻 + 検出間隔）
3. タスク辞書への登録
4. ログ出力・成功可否の返却

**入力インターフェース**:
```python
def schedule_detection(self, detection_function: Callable) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| detection_function | Callable | ○ | 検出処理を実行する関数 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | スケジューリング成功可否 |

**使用例**:
```python
scheduler.schedule_detection(system._perform_detection_cycle)
```

---

### schedule_daily_analysis(analysis_function)

**概要**: 日次分析処理のスケジューリング

**処理内容**:
1. 分析時刻の解析（時:分形式）
2. 次回実行時刻の計算（当日または翌日の指定時刻）
3. 分析タスクの作成・登録
4. 24時間間隔での定期実行設定

**入力インターフェース**:
```python
def schedule_daily_analysis(self, analysis_function: Callable) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| analysis_function | Callable | ○ | 分析処理を実行する関数 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | スケジューリング成功可否 |

**使用例**:
```python
scheduler.schedule_daily_analysis(system._perform_daily_analysis)
```

---

### schedule_custom_task(task_id, name, function, interval_seconds, delay_seconds)

**概要**: カスタムタスクのスケジューリング

**処理内容**:
1. 既存タスクID重複チェック・警告
2. 初回実行遅延時間を考慮した次回実行時刻計算
3. カスタムScheduledTaskの作成
4. タスク辞書への登録・ログ出力

**入力インターフェース**:
```python
def schedule_custom_task(self, task_id: str, name: str, function: Callable, interval_seconds: int, delay_seconds: int = 0) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| task_id | str | ○ | 一意のタスクID |
| name | str | ○ | タスク名（表示用） |
| function | Callable | ○ | 実行する関数 |
| interval_seconds | int | ○ | 実行間隔（秒） |
| delay_seconds | int | × | 初回実行遅延（秒、デフォルト: 0） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | スケジューリング成功可否 |

**使用例**:
```python
scheduler.schedule_custom_task("backup_task", "Daily Backup", backup_function, 86400, 3600)
```

---

### start()

**概要**: スケジューラーの開始

**処理内容**:
1. 実行状態チェック（重複開始防止）
2. スケジューラー状態フラグの設定
3. 開始時刻の記録・終了イベントのクリア
4. スケジューラーループスレッドの作成・開始
5. 成功ログ出力・成功可否返却

**入力インターフェース**:
```python
def start(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | スケジューラー開始成功可否 |

**使用例**:
```python
if scheduler.start():
    print("Scheduler started successfully")
```

---

### stop()

**概要**: スケジューラーの停止

**処理内容**:
1. 実行状態チェック・停止処理開始ログ
2. 実行状態フラグの無効化・終了イベントの設定
3. 実行中タスクの完了待機（_wait_for_tasks_completion）
4. スケジューラースレッドの終了待機
5. 停止完了ログ・成功可否返却

**入力インターフェース**:
```python
def stop(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | スケジューラー停止成功可否 |

**使用例**:
```python
scheduler.stop()
```

---

### pause_detection(duration_seconds)

**概要**: 検出処理の一時停止

**処理内容**:
1. 検出タスクの存在確認
2. 次回実行時刻の延期（現在時刻 + 停止時間）
3. タスク無効化（enabled=False）
4. 自動再開スレッドの作成・開始
5. 停止時間経過後の自動再開処理

**入力インターフェース**:
```python
def pause_detection(self, duration_seconds: int) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| duration_seconds | int | ○ | 停止時間（秒） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 一時停止処理完了 |

**使用例**:
```python
scheduler.pause_detection(300)  # 5分間停止
```

---

### update_detection_interval(new_interval)

**概要**: 検出間隔の動的更新

**処理内容**:
1. 検出タスクの存在確認
2. タスクの実行間隔更新
3. 次回実行時刻の新間隔での再計算
4. インスタンス変数の更新・ログ出力

**入力インターフェース**:
```python
def update_detection_interval(self, new_interval: int) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| new_interval | int | ○ | 新しい検出間隔（秒） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 間隔更新成功可否 |

**使用例**:
```python
scheduler.update_detection_interval(600)  # 10分間隔に変更
```

---

### _scheduler_loop()

**概要**: メインスケジューラーループ（別スレッド実行）

**処理内容**:
1. 実行状態・終了イベントの監視ループ
2. 実行すべきタスクのチェック・実行（_check_and_execute_tasks）
3. 統計情報の更新（_update_stats）
4. 1秒間隔での待機・継続
5. エラーハンドリング・5秒待機での復旧

**入力インターフェース**:
```python
def _scheduler_loop(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | ループ終了・実行状態無効化 |

---

### _check_and_execute_tasks()

**概要**: 実行すべきタスクのチェック・実行判定

**処理内容**:
1. 現在時刻の取得
2. 全タスクの状態・実行時刻チェック
3. 実行条件判定（有効・非実行中・実行時刻到達）
4. 条件一致タスクの実行開始（_execute_task）

**入力インターフェース**:
```python
def _check_and_execute_tasks(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | タスクチェック・実行処理完了 |

---

### _execute_task(task)

**概要**: 指定タスクの実行開始

**処理内容**:
1. タスク状態を実行中に変更
2. 最終実行時刻の記録
3. タスクランナースレッドの作成
4. スレッド開始・管理辞書への登録
5. エラー時の状態更新・エラー統計更新

**入力インターフェース**:
```python
def _execute_task(self, task: ScheduledTask) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| task | ScheduledTask | ○ | 実行するタスクオブジェクト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | タスク実行開始完了 |

---

### _task_runner(task)

**概要**: タスク実行ランナー（別スレッド実行）

**処理内容**:
1. 実行開始時刻の記録
2. タスク関数の実行
3. 実行時間の計算・統計更新
4. タスク状態の更新（完了・失敗）
5. 次回実行時刻の計算・設定
6. エラー時のリトライ制御・統計更新

**入力インターフェース**:
```python
def _task_runner(self, task: ScheduledTask) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| task | ScheduledTask | ○ | 実行するタスクオブジェクト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | タスク実行完了・状態更新 |

---

### get_scheduler_status()

**概要**: スケジューラー状態情報の取得

**処理内容**:
1. 現在の実行状態・統計情報の取得
2. 各タスクの状態・次回実行時刻の収集
3. 稼働時間の計算
4. 包括的な状態辞書の作成・返却

**入力インターフェース**:
```python
def get_scheduler_status(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| status | Dict[str, Any] | スケジューラー状態辞書 |

**戻り値構造**:
```python
{
    "running": bool,                   # 実行状態
    "paused": bool,                   # 一時停止状態
    "uptime_seconds": float,          # 稼働時間
    "stats": {...},                   # 統計情報
    "tasks": {                        # タスク状態
        "task_id": {
            "name": str,
            "status": str,
            "next_run": str,
            "run_count": int,
            "error_count": int
        }
    }
}
```

---

## 📊 データ構造

### TaskStatus (Enum)

**概要**: タスクの実行状態を表す列挙型

**値**:
| 状態名 | 値 | 説明 |
|-------|---|------|
| PENDING | "pending" | 実行待機中 |
| RUNNING | "running" | 実行中 |
| COMPLETED | "completed" | 実行完了 |
| FAILED | "failed" | 実行失敗 |
| CANCELLED | "cancelled" | キャンセル |

### ScheduledTask

**概要**: スケジュールされたタスクの情報

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| task_id | str | 一意のタスクID |
| name | str | タスク名（表示用） |
| function | Callable | 実行する関数 |
| interval_seconds | int | 実行間隔（秒） |
| next_run_time | datetime | 次回実行時刻 |
| last_run_time | Optional[datetime] | 最終実行時刻 |
| status | TaskStatus | 現在のタスク状態 |
| run_count | int | 実行回数 |
| error_count | int | エラー回数 |
| last_error | str | 最新エラーメッセージ |
| enabled | bool | タスク有効フラグ |
| max_retries | int | 最大リトライ回数 |

### SchedulerStats

**概要**: スケジューラーの統計情報

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| total_tasks_executed | int | 総実行タスク数 |
| successful_executions | int | 成功実行数 |
| failed_executions | int | 失敗実行数 |
| current_active_tasks | int | 現在アクティブなタスク数 |
| scheduler_uptime_seconds | float | スケジューラー稼働時間 |
| last_execution_time | str | 最終実行時刻 |
| average_execution_time_ms | float | 平均実行時間（ミリ秒） |

---

## 🔄 処理フロー

### スケジューラー起動フロー
```
1. スケジューラー初期化（__init__）
   ↓
2. タスクスケジューリング
   ├─ 検出タスク（schedule_detection）
   └─ 分析タスク（schedule_daily_analysis）
   ↓
3. スケジューラー開始（start）
   ↓
4. メインループ開始（_scheduler_loop）
   ↓
5. タスク監視・実行ループ
```

### タスク実行フロー
```
タスク実行時刻到達
   ↓
タスク実行判定（_check_and_execute_tasks）
   ↓
タスク実行開始（_execute_task）
   ↓
別スレッドでタスク実行（_task_runner）
   ↓
実行結果・統計更新
   ↓
次回実行時刻設定
```

### エラー・リトライフロー
```
タスク実行エラー
   ↓
エラー回数カウント・ログ出力
   ↓
最大リトライ回数チェック
   ├─ 未達成: リトライ実行
   └─ 超過: タスク失敗設定
   ↓
統計更新・次回実行設定
```

---

## 📝 実装メモ

### 注意事項
- 全タスクは別スレッドで非同期実行
- スレッドセーフなタスク管理・状態更新
- 終了時の実行中タスク完了待機
- 一時停止時の自動再開スレッド管理

### 依存関係
- threading: スレッド管理・同期制御
- datetime: 時刻計算・スケジューリング
- logging: ログ出力・デバッグ情報
- collections: デフォルト辞書・統計管理

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |