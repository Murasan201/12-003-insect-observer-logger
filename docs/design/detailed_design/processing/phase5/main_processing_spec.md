# main.py 処理説明書

**文書番号**: 12-002-PROC-007  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: main.py 処理説明書  
**対象ファイル**: `main.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
昆虫自動観察システムの中央制御モジュール。全システムの統合管理とライフサイクル制御を行う。

### 主要機能
- システム初期化・終了処理
- 定期実行スケジューリング
- 各モジュール間の連携制御
- エラーハンドリングと復旧処理
- システム状態監視・ヘルスチェック
- 設定動的更新・リロード

---

## 🔧 関数・メソッド仕様

### __init__(config_path)

**概要**: 昆虫観察システムのメインコントローラー初期化

**処理内容**:
1. ロガー設定
2. 設定管理器（ConfigManager）の初期化
3. システム設定の読み込み
4. システム状態オブジェクト初期化
5. エラーハンドリング・監視機能の初期化
6. 各モジュールインスタンス変数の初期化
7. シグナルハンドラー設定（SIGINT, SIGTERM）

**入力インターフェース**:
```python
def __init__(self, config_path: str = "./config/system_config.json"):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config_path | str | × | 設定ファイルパス（デフォルト: "./config/system_config.json"） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### initialize_system()

**概要**: システム全体の初期化処理

**処理内容**:
1. システム監視の開始
2. モデル管理器の初期化・自動セットアップ
3. ハードウェア制御器の初期化
4. 検出器の初期化・設定適用
5. 検出処理器の初期化
6. 活動量算出器の初期化
7. データ処理器の初期化
8. 可視化器の初期化
9. システム制御器の初期化
10. スケジューラーの初期化・設定
11. システム状態の更新

**入力インターフェース**:
```python
def initialize_system(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 初期化成功可否 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| ConfigurationError | 設定ファイル不正・モジュール初期化失敗 |
| HardwareError | ハードウェア初期化失敗 |

**使用例**:
```python
system = InsectObserverSystem()
if system.initialize_system():
    system.run_main_loop()
