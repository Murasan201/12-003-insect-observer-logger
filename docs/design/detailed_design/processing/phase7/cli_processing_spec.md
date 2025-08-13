# cli.py 処理説明書

**文書番号**: 12-002-PROC-012  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: cli.py 処理説明書  
**対象ファイル**: `cli.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
Clickライブラリを使用した高度なコマンドラインインターフェースを提供し、対話的操作、バッチ処理、システム診断機能を統合する。

### 主要機能
- 複数実行モード（連続観察・単発検出・データ分析）
- リアルタイムシステム監視・ステータス表示
- 包括的システム診断・ハードウェアテスト
- 対話式CLI・設定管理
- データクリーンアップ・メンテナンス機能
- Rich UIライブラリによる視覚的表示

---

## 🔧 関数・メソッド仕様

### CLIController.__init__(config_path)

**概要**: CLI操作用コントローラーの初期化

**処理内容**:
1. 設定ファイルパスの保存
2. システムインスタンス変数の初期化
3. 監視関連フラグ・スレッドの初期化

**入力インターフェース**:
```python
def __init__(self, config_path: str):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| config_path | str | ○ | システム設定ファイルパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### CLIController.initialize_system()

**概要**: システム初期化

**処理内容**:
1. InsectObserverSystemインスタンスの作成
2. システム初期化メソッドの呼び出し
3. 初期化成功可否の返却
4. エラー時のコンソール出力

