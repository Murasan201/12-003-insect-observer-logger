# monitoring.py 処理説明書

**文書番号**: 12-002-PROC-011  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: monitoring.py 処理説明書  
**対象ファイル**: `monitoring.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
システム全体の健全性監視とパフォーマンス追跡を行うシステム監視統合管理モジュール。

### 主要機能
- リアルタイムシステム監視・健全性チェック
- パフォーマンスメトリクス収集・履歴管理
- リソース使用量監視（CPU・メモリ・ディスク・ネットワーク）
- コンポーネント別健全性チェック・アラート生成
- 監視ダッシュボード機能・レポート生成

---

## 🔧 関数・メソッド仕様

### __init__(config)

**概要**: システム監視統合管理クラスの初期化

**処理内容**:
1. 設定の保存・ロガー設定
2. 健全性チェッカー辞書・コンポーネント状態辞書の初期化
3. メトリクス履歴・現在メトリクス管理の初期化
4. アラート管理（アクティブアラート・履歴）の設定
5. 監視間隔・メトリクス収集間隔の設定
6. 監視スレッド管理の初期化
7. システムリソース監視・ログディレクトリの設定
8. デフォルト健全性チェッカーの設定（_setup_default_checkers）

**入力インターフェース**:
```python
def __init__(self, config: Dict[str, Any]):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config | Dict[str, Any] | ○ | 監視設定辞書 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### register_health_checker(checker)

**概要**: 健全性チェッカーを登録

**処理内容**:
1. チェッカー名をキーとして健全性チェッカー辞書に追加
2. 登録完了ログの出力

**入力インターフェース**:
```python
def register_health_checker(self, checker: HealthChecker):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| checker | HealthChecker | ○ | 健全性チェッカーオブジェクト |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 登録完了 |

**使用例**:
```python
fs_checker = FileSystemHealthChecker("logs_disk", "logs", min_free_gb=1.0)
monitor.register_health_checker(fs_checker)
```

---

### start_monitoring()

**概要**: 監視を開始

**処理内容**:
1. 既存監視の重複開始チェック
2. 監視アクティブフラグの設定
3. 健全性チェックスレッドの作成・開始（_health_check_loop）
4. メトリクス収集スレッドの作成・開始（_metrics_collection_loop）
5. 監視開始ログの出力

**入力インターフェース**:
```python
def start_monitoring(self):
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 監視開始完了 |

**使用例**:
```python
monitor.start_monitoring()
print("システム監視が開始されました")
```

---

### stop_monitoring()

**概要**: 監視を停止

**処理内容**:
1. 監視アクティブフラグの無効化
2. 健全性チェックスレッドの停止待機（5秒タイムアウト）
3. メトリクス収集スレッドの停止待機（5秒タイムアウト）
4. 監視停止ログの出力

**入力インターフェース**:
```python
def stop_monitoring(self):
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 監視停止完了 |

---

### _health_check_loop()

**概要**: 健全性チェックループ（別スレッド実行）

**処理内容**:
1. 監視アクティブ状態での継続ループ
2. 全健全性チェックの実行（_perform_health_checks）
3. 監視間隔での待機
4. エラー時の短間隔再試行（5秒）

**入力インターフェース**:
```python
def _health_check_loop(self):
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | ループ終了 |

---

### _metrics_collection_loop()

**概要**: メトリクス収集ループ（別スレッド実行）

**処理内容**:
1. 監視アクティブ状態での継続ループ
2. システムメトリクス収集（_collect_system_metrics）
3. メトリクス収集間隔での待機
4. エラー時の短間隔再試行（5秒）

**入力インターフェース**:
```python
def _metrics_collection_loop(self):
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | ループ終了 |

---

### _perform_health_checks()

**概要**: すべての健全性チェックを実行

**処理内容**:
1. スレッドロック取得
2. 登録済み健全性チェッカーの順次実行
3. チェック結果のコンポーネント状態への保存
4. 異常状態時のアラート生成（_generate_alert）
5. 正常復旧時のアラート解決（_resolve_alerts）
6. チェック失敗時のフォールバック処理

**入力インターフェース**:
```python
def _perform_health_checks(self):
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 健全性チェック完了 |

---

### _collect_system_metrics()

**概要**: システムメトリクスを収集

**処理内容**:
1. 現在時刻の取得
2. CPU使用率の測定・記録
3. メモリ使用量・空き容量の測定・記録
4. ディスク使用量・空き容量の測定・記録
5. ネットワーク送受信バイト数の測定・記録
6. システムアップタイムの計算・記録
7. ロードアベレージの測定・記録（Linux専用）