```

---

### run_main_loop()

**概要**: システムメインループの実行

**処理内容**:
1. システム状態の更新（is_running=True, current_mode="detecting"）
2. 監視スレッドの開始（_system_monitoring_loop）
3. スケジューラーの開始
4. メインループの実行：
   - システム状態更新（_update_system_status）
   - 設定更新チェック（_check_config_updates）
   - 定期ヘルスチェック実行
   - 1秒間隔での待機
5. エラー処理・復旧機能
6. 終了条件の監視（shutdown_requested）

**入力インターフェース**:
```python
def run_main_loop(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | ループ終了後に処理完了 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| KeyboardInterrupt | ユーザーによる中断（Ctrl+C） |
| SystemError | システム致命的エラー |

---

### shutdown_system()

**概要**: システムの安全な終了処理

**処理内容**:
1. 終了要求フラグの設定
2. スケジューラーの停止
3. 監視スレッドの停止・合流
4. ハードウェア制御器のクリーンアップ
5. システム監視の停止
6. 最終ログ出力・リソース解放

**入力インターフェース**:
```python
def shutdown_system(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 終了処理完了 |

---

### _perform_detection_cycle()

**概要**: 1回の検出サイクル実行

**処理内容**:
1. システム制御器を使用した統合検出ワークフロー実行
2. 検出結果の取得・検証
3. 検出統計の更新
4. 最終検出時刻の記録
5. エラーハンドリング・ログ出力

**入力インターフェース**:
```python
def _perform_detection_cycle(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| result | Dict[str, Any] | 検出結果辞書 |

**戻り値構造**:
```python
{
    "success": bool,           # 検出成功可否
    "detection_count": int,    # 検出された昆虫数
    "timestamp": str,          # 検出時刻
    "confidence": float,       # 平均信頼度
    "error": str              # エラーメッセージ（失敗時）
}
```

---

### _perform_daily_analysis()

**概要**: 日次分析処理の実行

**処理内容**:
1. 前日の検出データ読み込み
2. データ処理器による前処理・クリーニング
3. 活動量算出器による活動指標計算
4. 時間別サマリーの生成
5. 可視化器による包括レポート生成
6. エラーハンドリング・状態管理

**入力インターフェース**:
```python
def _perform_daily_analysis(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 分析処理完了（レポートファイル生成） |

---

### _system_monitoring_loop()

**概要**: システム監視ループ（別スレッド実行）

**処理内容**:
1. システムリソース監視（_monitor_system_resources）
2. モジュール健全性チェック（_check_module_health）
3. 30秒間隔での定期実行
4. エラー処理・継続性確保

**入力インターフェース**:
```python
def _system_monitoring_loop(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 監視ループ終了 |

---

### _monitor_system_resources()

**概要**: システムリソースの監視

**処理内容**:
1. CPU温度の取得・閾値チェック
2. 高温時の警告ログ出力
3. 危険温度時の検出一時停止（85℃以上で5分間）
4. ハードウェア状態の確認

**入力インターフェース**:
```python
def _monitor_system_resources(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | リソース監視完了 |

---

### _check_module_health()

**概要**: 各モジュールの健全性チェック

**処理内容**:
1. ハードウェア制御器の状態確認
2. 検出器の初期化状態確認
3. 他モジュールの状態取得
4. 問題のあるモジュールの警告出力

**入力インターフェース**:
```python
def _check_module_health(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | ヘルスチェック完了 |

---

### run_single_detection()

**概要**: 単発検出の実行（外部API）

**処理内容**:
1. システム初期化状態の確認
2. 必要に応じたシステム初期化
3. 検出サイクルの実行
4. 結果の返却

**入力インターフェース**:
```python
def run_single_detection(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| result | Dict[str, Any] | 検出結果または初期化エラー |

**使用例**:
```python
result = system.run_single_detection()
if result.get("success"):
    print(f"Detected {result['detection_count']} insects")
```

---

### run_analysis_for_date(date)

**概要**: 指定日の分析実行（外部API）

**処理内容**:
1. システム初期化状態の確認
2. 指定日の検出データ読み込み
3. 活動量指標の算出
4. 可視化レポートの生成
5. 成功可否の返却

**入力インターフェース**:
```python
def run_analysis_for_date(self, date: str) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| date | str | ○ | 分析対象日（YYYY-MM-DD形式） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 分析成功可否 |

**使用例**:
```python
if system.run_analysis_for_date("2025-07-29"):
    print("Analysis completed successfully")
```

---

## 📊 データ構造

### SystemStatus

**概要**: システムの実行状態情報

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| is_running | bool | システム稼働状態 |
| start_time | str | システム開始時刻（ISO形式） |
| uptime_seconds | float | 稼働時間（秒） |
| total_detections | int | 総検出数 |
| total_images_processed | int | 総処理画像数 |
| last_detection_time | str | 最終検出時刻 |
| current_mode | str | 現在のモード（idle/detecting/analyzing/maintenance） |
| error_count | int | エラー発生回数 |
| last_error | str | 最新エラーメッセージ |

---

## 🔄 処理フロー

### システム起動フロー
```
1. インスタンス初期化（__init__）
   ↓
2. システム初期化（initialize_system）
   ↓
3. メインループ開始（run_main_loop）
   ↓
4. 監視スレッド開始
   ↓
5. スケジューラー開始
   ↓
6. 定期処理ループ
```

### 検出サイクルフロー
```
スケジューラー定期実行
   ↓
検出サイクル実行（_perform_detection_cycle）
   ↓
システム制御器連携
   ↓
検出結果記録・統計更新
   ↓
次回実行待機
```

### 終了処理フロー
```
シグナル受信またはエラー
   ↓
終了要求設定（shutdown_requested=True）
   ↓
メインループ終了
   ↓
システム終了処理（shutdown_system）
   ↓
リソース解放・クリーンアップ
```

---

## 📝 実装メモ

### 注意事項
- 全モジュールの初期化順序に依存関係あり
- シグナルハンドリングによる安全な終了処理
- スレッド管理とリソース競合の回避
- 設定ファイル更新の動的検知・リロード

### 依存関係
- config.config_manager: システム設定管理
- hardware_controller: ハードウェア制御統合
- insect_detector: 昆虫検出機能
- system_controller: システム統合制御
- error_handler: エラーハンドリング統合
- monitoring: システム監視機能
- 全Phase 1-7モジュール

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |