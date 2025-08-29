# 昆虫観察システム クイックガイド

## 動作確認済み設定

### ハードウェア
- **カメラ**: Raspberry Pi Camera Module 3 Wide NoIR
- **観察環境**: 透明な虫かご越しの撮影
- **フォーカス距離**: 20cm（虫かごの壁から昆虫までの距離）

### ソフトウェア
- **検出モデル**: `weights/best.pt`（甲虫検出専用）
- **検出精度**: mAP@0.5: 97.63%
- **スクリプト**: `test_camera_detection_picamera2_fixed.py`

## 基本的な実行コマンド

### 1. 標準実行（推奨設定）
```bash
python test_camera_detection_picamera2_fixed.py --model weights/best.pt --distance 20
```

### 2. 高精度モード（誤検出を減らしたい場合）
```bash
python test_camera_detection_picamera2_fixed.py --model weights/best.pt --distance 20 --conf 0.4
```

### 3. ヘッドレス実行（SSH経由）
```bash
python test_camera_detection_picamera2_fixed.py --model weights/best.pt --distance 20 --no-display
```

## フォーカス調整ガイド

### 距離別の推奨設定

| 観察距離 | コマンドパラメータ | 用途 |
|---------|------------------|------|
| 10cm | `--distance 10` | 小さな昆虫の詳細観察 |
| 20cm | `--distance 20` | 標準的な昆虫観察（推奨） |
| 30cm | `--distance 30` | 大きめの虫かご使用時 |
| 50cm | `--distance 50` | 広範囲の観察 |

### フォーカス調整のコツ
1. 透明な壁（虫かごなど）がある場合は、壁から対象物までの距離を設定
2. 初回実行時はシャープネス最適化が自動で行われる（約5秒）
3. 最適な設定が見つかったら、その距離値を記録しておく

## トラブルシューティング

### 検出されない場合
```bash
# 信頼度閾値を下げる
python test_camera_detection_picamera2_fixed.py --model weights/best.pt --distance 20 --conf 0.2
```

### フォーカスが合わない場合
```bash
# 異なる距離を試す（5cm刻み）
python test_camera_detection_picamera2_fixed.py --model weights/best.pt --distance 15
python test_camera_detection_picamera2_fixed.py --model weights/best.pt --distance 25
```

### 処理が重い場合
```bash
# 解像度を下げる
python test_camera_detection_picamera2_fixed.py --model weights/best.pt --distance 20 --width 640 --height 480
```

## 長時間観察モード

### 連続観察の実行
```bash
# 長時間実行する場合はnohupを使用
nohup python test_camera_detection_picamera2_fixed.py --model weights/best.pt --distance 20 --no-display > observation.log 2>&1 &

# プロセスの確認
ps aux | grep test_camera_detection

# 停止方法
kill [プロセスID]
```

## データ記録について

現在の実装では画面表示とコンソール出力のみですが、将来的には以下の機能を追加予定：
- 検出ログのCSV保存
- 検出画像の自動保存
- 活動パターンの分析

## メンテナンス

### 定期的な確認事項
1. カメラレンズの汚れをチェック
2. 虫かごの透明度を確認（汚れがあると検出精度が低下）
3. 照明条件の確認（NoIRカメラは赤外線照明が有効）

### モデルの更新
```bash
# 新しいモデルがある場合
python test_camera_detection_picamera2_fixed.py --model weights/new_model.pt --distance 20
```

---

*最終更新: 2025-08-29*
*動作確認済み環境: Raspberry Pi with Camera Module 3 Wide NoIR*