**入力インターフェース**:
```python
def _collect_system_metrics(self):
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | メトリクス収集完了 |

**収集メトリクス**:
| メトリクス名 | 型 | 単位 | 説明 |
|-------------|---|------|------|
| system.cpu_percent | GAUGE | % | CPU使用率 |
| system.memory_percent | GAUGE | % | メモリ使用率 |
| system.memory_available_mb | GAUGE | MB | 利用可能メモリ量 |
| system.disk_percent | GAUGE | % | ディスク使用率 |
| system.disk_free_gb | GAUGE | GB | ディスク空き容量 |
| system.network_bytes_sent | COUNTER | bytes | ネットワーク送信バイト数 |
| system.network_bytes_recv | COUNTER | bytes | ネットワーク受信バイト数 |
| system.uptime_seconds | GAUGE | seconds | システムアップタイム |
| system.load_1min | GAUGE | - | 1分間ロードアベレージ |

---

### get_system_health()

**概要**: システム全体の健全性情報を取得

**処理内容**:
1. スレッドロック取得
2. 各コンポーネント状態の確認・優先度判定
3. 最も深刻な状態を全体状態として採用
4. コンポーネント別健全性情報の収集
5. アクティブアラート数の算出
6. 健全性情報辞書の作成・返却

**入力インターフェース**:
```python
def get_system_health(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| health_info | Dict[str, Any] | システム健全性情報辞書 |

**戻り値構造**:
```python
{
    "overall_status": str,                    # 全体状態（healthy/warning/error/critical）
    "components": {                           # コンポーネント別状態
        "component_name": {
            "name": str,
            "status": str,
            "last_check_time": str,
            "response_time_ms": float,
            "error_message": str,
            "metrics": dict
        }
    },
    "active_alerts_count": int,               # アクティブアラート数
    "last_check_time": str                    # 最終チェック時刻
}
```

---

### get_current_metrics()

**概要**: 現在のメトリクス情報を取得

**処理内容**:
1. スレッドロック取得
2. 現在メトリクス辞書の全項目を辞書形式に変換
3. メトリクス情報辞書の返却

**入力インターフェース**:
```python
def get_current_metrics(self) -> Dict[str, Any]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| metrics | Dict[str, Any] | 現在メトリクス情報辞書 |

---

### get_metric_history(metric_name, hours)

**概要**: 指定メトリクスの履歴を取得

**処理内容**:
1. カットオフ時刻の計算（現在時刻 - 指定時間）
2. メトリクス履歴からの該当データ抽出
3. 時刻フィルタリング・リスト返却

**入力インターフェース**:
```python
def get_metric_history(self, metric_name: str, hours: int = 1) -> List[PerformanceMetric]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| metric_name | str | ○ | 取得対象メトリクス名 |
| hours | int | × | 取得期間（時間、デフォルト: 1） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| history | List[PerformanceMetric] | メトリクス履歴リスト |

**使用例**:
```python
cpu_history = monitor.get_metric_history("system.cpu_percent", hours=24)
print(f"過去24時間のCPU使用率履歴: {len(cpu_history)}件")
```

---

### get_active_alerts()

**概要**: アクティブなアラートを取得

**処理内容**:
1. スレッドロック取得
2. アクティブアラート辞書から未解決アラートの抽出
3. アラートリストの返却

**入力インターフェース**:
```python
def get_active_alerts(self) -> List[MonitoringAlert]:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| alerts | List[MonitoringAlert] | アクティブアラートリスト |

---

### acknowledge_alert(alert_id)

**概要**: アラートを確認済みにする

**処理内容**:
1. スレッドロック取得
2. 指定アラートIDの検索
3. 確認フラグの設定・ログ出力
4. 成功可否の返却

**入力インターフェース**:
```python
def acknowledge_alert(self, alert_id: str) -> bool:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| alert_id | str | ○ | 確認対象アラートID |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 確認処理成功可否 |

---

### export_monitoring_report(output_path)

**概要**: 監視レポートをエクスポート

**処理内容**:
1. レポート辞書の作成（システム健全性・現在メトリクス・アラート情報）
2. アップタイム時間の計算
3. JSONファイルの生成・保存
4. ファイルパスの返却

**入力インターフェース**:
```python
def export_monitoring_report(self, output_path: Path) -> Path:
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
report_path = monitor.export_monitoring_report(Path("logs/reports"))
print(f"監視レポート生成: {report_path}")
```

---

## 🏥 健全性チェッカークラス

### ProcessHealthChecker

**概要**: プロセス健全性チェック

**主要機能**:
- プロセス存在確認・状態チェック
- プロセス数・PID情報の収集
- プロセス停止時の重大アラート生成

**チェック項目**:
- プロセス名での検索・存在確認
- プロセス状態（running/sleeping/stopped等）
- プロセス数の監視

### FileSystemHealthChecker

**概要**: ファイルシステム健全性チェック

**主要機能**:
- ディスク容量監視・閾値チェック
- 書き込み権限テスト
- 容量不足・権限エラーのアラート生成

**チェック項目**:
- 空き容量（GB）の監視
- ディスク使用率（%）の監視
- ファイル書き込み権限の確認

### HardwareHealthChecker

**概要**: ハードウェア健全性チェック

**主要機能**:
- CPU温度監視（Raspberry Pi対応）
- GPU情報取得・監視
- 高温時の警告・危険レベル判定

**チェック項目**:
- CPU温度（/sys/class/thermal/thermal_zone0/temp）
- GPU メモリ使用量（vcgencmd使用）
- 温度閾値（80℃警告・85℃危険）

---

## 📊 データ構造

### ComponentStatus (Enum)

**概要**: コンポーネント状態の列挙型

**値**:
| 状態 | 値 | 説明 |
|-----|---|------|
| HEALTHY | "healthy" | 正常状態 |
| WARNING | "warning" | 警告状態 |
| ERROR | "error" | エラー状態 |
| CRITICAL | "critical" | 致命的状態 |
| UNKNOWN | "unknown" | 不明状態 |
| OFFLINE | "offline" | オフライン状態 |

### MetricType (Enum)

**概要**: メトリクス種別の列挙型

**値**:
| 種別 | 値 | 説明 |
|-----|---|------|
| COUNTER | "counter" | カウンター（累積値） |
| GAUGE | "gauge" | ゲージ（現在値） |
| HISTOGRAM | "histogram" | ヒストグラム（分布） |
| TIMER | "timer" | タイマー（実行時間） |

### PerformanceMetric

**概要**: パフォーマンスメトリクス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| name | str | メトリクス名 |
| type | MetricType | メトリクス種別 |
| value | float | 測定値 |
| timestamp | str | 測定時刻（ISO形式） |
| tags | Dict[str, str] | タグ情報 |
| unit | str | 単位 |
| description | str | 説明 |

### MonitoringAlert

**概要**: 監視アラート

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| alert_id | str | アラートID |
| component | str | 対象コンポーネント名 |
| severity | str | 重要度（WARNING/ERROR/CRITICAL） |
| message | str | アラートメッセージ |
| timestamp | str | 発生時刻 |
| resolved | bool | 解決済みフラグ |
| resolution_time | Optional[str] | 解決時刻 |
| acknowledgment | bool | 確認済みフラグ |

---

## 🔄 処理フロー

### 監視開始フロー
```
監視開始要求
   ↓
重複チェック・フラグ設定
   ↓
健全性チェックスレッド開始
   ├─ 監視間隔でのループ実行
   ├─ 全チェッカーの実行
   ├─ 結果評価・アラート生成
   └─ エラー時短間隔再試行
   ↓
メトリクス収集スレッド開始
   ├─ 収集間隔でのループ実行
   ├─ システムリソース測定
   ├─ メトリクス記録・履歴管理
   └─ エラー時短間隔再試行
```

### 健全性チェックフロー
```
定期チェック実行
   ↓
登録チェッカーの順次実行
   ├─ ProcessHealthChecker: プロセス存在確認
   ├─ FileSystemHealthChecker: ディスク容量・権限確認
   └─ HardwareHealthChecker: CPU温度・GPU状態確認
   ↓
チェック結果評価
   ├─ 正常: アラート解決処理
   └─ 異常: アラート生成・重要度判定
   ↓
コンポーネント状態更新
```

### アラート管理フロー
```
異常状態検出
   ↓
既存アラート確認
   ├─ 既存: スキップ
   └─ 新規: アラート生成
   ↓
アラート生成・記録
   ├─ アラートID生成
   ├─ 重要度・メッセージ設定
   ├─ アクティブアラート登録
   └─ 履歴記録・ログ出力
   ↓
正常復旧時: アラート解決処理
```

---

## 📝 実装メモ

### 注意事項
- スレッドセーフな状態管理・データ共有
- プラットフォーム依存機能の適切な処理（Linux専用機能）
- メモリ効率的な履歴データ管理（deque使用）
- ハードウェア情報取得の例外処理

### 依存関係
- psutil: システムリソース監視・プロセス管理
- threading: スレッド管理・同期制御
- subprocess: システムコマンド実行（温度取得等）
- pathlib: ファイルパス操作
- collections: deque・defaultdict（効率的なデータ管理）

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |