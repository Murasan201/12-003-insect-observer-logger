# simple_observer.py 処理説明書

**文書番号**: 12-002-PROC-301  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: simple_observer.py 処理説明書  
**対象ファイル**: `simple_observer.py`  
**バージョン**: 1.0  
**作成日**: 2025-08-13  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
既存のinsect_detector.pyを活用し、継続的な昆虫観測を簡単操作で実現するシンプルな観測アプリケーション。初心者・研究者向けに最小限の設定で長時間の自動観測を可能にする。

### 主要機能
- 既存検出器の内部呼び出しによる観測実行
- 指定間隔での継続的な自動観測
- CSV形式での観測データ自動保存
- リアルタイムログ出力と統計表示
- Ctrl+Cによる安全な停止機能
- エラー発生時の継続実行

### 設計思想
- **既存システム無変更**: main.py、insect_detector.pyを一切変更しない
- **シンプル操作**: 最小限のコマンドライン引数
- **堅牢性**: エラー発生時も観測継続
- **データ完整性**: CSV書き込みの確実性保証

---

## 🔧 関数・メソッド仕様

### SimpleObserver.__init__()

**概要**: シンプル観測クラスの初期化処理

**処理内容**:
1. 観測パラメータ（間隔・時間・出力先）の設定
2. 出力ディレクトリの作成
3. ログシステムの初期化
4. 検出器設定（DetectionSettings）の構築
5. 内部変数（実行状態・統計）の初期化
6. シグナルハンドラー（Ctrl+C対応）の設定

**入力インターフェース**:
```python
def __init__(self, interval: int = 60, 
             duration: Optional[int] = None, 
             output_dir: str = "./simple_logs"):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| interval | int | × | 観測間隔（秒）デフォルト: 60 |
| duration | Optional[int] | × | 観測時間（秒）None: 無制限 |
| output_dir | str | × | 出力ディレクトリパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| インスタンス | SimpleObserver | 初期化済み観測オブジェクト |

**使用例**:
```python
# デフォルト設定
observer = SimpleObserver()

# カスタム設定
observer = SimpleObserver(interval=30, duration=3600, output_dir="./my_logs")
```

---

### SimpleObserver._setup_logging()

**概要**: ログシステムの設定と初期化

**処理内容**:
1. ログファイル名生成（タイムスタンプ付き）
2. ログレベル設定（INFO）
3. ログフォーマット設定（時刻・レベル・メッセージ）
4. ファイル・コンソール両方への出力設定
5. ロガーインスタンスの取得・保存

**入力インターフェース**:
```python
def _setup_logging(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | ログ設定完了 |

**生成ファイル**: `observer_YYYYMMDD_HHMMSS.log`

---

### SimpleObserver._signal_handler()

**概要**: シグナル（Ctrl+C）による安全停止処理

**処理内容**:
1. 受信シグナルの識別
2. 停止メッセージのログ出力
3. 観測ループの停止フラグ設定
4. stop()メソッドの呼び出し

**入力インターフェース**:
```python
def _signal_handler(self, signum: int, frame) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| signum | int | ○ | シグナル番号 |
| frame | FrameType | ○ | フレーム情報 |

**対応シグナル**: SIGINT (Ctrl+C), SIGTERM

---

### SimpleObserver._setup_csv()

**概要**: CSV出力ファイルの設定と初期化

**処理内容**:
1. CSVファイル名生成（タイムスタンプ付き）
2. 出力ディレクトリの確認・作成
3. CSVファイルのオープン（UTF-8エンコーディング）
4. CSVライター（csv.writer）の初期化
5. ヘッダー行の書き込み
6. バッファフラッシュの実行

**入力インターフェース**:
```python
def _setup_csv(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | CSV設定成功可否 |

**CSVヘッダー**:
```csv
timestamp,detection_count,has_detection,confidence_avg,x_center_avg,y_center_avg,processing_time_ms,observation_number
```

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| IOError | ファイル作成・書き込み権限エラー |
| OSError | ディスク容量不足 |

---

### SimpleObserver.initialize()

**概要**: 観測システム全体の初期化処理

**処理内容**:
1. 初期化開始ログの出力
2. CSV出力システムの設定（_setup_csv）
3. InsectDetector インスタンスの作成
4. 検出器の初期化実行（detector.initialize）
5. 初期化結果の検証・ログ出力
6. 観測設定（間隔・時間）の表示

**入力インターフェース**:
```python
def initialize(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 全体初期化成功可否 |

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| Exception | 検出器初期化失敗 |

**使用例**:
```python
observer = SimpleObserver()
if observer.initialize():
    print("初期化成功")
else:
    print("初期化失敗")
```

---

### SimpleObserver.start_observation()

**概要**: 観測のメインループ実行・制御

**処理内容**:
1. 初期化処理の実行・確認
2. 実行状態フラグの設定
3. 開始時刻・統計カウンターの初期化
4. 観測開始ログの出力
5. **メインループ**:
   - 単一観測の実行（_perform_single_observation）
   - 観測結果のCSV保存（_save_observation_to_csv）
   - 結果のログ出力（_log_observation_result）
   - 終了条件の確認（時間・ユーザー中断）
   - 次回観測までの待機（time.sleep）
6. 例外処理とクリーンアップ

**入力インターフェース**:
```python
def start_observation(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 観測完了・停止 |

**実行フロー**:
```
初期化 → 開始ログ → [観測ループ] → 終了処理
                     ↓     ↑
              単一観測 → 結果保存 → 待機
```

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| KeyboardInterrupt | ユーザー中断（Ctrl+C） |
| Exception | 観測処理中のエラー |

---

### SimpleObserver._perform_single_observation()

**概要**: 単一回の観測処理実行

**処理内容**:
1. 観測回数カウンターの増加
2. 処理開始時刻の記録
3. **検出実行**: `detector.detect_single_image(use_ir_led=True, save_result=True)`
4. 処理時間の計算（ミリ秒）
5. 検出結果の解析:
   - 検出数の取得
   - 検出有無フラグの設定
   - 平均信頼度の計算
   - 平均座標（X, Y）の計算
6. 観測データ辞書の生成
7. エラー処理・ログ出力

**入力インターフェース**:
```python
def _perform_single_observation(self) -> Optional[Dict[str, Any]]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| observation_data | Optional[Dict[str, Any]] | 観測結果データ（失敗時None） |

**出力データ構造**:
```python
{
    'timestamp': str,           # ISO形式時刻
    'detection_count': int,     # 検出昆虫数
    'has_detection': bool,      # 検出有無
    'confidence_avg': float,    # 平均信頼度（3桁）
    'x_center_avg': float,      # X座標平均（1桁）
    'y_center_avg': float,      # Y座標平均（1桁）
    'processing_time_ms': float,# 処理時間（1桁）
    'observation_number': int   # 観測連番
}
```

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| Exception | 検出処理失敗 |

---

### SimpleObserver._save_observation_to_csv()

**概要**: 観測結果のCSV書き込み処理

**処理内容**:
1. CSVライターの存在確認
2. 観測データから行データの構築
3. CSV行の書き込み（csv.writer.writerow）
4. バッファの即座フラッシュ（.flush）
5. エラー処理・ログ出力

**入力インターフェース**:
```python
def _save_observation_to_csv(self, observation_data: Dict[str, Any]) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| observation_data | Dict[str, Any] | ○ | 観測結果データ辞書 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | CSV書き込み完了 |

**書き込み順序**:
```python
row = [
    observation_data['timestamp'],
    observation_data['detection_count'],
    observation_data['has_detection'],
    observation_data['confidence_avg'],
    observation_data['x_center_avg'],
    observation_data['y_center_avg'],
    observation_data['processing_time_ms'],
    observation_data['observation_number']
]
```

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| Exception | CSV書き込みエラー |

---

### SimpleObserver._log_observation_result()

**概要**: 観測結果のコンソール・ログ出力

**処理内容**:
1. 検出有無による分岐処理
2. **検出あり**: 検出数・信頼度・処理時間の表示
3. **検出なし**: 未検出・処理時間の表示
4. 観測番号の表示
5. INFO レベルでのログ出力

**入力インターフェース**:
```python
def _log_observation_result(self, result: Dict[str, Any]) -> None:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| result | Dict[str, Any] | ○ | 観測結果データ |

**出力例**:
```
INFO - #1: 2 insects detected (confidence: 0.785, time: 1205.3ms)
INFO - #2: No insects detected (time: 890.1ms)
```

---

### SimpleObserver._should_stop()

**概要**: 観測終了条件の判定

**処理内容**:
1. 観測時間制限（duration）の確認
2. 無制限設定時は継続判定（False）
3. 開始時刻からの経過時間計算
4. 制限時間との比較判定

**入力インターフェース**:
```python
def _should_stop(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| should_stop | bool | 停止判定（True: 停止, False: 継続） |

**判定ロジック**:
```python
if not self.duration:      # 無制限
    return False
    
elapsed = (datetime.now() - self.start_time).total_seconds()
return elapsed >= self.duration
```

---

### SimpleObserver.stop()

**概要**: 観測停止・リソースクリーンアップ処理

**処理内容**:
1. 実行フラグの停止設定
2. **統計情報の算出・表示**:
   - 総観測回数
   - 総実行時間
   - 平均観測間隔
3. **リソースクリーンアップ**:
   - 検出器のクリーンアップ（detector.cleanup）
   - CSVファイルのクローズ
4. 停止完了ログの出力

**入力インターフェース**:
```python
def stop(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 停止処理完了 |

**表示統計**:
```
=== Observation Summary ===
Total observations: 120
Total time: 2:05:15
Average interval: 62.3 seconds
```

---

### SimpleObserver.get_status()

**概要**: 現在の観測状態情報の取得

**処理内容**:
1. 実行状態の確認
2. 開始時刻・経過時間の計算
3. 観測統計の集計
4. 設定情報の取得
5. 状態辞書の生成・返却

**入力インターフェース**:
```python
def get_status(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| status | Dict[str, Any] | 現在状態情報辞書 |

**状態情報構造**:
```python
{
    'is_running': bool,              # 実行中フラグ
    'start_time': str,               # 開始時刻（ISO形式）
    'elapsed_time': str,             # 経過時間
    'observation_count': int,        # 観測回数
    'interval_seconds': int,         # 観測間隔
    'duration_seconds': int,         # 観測時間制限
    'output_directory': str          # 出力ディレクトリ
}
```

---

### main()

**概要**: コマンドライン実行時のメイン関数

**処理内容**:
1. コマンドライン引数の解析（argparse）
2. SimpleObserver インスタンスの作成
3. 観測実行（start_observation）
4. 例外処理・エラー終了

**入力インターフェース**:
```python
def main() -> None:
```

**コマンドライン引数**:
| 引数 | 型 | デフォルト | 説明 |
|------|---|----------|------|
| --interval | int | 60 | 観測間隔（秒） |
| --duration | int | None | 観測時間（秒） |
| --output-dir | str | "./simple_logs" | 出力ディレクトリ |

**使用例**:
```bash
python simple_observer.py --interval 30 --duration 3600
```

**例外**:
| 例外名 | 発生条件 |
|-------|---------|
| Exception | アプリケーション実行エラー |

---

## 📊 データ構造

### ObservationRecord (仮想データクラス)

**概要**: 観測記録を表現するデータ構造（実装では辞書を使用）

**属性**:
| 属性名 | 型 | 説明 | 範囲・形式 |
|-------|---|------|----------|
| timestamp | str | 観測時刻 | ISO8601形式 |
| detection_count | int | 検出昆虫数 | 0以上の整数 |
| has_detection | bool | 検出有無フラグ | True/False |
| confidence_avg | float | 平均信頼度 | 0.0-1.0 |
| x_center_avg | float | X座標平均値 | ピクセル値 |
| y_center_avg | float | Y座標平均値 | ピクセル値 |
| processing_time_ms | float | 処理時間 | ミリ秒 |
| observation_number | int | 観測連番 | 1から開始 |

### SimpleObserver クラス

**概要**: シンプル観測処理クラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| interval | int | 観測間隔（秒） |
| duration | Optional[int] | 観測時間制限（秒） |
| output_dir | Path | 出力ディレクトリパス |
| logger | logging.Logger | ロガーインスタンス |
| detector_settings | DetectionSettings | 検出器設定 |
| detector | Optional[InsectDetector] | 検出器インスタンス |
| is_running | bool | 実行状態フラグ |
| start_time | Optional[datetime] | 開始時刻 |
| observation_count | int | 観測回数カウンター |
| csv_file | Optional[TextIO] | CSVファイルハンドル |
| csv_writer | Optional[csv.writer] | CSVライター |

---

## 🔄 処理フロー

### アプリケーション全体フロー
```
[コマンド実行]
        │
        ▼
    ┌─────────┐
    │引数解析  │ ←── --interval, --duration, --output-dir
    └─────────┘
        │
        ▼
    ┌─────────┐
    │インスタンス│ ←── SimpleObserver作成
    │作成     │
    └─────────┘
        │
        ▼
    ┌─────────┐
    │観測実行  │ ←── start_observation()
    │        │     [メインループ]
    └─────────┘
        │
        ▼
    ┌─────────┐
    │終了処理  │ ←── 統計表示・リソース解放
    └─────────┘
```

### 観測メインループフロー
```
[観測ループ開始]
        │
        ▼
    ┌─────────┐
    │単一観測  │ ←── detector.detect_single_image()
    │実行     │     処理時間計測
    └─────────┘
        │
        ▼
    ┌─────────┐
    │結果処理  │ ←── 平均値計算・データ構築
    └─────────┘
        │
        ▼
    ┌─────────┐
    │CSV保存  │ ←── 即座書き込み・フラッシュ
    └─────────┘
        │
        ▼
    ┌─────────┐
    │ログ出力  │ ←── コンソール表示
    └─────────┘
        │
        ▼
    ┌─────────┐
    │終了判定  │ ←── 時間制限・ユーザー中断
    └─────────┘
        │
    継続 ▼ 終了
    ┌─────────┐
    │待機     │ ←── time.sleep(interval)
    └─────────┘
        │
        ▲──────────┘
```

### エラー処理フロー
```
[エラー発生]
        │
        ▼
    ┌─────────┐
    │エラー種別│ ←── 初期化 / 観測 / CSV / その他
    │判定     │
    └─────────┘
        │
    ┌───▼───┐
    │致命的  │ → アプリケーション終了
    └───────┘
        │
    ┌───▼───┐
    │一時的  │ → ログ出力・観測継続
    └───────┘
```

---

## 📝 実装メモ

### 設計原則
1. **既存システム保護**: main.py、insect_detector.py の完全無変更
2. **シンプル操作**: 最小限のコマンドライン引数
3. **堅牢性**: エラー発生時の継続実行
4. **データ完整性**: CSV書き込みの確実性保証
5. **リソース管理**: 適切なクリーンアップ処理

### 技術的特徴
- **非同期処理なし**: シンプルな順次処理
- **外部依存最小**: 標準ライブラリ中心
- **メモリ効率**: 大量データの保持なし
- **ファイルI/O**: 即座書き込み・バッファフラッシュ

### 注意事項
- 長時間実行時のディスク容量監視が必要
- IR LED発熱による連続動作制限を考慮
- CSV ファイルの手動編集は非推奨
- 複数インスタンスの同時実行は出力ディレクトリで分離

### 依存関係
- **標準ライブラリ**: logging, time, csv, signal, sys, argparse, datetime, pathlib
- **プロジェクト内**: insect_detector.py (DetectionSettings, InsectDetector)
- **外部ライブラリ**: typing (型ヒント)

### パフォーマンス考慮
- CSV書き込み: 同期・即座フラッシュで確実性重視
- メモリ使用量: 観測データの即座処理で最小化
- 処理時間: 検出器処理時間に依存（1-3秒程度）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-08-13 | 開発チーム | 初版作成 |