**入力インターフェース**:
```python
def initialize_system(self) -> bool:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| success | bool | 初期化成功可否 |

---

### cli(ctx, config, log_level)

**概要**: メインCLIグループ・エントリーポイント

**処理内容**:
1. ログレベル設定（setup_logging）
2. CLIControllerインスタンスの作成
3. Clickコンテキストへのコントローラー保存

**入力インターフェース**:
```python
@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), default='./config/system_config.json')
@click.option('--log-level', '-l', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']), default='INFO')
@click.pass_context
def cli(ctx, config, log_level):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| ctx | Context | ○ | Clickコンテキスト |
| config | str | × | 設定ファイルパス（デフォルト: system_config.json） |
| log_level | str | × | ログレベル（デフォルト: INFO） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | コンテキスト設定完了 |

---

### run(controller, interval, duration, daemon)

**概要**: 連続観察モードで実行

**処理内容**:
1. 実行パラメータのパネル表示
2. システム初期化・失敗時早期終了
3. 実行時間制限の計算（duration指定時）
4. メインループ実行・KeyboardInterrupt処理
5. クリーンアップ処理

**入力インターフェース**:
```python
@cli.command()
@click.option('--interval', '-i', type=int, default=60)
@click.option('--duration', '-d', type=int, default=0)
@click.option('--daemon', is_flag=True)
@click.pass_obj
def run(controller: CLIController, interval, duration, daemon):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| controller | CLIController | ○ | CLIコントローラー |
| interval | int | × | 検出間隔（秒、デフォルト: 60） |
| duration | int | × | 実行時間（分、0は無制限） |
| daemon | bool | × | デーモンモードフラグ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 実行完了・中断時 |

**使用例**:
```bash
python cli.py run --interval 300 --duration 60  # 5分間隔で1時間実行
python cli.py run --daemon  # デーモンモード実行
```

---

### detect(controller, save_image, output_dir, no_led)

**概要**: 単発検出を実行

**処理内容**:
1. 検出実行メッセージの表示
2. システム初期化・失敗時早期終了
3. プログレス表示付き検出実行
4. 検出結果のテーブル表示・エラー処理
5. クリーンアップ処理

**入力インターフェース**:
```python
@cli.command()
@click.option('--save-image', is_flag=True)
@click.option('--output-dir', '-o', type=click.Path(), default='./output')
@click.option('--no-led', is_flag=True)
@click.pass_obj
def detect(controller: CLIController, save_image, output_dir, no_led):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| controller | CLIController | ○ | CLIコントローラー |
| save_image | bool | × | 検出画像保存フラグ |
| output_dir | str | × | 出力ディレクトリ（デフォルト: ./output） |
| no_led | bool | × | LED照明無効フラグ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 検出完了・エラー時 |

**結果表示項目**:
- タイムスタンプ・検出数・処理時間・成功可否

**使用例**:
```bash
python cli.py detect --save-image --output-dir ./results
python cli.py detect --no-led  # LED照明なしで検出
```

---

### analyze(controller, date_or_range, output_format, include_charts, export_images)

**概要**: データ分析を実行

**処理内容**:
1. 日付・期間の解析処理
2. 単日分析・期間分析の分岐処理
3. システム初期化・分析実行
4. 分析結果の成功可否表示
5. クリーンアップ処理

**入力インターフェース**:
```python
@cli.command()
@click.argument('date_or_range', required=False)
@click.option('--output-format', '-f', type=click.Choice(['csv', 'json', 'html']), default='csv')
@click.option('--include-charts', is_flag=True)
@click.option('--export-images', is_flag=True)
@click.pass_obj
def analyze(controller: CLIController, date_or_range, output_format, include_charts, export_images):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| controller | CLIController | ○ | CLIコントローラー |
| date_or_range | str | × | 日付またはrange（デフォルト: 昨日） |
| output_format | str | × | 出力形式（csv/json/html） |
| include_charts | bool | × | グラフ含有フラグ |
| export_images | bool | × | 画像エクスポートフラグ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 分析完了・失敗時 |

**使用例**:
```bash
python cli.py analyze 2025-07-29  # 指定日分析
python cli.py analyze 2025-07-25:2025-07-29  # 期間分析
python cli.py analyze --output-format json --include-charts
```

---

### status(controller, output_json, detailed, watch)

**概要**: システム状態を表示

**処理内容**:
1. システム初期化・失敗時早期終了
2. ウォッチモード・単発表示の分岐
3. JSON出力・テーブル表示の選択
4. リアルタイム監視機能（watch時）
5. クリーンアップ処理

**入力インターフェース**:
```python
@cli.command()
@click.option('--json', 'output_json', is_flag=True)
@click.option('--detailed', is_flag=True)
@click.option('--watch', '-w', is_flag=True)
@click.pass_obj
def status(controller: CLIController, output_json, detailed, watch):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| controller | CLIController | ○ | CLIコントローラー |
| output_json | bool | × | JSON形式出力フラグ |
| detailed | bool | × | 詳細情報表示フラグ |
| watch | bool | × | リアルタイム監視モードフラグ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 状態表示完了・監視終了時 |

**表示項目**:
- システム状態（稼働・稼働時間・検出数・エラー数）
- ハードウェア状態（カメラ・LED・CPU温度）

**使用例**:
```bash
python cli.py status --detailed  # 詳細表示
python cli.py status --json  # JSON出力
python cli.py status --watch  # リアルタイム監視
```

---

### diagnose(controller, full, output_file)

**概要**: システム診断を実行

**処理内容**:
1. システム初期化・失敗時早期終了
2. 診断項目リストの作成（基本・完全診断）
3. プログレス表示付き診断実行
4. 診断結果の表示・ファイル保存
5. クリーンアップ処理

**入力インターフェース**:
```python
@cli.command()
@click.option('--full', is_flag=True)
@click.option('--output-file', '-o', type=click.Path())
@click.pass_obj
def diagnose(controller: CLIController, full, output_file):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| controller | CLIController | ○ | CLIコントローラー |
| full | bool | × | 完全診断実行フラグ |
| output_file | str | × | 結果保存ファイルパス |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 診断完了・結果出力後 |

**診断項目**:
- **基本診断**: ハードウェア・モデル・ストレージ・設定チェック
- **完全診断**: 基本診断 + カメラテスト・検出テスト

**使用例**:
```bash
python cli.py diagnose  # 基本診断
python cli.py diagnose --full --output-file diagnosis.json  # 完全診断・結果保存
```

---

### cleanup(controller, dry_run, older_than)

**概要**: 古いデータをクリーンアップ

**処理内容**:
1. クリーンアップ対象ディレクトリの設定
2. カットオフ日付の計算・ファイル検索
3. 削除対象ファイルリスト・サイズ計算
4. dry-run モード・実行モードの分岐処理
5. 確認プロンプト・削除実行

**入力インターフェース**:
```python
@cli.command()
@click.option('--dry-run', is_flag=True)
@click.option('--older-than', type=int, default=30)
@click.pass_obj
def cleanup(controller: CLIController, dry_run, older_than):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| controller | CLIController | ○ | CLIコントローラー |
| dry_run | bool | × | 試行実行モードフラグ |
| older_than | int | × | 保存期間（日数、デフォルト: 30） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | クリーンアップ完了・キャンセル時 |

**対象ディレクトリ**:
- `./logs`, `./output`, `./data/detections`, `./data/processed`

**使用例**:
```bash
python cli.py cleanup --dry-run  # 試行実行
python cli.py cleanup --older-than 7  # 7日より古いファイル削除
```

---

### interactive(controller)

**概要**: 対話モードを開始

**処理内容**:
1. 対話モード開始パネルの表示
2. システム初期化・失敗時早期終了
3. コマンドマップの定義・ループ処理
4. ユーザー入力の受付・コマンド実行
5. 終了コマンド・KeyboardInterrupt処理

**入力インターフェース**:
```python
@cli.command()
@click.pass_obj
def interactive(controller: CLIController):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| controller | CLIController | ○ | CLIコントローラー |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 対話モード終了時 |

**対話コマンド**:
- `help`: コマンド一覧表示
- `status`: システム状態表示
- `detect`: 単発検出実行
- `analyze`: データ分析実行
- `config`: 現在設定表示
- `exit/quit`: 対話モード終了

**使用例**:
```bash
python cli.py interactive
insect-observer> help  # コマンド一覧
insect-observer> detect  # 検出実行
insect-observer> exit  # 終了
```

---

### config(controller, config_file, validate_only)

**概要**: 設定ファイルの検証・適用

**処理内容**:
1. 設定ファイルの読み込み・JSON解析
2. 必須フィールドの検証
3. 検証結果の表示・エラー処理
4. 設定適用の確認・ファイルコピー

**入力インターフェース**:
```python
@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--validate-only', is_flag=True)
@click.pass_obj
def config(controller: CLIController, config_file, validate_only):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| controller | CLIController | ○ | CLIコントローラー |
| config_file | str | ○ | 検証対象設定ファイルパス |
| validate_only | bool | × | 検証のみ実行フラグ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | 検証・適用完了時 |

**必須フィールド**:
- `system`, `hardware`, `detection`, `analysis`

**使用例**:
```bash
python cli.py config new_config.json --validate-only  # 検証のみ
python cli.py config new_config.json  # 検証・適用
```

---

## 🎨 表示・UI関数仕様

### _display_status_table(status_data, detailed)

**概要**: ステータステーブル表示

**処理内容**:
1. システム状態テーブルの作成・表示
2. 詳細モード時のハードウェア状態テーブル表示
3. Rich Tableによる視覚的表示

**表示項目**:
- システム状態: 稼働状態・稼働時間・総検出数・処理画像数・最終検出・エラー数
- ハードウェア状態: カメラ・LED・CPU温度情報

---

### _watch_system_status(controller)

**概要**: リアルタイムシステム監視

**処理内容**:
1. Live表示の開始・1秒間隔更新
2. システム状態・ハードウェア状態の取得
3. パネル表示の構築・更新
4. KeyboardInterrupt処理

---

### _display_diagnosis_results(results)

**概要**: 診断結果表示

**処理内容**:
1. 診断結果テーブルの作成
2. 状態アイコン・詳細情報の表示
3. サマリー（OK項目数/総項目数）の表示

**状態アイコン**:
- OK: ✓（緑）, NG: ✗（赤）, WARNING: ⚠（黄）, UNKNOWN: ?（灰）

---

## 🔍 診断機能仕様

### _check_hardware(controller)

**概要**: ハードウェアチェック

**処理内容**:
1. ハードウェア制御器からの詳細状態取得
2. カメラ初期化・LED可用性・CPU温度の確認
3. ステータス判定・結果辞書返却

---

### _check_model(controller)

**概要**: モデルチェック

**処理内容**:
1. モデル管理器からのモデル状態取得
2. モデル存在・パス確認
3. ステータス判定・結果辞書返却

---

### _check_storage(controller)

**概要**: ストレージチェック

**処理内容**:
1. ディスク使用量統計の取得
2. 空き容量・使用率の計算
3. 閾値チェック（1GB未満で警告）・結果辞書返却

---

### _test_camera(controller)

**概要**: カメラテスト

**処理内容**:
1. ハードウェア制御器による画像キャプチャ
2. キャプチャ成功可否・画像形状の確認
3. エラーハンドリング・結果辞書返却

---

### _test_detection(controller)

**概要**: 検出テスト

**処理内容**:
1. システム単発検出の実行
2. 検出成功可否・処理時間の確認
3. エラーハンドリング・結果辞書返却

---

## 📊 データ構造

### CLIController

**概要**: CLI操作用コントローラークラス

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| config_path | str | 設定ファイルパス |
| system | Optional[InsectObserverSystem] | システムインスタンス |
| monitoring_active | bool | 監視アクティブフラグ |
| monitoring_thread | Optional[threading.Thread] | 監視スレッド |

### 診断結果構造

**概要**: 各診断機能の戻り値構造

**共通フィールド**:
| フィールド名 | 型 | 説明 |
|-------------|---|------|
| status | str | 診断結果（OK/NG/WARNING/UNKNOWN） |

**ハードウェア診断**:
```python
{
    "camera_initialized": bool,
    "led_available": bool,
    "temperature": float,
    "status": str
}
```

**ストレージ診断**:
```python
{
    "free_space_gb": float,
    "total_space_gb": float,
    "usage_percent": float,
    "status": str
}
```

---

## 🔄 処理フロー

### コマンド実行フロー
```
CLI起動
   ↓
メイングループ（cli）
   ├─ ログ設定
   ├─ CLIController作成
   └─ コンテキスト保存
   ↓
サブコマンド分岐
   ├─ run: 連続観察モード
   ├─ detect: 単発検出
   ├─ analyze: データ分析
   ├─ status: 状態表示
   ├─ diagnose: システム診断
   ├─ cleanup: データクリーンアップ
   ├─ interactive: 対話モード
   └─ config: 設定管理
   ↓
各コマンド処理
   ├─ システム初期化
   ├─ 処理実行
   ├─ 結果表示
   └─ クリーンアップ
```

### 対話モードフロー
```
対話モード開始
   ↓
システム初期化
   ↓
コマンドループ
   ├─ プロンプト表示
   ├─ ユーザー入力受付
   ├─ コマンド判定・実行
   │   ├─ help: ヘルプ表示
   │   ├─ status: 状態表示
   │   ├─ detect: 検出実行
   │   ├─ analyze: 分析実行
   │   ├─ config: 設定表示
   │   └─ exit/quit: 終了
   └─ 継続・終了判定
   ↓
クリーンアップ・終了
```

### システム診断フロー
```
診断開始
   ↓
診断項目設定
   ├─ 基本診断: ハードウェア・モデル・ストレージ・設定
   └─ 完全診断: 基本診断 + カメラテスト・検出テスト
   ↓
プログレス表示付き実行
   ├─ 各診断機能の順次実行
   ├─ 結果収集・エラー処理
   └─ 進捗更新
   ↓
結果表示・ファイル保存
   ├─ 診断結果テーブル表示
   ├─ サマリー表示
   └─ JSON形式ファイル出力
```

---

## 📝 実装メモ

### 注意事項
- Rich UIライブラリによる視覚的表示・プログレス表示
- Click フレームワークによる堅牢なCLI実装
- 適切なエラーハンドリング・リソース管理
- ユーザビリティを考慮したインタラクティブ操作

### 依存関係
- click: CLIフレームワーク・コマンド定義
- rich: 高度なテキスト表示・UI表示
- pathlib: ファイルパス操作
- threading: 監視スレッド管理
- json: 設定ファイル・結果データの処理
- main: InsectObserverSystemとの統合

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |