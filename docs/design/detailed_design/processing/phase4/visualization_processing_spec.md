# visualization.py 処理説明書

**文書番号**: 12-002-PROC-006  
**プロジェクト名**: 昆虫自動観察＆ログ記録アプリ  
**文書名**: visualization.py 処理説明書  
**対象ファイル**: `visualization.py`  
**バージョン**: 1.0  
**作成日**: 2025-07-29  
**作成者**: 開発チーム  

---

## 📋 ファイル概要

### 目的
昆虫活動データの可視化・グラフ・チャート生成を行うモジュール。分析結果を視覚的に理解しやすい形式で出力する。

### 主要機能
- 時系列グラフ・アクティビティチャート
- 移動軌跡・ヒートマップ生成
- 統計グラフ・分布図作成
- ダッシュボード・レポート生成
- インタラクティブ可視化（Plotly）
- カスタムテーマ・スタイル設定

---

## 🔧 関数・メソッド仕様

### __init__(settings)

**概要**: 可視化器の初期化処理

**処理内容**:
1. ロガー設定
2. 可視化設定の初期化（デフォルト値適用）
3. 出力ディレクトリの作成
4. matplotlib・plotlyライブラリ可用性チェック
5. matplotlib設定（_setup_matplotlib）
6. plotly設定（_setup_plotly）

**入力インターフェース**:
```python
def __init__(self, settings: Optional[VisualizationSettings] = None):
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| settings | VisualizationSettings | × | 可視化設定（デフォルト値使用可） |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | インスタンス初期化 |

---

### _setup_matplotlib()

**概要**: matplotlib可視化ライブラリの設定

**処理内容**:
1. スタイルテーマの適用
2. フォント設定（フォント名・サイズ）
3. 図サイズ・DPI設定
4. 日本語フォント対応設定
5. エラーハンドリング・ログ出力

**入力インターフェース**:
```python
def _setup_matplotlib(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | matplotlib設定完了 |

---

### _setup_plotly()

**概要**: plotlyインタラクティブ可視化ライブラリの設定

**処理内容**:
1. デフォルトテーマの設定
2. テンプレート適用
3. エラーハンドリング・ログ出力

**入力インターフェース**:
```python
def _setup_plotly(self) -> None:
```

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| なし | None | plotly設定完了 |

---

### create_activity_timeline(data, title)

**概要**: 昆虫活動タイムライングラフの作成

**処理内容**:
1. matplotlib可用性チェック
2. 3段構成のサブプロット作成
3. 検出数時系列グラフの描画
4. 信頼度推移の散布図作成
5. 移動距離時系列グラフの描画
6. 時刻軸フォーマット設定
7. ファイル保存・パス返却

**入力インターフェース**:
```python
def create_activity_timeline(self, data: pd.DataFrame, title: str = "昆虫活動タイムライン") -> Optional[str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 時系列活動データ |
| title | str | × | グラフタイトル |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filepath | Optional[str] | 保存ファイルパス（失敗時None） |

**使用例**:
```python
timeline_path = visualizer.create_activity_timeline(df, "2025-07-29 昆虫活動")
```

---

### create_movement_heatmap(data, title)

**概要**: 昆虫移動軌跡ヒートマップの作成

**処理内容**:
1. matplotlib可用性・位置データ存在確認
2. x_center・y_centerカラムからの位置データ抽出
3. 2Dヒストグラム計算（50x50ビン）
4. ヒートマップ画像生成・表示
5. カラーバー・軸ラベル設定
6. 画面境界矩形の描画
7. ファイル保存・パス返却

**入力インターフェース**:
```python
def create_movement_heatmap(self, data: pd.DataFrame, title: str = "昆虫移動ヒートマップ") -> Optional[str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 位置データ |
| title | str | × | グラフタイトル |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filepath | Optional[str] | 保存ファイルパス（失敗時None） |

**使用例**:
```python
heatmap_path = visualizer.create_movement_heatmap(df)
```

---

### create_statistics_dashboard(activity_metrics, hourly_summaries)

**概要**: 統計ダッシュボードの作成

**処理内容**:
1. 複数サブプロットレイアウト作成
2. 基本統計値の表示
3. 時間別活動量の棒グラフ作成
4. 活動分布のヒストグラム描画
5. 統計値テキストボックス配置
6. 統一レイアウト・保存処理

**入力インターフェース**:
```python
def create_statistics_dashboard(self, activity_metrics: ActivityMetrics, hourly_summaries: List[HourlyActivitySummary]) -> Optional[str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| activity_metrics | ActivityMetrics | ○ | 活動量指標データ |
| hourly_summaries | List[HourlyActivitySummary] | ○ | 時間別サマリー |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filepath | Optional[str] | 保存ファイルパス（失敗時None） |

---

### create_interactive_dashboard(data, activity_metrics)

**概要**: Plotlyベースのインタラクティブダッシュボード作成

**処理内容**:
1. plotly可用性チェック
2. サブプロット構成の設定
3. 時系列インタラクティブチャート作成
4. 散布図・ヒートマップ追加
5. 統計サマリーテーブル配置
6. ズーム・パン・ホバー機能設定
7. HTMLファイル出力

**入力インターフェース**:
```python
def create_interactive_dashboard(self, data: pd.DataFrame, activity_metrics: ActivityMetrics) -> Optional[str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 時系列データ |
| activity_metrics | ActivityMetrics | ○ | 活動量指標 |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| filepath | Optional[str] | HTMLファイルパス（失敗時None） |

**使用例**:
```python
dashboard_path = visualizer.create_interactive_dashboard(df, metrics)
```

---

### export_visualization_report(activity_metrics, detection_data, hourly_summaries)

**概要**: 包括的な可視化レポートの生成・エクスポート

**処理内容**:
1. 複数の可視化グラフを生成：
   - 活動タイムライン
   - 移動軌跡ヒートマップ
   - 統計ダッシュボード
   - インタラクティブダッシュボード
2. レポートメタデータの作成
3. 生成ファイルリストの管理
4. エラーハンドリング・ログ出力
5. レポートサマリーファイル出力

**入力インターフェース**:
```python
def export_visualization_report(self, activity_metrics: ActivityMetrics, detection_data: pd.DataFrame, hourly_summaries: List[HourlyActivitySummary] = None) -> Optional[str]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| activity_metrics | ActivityMetrics | ○ | 活動量指標 |
| detection_data | pd.DataFrame | ○ | 検出データ |
| hourly_summaries | List[HourlyActivitySummary] | × | 時間別サマリー |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| report_dir | Optional[str] | レポートディレクトリパス（失敗時None） |

**使用例**:
```python
report_path = visualizer.export_visualization_report(metrics, df, hourly_data)
```

---

### _calculate_movement_for_viz(data)

**概要**: 可視化用移動距離計算（簡易版）

**処理内容**:
1. 座標データの前処理
2. 前回位置との差分計算
3. ユークリッド距離算出
4. 移動距離リスト返却

**入力インターフェース**:
```python
def _calculate_movement_for_viz(self, data: pd.DataFrame) -> List[float]:
```

| 引数名 | 型 | 必須 | 説明 |
|-------|---|------|------|
| data | pd.DataFrame | ○ | 位置データ |

**出力インターフェース**:
| 戻り値 | 型 | 説明 |
|-------|---|------|
| movements | List[float] | 移動距離リスト |

---

## 📊 データ構造

### VisualizationSettings

**概要**: 可視化の設定パラメータ

**属性**:
| 属性名 | 型 | 説明 |
|-------|---|------|
| output_format | str | 出力ファイル形式（png, jpg, svg, pdf, html） |
| output_dir | str | 出力ディレクトリパス |
| dpi | int | 画像解像度（DPI） |
| figure_size | Tuple[int, int] | 図のサイズ（幅, 高さ） |
| style_theme | str | スタイルテーマ（seaborn, ggplot, classic） |
| color_palette | str | カラーパレット（viridis, plasma, tab10） |
| font_family | str | フォントファミリー |
| font_size | int | フォントサイズ |
| show_grid | bool | グリッド表示フラグ |
| show_legend | bool | 凡例表示フラグ |
| transparency | float | 透明度（0.0-1.0） |
| line_width | float | 線の太さ |
| marker_size | float | マーカーサイズ |
| interactive_mode | bool | インタラクティブモード有効フラグ |
| plotly_theme | str | Plotlyテーマ名 |

---

## 🔄 処理フロー

### 可視化レポート生成フロー
```
1. 入力データ検証
   ↓
2. 活動タイムライン作成
   ↓
3. 移動ヒートマップ作成
   ↓
4. 統計ダッシュボード作成
   ↓
5. インタラクティブダッシュボード作成
   ↓
6. レポートサマリー生成
   ↓
7. ファイル保存・パス返却
```

### グラフ作成フロー
```
ライブラリ可用性チェック
   ↓
データ前処理・検証
   ↓
プロット設定・スタイル適用
   ↓
グラフ要素描画
   ↓
ラベル・タイトル設定
   ↓
ファイル保存・クリーンアップ
```

---

## 📝 実装メモ

### 注意事項
- matplotlib・plotlyの両方がオプション依存
- 大量データの可視化ではメモリ使用量に注意
- 日本語フォント設定の環境依存性
- ファイル保存時の権限・容量確認

### 依存関係
- matplotlib: 静的グラフ・チャート生成
- seaborn: 統計的可視化・美しいプロット
- plotly: インタラクティブ可視化・ダッシュボード
- pandas: データフレーム操作・時系列処理
- numpy: 数値計算・ヒストグラム生成
- models.activity_models: 活動量データクラス

---

## 🔄 更新履歴

| バージョン | 更新日 | 更新者 | 更新内容 |
|-----------|--------|--------|----------|
| 1.0 | 2025-07-29 | 開発チーム | 初版作成 |