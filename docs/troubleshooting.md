# トラブルシューティングガイド

このドキュメントでは、昆虫自動観察システムの開発・実行時に発生した問題と解決方法を記載しています。

## 目次
- [カメラアクセスエラー](#カメラアクセスエラー)
- [Python環境の問題](#python環境の問題)
- [モジュールインストールエラー](#モジュールインストールエラー)

---

## カメラアクセスエラー

### 問題1: 仮想環境でカメラにアクセスできない

**症状:**
```
警告: フレームの取得に失敗しました
```
- `test_camera_detection.py`実行時に上記メッセージが繰り返し表示される
- フレーム数が0のまま終了する
- `UnboundLocalError: cannot access local variable 'avg_time'`エラーが発生

**原因:**
- 仮想環境のOpenCVがRaspberry Piカメラモジュールに正しくアクセスできない
- システムのOpenCV（4.6.0）と仮想環境のOpenCV（4.12.0）でバージョンとビルド設定が異なる

**試した対策:**

1. **カメラデバイスの権限確認**
   ```bash
   ls -la /dev/video0
   # 結果: crw-rw----+ 1 root video 81, 17  8月  2 00:17 /dev/video0
   
   groups
   # 結果: videoグループに所属していることを確認
   ```

2. **カメラ使用プロセスの確認**
   ```bash
   sudo fuser /dev/video0
   # 結果: No process using camera
   ```

3. **複数のカメラバックエンドを試す（コード修正）**
   - デフォルトバックエンド
   - V4L2バックエンド明示指定
   - GStreamerパイプライン

4. **シンプルなカメラテストスクリプト作成**
   - `test_camera_simple.py`でOpenCVのみでのカメラアクセスをテスト
   - カメラは開けるがフレーム取得に失敗

**解決方法:**
- **仮想環境を使用せず、システムのPython環境で実行する**
- システム環境にはカメラアクセスに必要な設定が含まれている

---

## Python環境の問題

### 問題2: externally-managed-environment エラー

**症状:**
```
error: externally-managed-environment
× This environment is externally managed
```

**原因:**
- 新しいRaspberry Pi OS（Debian 12ベース）ではシステムのPython環境が保護されている
- PEP 668に基づく変更により、pipでのシステム全体へのインストールが制限されている

**試した対策:**

1. **--userフラグの使用**
   ```bash
   pip3 install --user ultralytics
   # 結果: 同じエラーが発生
   ```

2. **仮想環境の作成と使用**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # 結果: インストールは成功するが、カメラアクセスの問題が発生
   ```

**解決方法:**
```bash
sudo pip3 install ultralytics --break-system-packages
```
- `--break-system-packages`フラグを使用してシステムレベルでインストール
- セキュリティリスクを理解した上で使用する

---

## モジュールインストールエラー

### 問題3: ModuleNotFoundError: No module named 'ultralytics'

**症状:**
```
ModuleNotFoundError: No module named 'ultralytics'
```

**原因:**
- 必要なモジュールがインストールされていない
- 仮想環境とシステム環境の混在

**解決手順:**

1. **仮想環境の場合:**
   ```bash
   source venv/bin/activate
   pip install ultralytics opencv-python numpy
   ```

2. **システム環境の場合:**
   ```bash
   sudo pip3 install ultralytics --break-system-packages
   ```

---

## カメラフレーム取得エラー

### 問題4: カメラは開けるがフレームが取得できない

**症状:**
- `カメラ 0 を初期化中...` は成功
- `エラー: カメラからフレームを取得できませんでした`
- 画面が真っ黒
- FPS取得エラー: `Unable to get camera FPS`

**原因:**
- Raspberry Pi Camera Module 3とOpenCVの直接的な互換性の問題
- libcameraスタックとV4L2の統合問題

**解決方法（推奨順）:**

1. **libcamera-vidを使用したストリーミング + OpenCV**
   ```bash
   # ターミナル1: libcameraでストリーミング開始
   libcamera-vid -t 0 --width 640 --height 480 --codec h264 --output - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/stream}' :demux=h264
   
   # ターミナル2: OpenCVでRTSPストリームを読む
   # test_camera_detection.pyを修正してrtsp://localhost:8554/streamを使用
   ```

2. **Picamera2の使用（最も確実）**
   ```python
   # Picamera2をシステムにインストール
   sudo apt install -y python3-picamera2
   
   # YOLOv8と組み合わせて使用
   # 別途Picamera2対応スクリプトを作成
   ```

3. **古いlibcamera互換レイヤーの使用**
   ```bash
   # libcamera-v4l2を使用
   sudo modprobe bcm2835-v4l2
   ```

### 最終解決方法 ✅ **成功**

**実施した解決策:**
1. **システムPython環境にultralyticsをインストール**
   ```bash
   sudo pip3 install ultralytics --break-system-packages
   ```

2. **libcameraベースの実用的なスクリプト作成**
   - **test_libcamera_yolo.py** - ファイルベース検出
   - **test_simple_realtime.py** - リアルタイム表示（推奨）
   - **test_realtime_display.py** - 高性能ストリーミング

3. **動作確認コマンド**
   ```bash
   # ファイルベース検出
   python3 test_libcamera_yolo.py --frames 5 --interval 3
   
   # リアルタイム表示（デスクトップ環境）
   export DISPLAY=:0
   python3 test_simple_realtime.py --fps 3
   ```

**成功結果:**
- ✅ カメラ映像の取得・表示
- ✅ YOLOv8による物体検出
- ✅ リアルタイム検出結果の可視化
- ✅ 安定した2-5 FPS動作
- ✅ 平均推論時間: 400-700ms

**重要なポイント:**
- 仮想環境ではなくシステムPython環境を使用
- libcamera-stillベースのアプローチが最も安定
- Raspberry Pi Camera Module 3 (imx708_noir) で動作確認済み

## 推奨される実行方法

### 開発時の推奨設定

1. **システム環境での実行（カメラを使用する場合）**
   ```bash
   # 仮想環境を抜ける
   deactivate
   
   # システム環境で実行
   python3 test_camera_detection.py
   ```

2. **ラッパースクリプトの使用**
   - `run_test_camera.sh`を作成して環境チェックを自動化

3. **環境確認コマンド**
   ```bash
   # OpenCVバージョン確認
   python3 -c "import cv2; print('OpenCV:', cv2.__version__)"
   
   # カメラデバイス確認
   ls /dev/video*
   
   # libcameraデバイス確認
   libcamera-hello --list-cameras
   ```

---

## Camera Module 3 Wide 互換性問題

### 問題5: Camera Module 3 WideでOpenCVがフレーム取得に失敗

**症状:**
```
モデルを読み込み中: yolov8n.pt
モデルの読み込みが成功しました。クラス数: 80
カメラ 0 を初期化中...
カメラ解像度: 640x480 @ -1fps
カメラの初期化を待っています...
エラー: カメラからフレームを取得できませんでした
```
- OpenCVでカメラは開けるがフレームが黒画面
- 文字化け表示（UTF-8エンコーディング問題）
- FPS取得エラー: `Unable to get camera FPS`

**原因:**
1. **カメラスタックの非互換性**
   - Camera Module 3 Wide: libcameraスタック（新）
   - OpenCV (cv2.VideoCapture): V4L2/GStreamer期待（旧）
   
2. **解像度の不一致**
   - GStreamerパイプラインが640×480固定
   - Camera Module 3 Wideのネイティブ解像度:
     - 1536×864 (120fps)
     - 2304×1296 (56fps)
     - 4608×2592 (14fps)

3. **libcameraとOpenCVのブリッジ問題**
   - Raspberry Pi OSがlibcameraに移行
   - OpenCVは旧V4L2インターフェース期待

**解決方法: Picamera2を使用**

1. **新しいスクリプト作成**
   ```bash
   # test_camera_detection_picamera2.py を作成
   # Picamera2を使用してCamera Module 3 Wideに直接アクセス
   ```

2. **実行コマンド**
   ```bash
   # デフォルト設定（1536×864）
   python test_camera_detection_picamera2.py
   
   # 高解像度
   python test_camera_detection_picamera2.py --width 2304 --height 1296
   
   # SSHからヘッドレス実行
   python test_camera_detection_picamera2.py --no-display
   ```

**技術的詳細:**
- **Picamera2**: libcameraの公式Pythonラッパー
- **直接アクセス**: Camera Module 3シリーズ専用設計
- **自動ネゴシエーション**: 解像度の自動調整機能
- **NumPy互換**: YOLOv8と直接連携可能

**重要:** Camera Module 3 WideではOpenCVの代わりにPicamera2を使用することが推奨されます。

---

## ハードウェア情報

### 確認されたカメラ
- **デバイス:** 
  - Raspberry Pi Camera Module 3 NoIR
  - Raspberry Pi Camera Module 3 Wide NoIR（広角タイプ）
- **センサー:** 
  - imx708_noir [4608x2592 10-bit RGGB]
  - imx708_wide_noir [4608x2592 10-bit RGGB]
- **接続:** CSI接続（/base/axi/pcie@1000120000/rp1/i2c@88000/imx708@1a）

### 利用可能なモード
- 1536x864 @ 120.13 fps
- 2304x1296 @ 56.03 fps  
- 4608x2592 @ 14.35 fps

---

## 関連リンク

- [Raspberry Pi公式ドキュメント - Camera](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [PEP 668 – Externally Managed Environments](https://peps.python.org/pep-0668/)
- [OpenCV Python Documentation](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

---

## クイックスタートガイド

### 標準YOLOv8でのカメラテスト（推奨手順）

1. **環境確認**
   ```bash
   # libcameraが動作するか確認
   libcamera-hello -t 5000
   
   # 必要なパッケージがインストールされているか確認
   python3 -c "import ultralytics, cv2; print('✓ 準備完了')"
   ```

2. **リアルタイム検出の実行**
   ```bash
   # デスクトップ環境で実行
   export DISPLAY=:0
   python3 test_simple_realtime.py
   
   # カスタマイズ例
   python3 test_simple_realtime.py --fps 5 --size 800x600 --conf 0.3
   ```

3. **ファイルベース検出の実行**
   ```bash
   # 連続撮影・検出
   python3 test_libcamera_yolo.py --frames 10 --interval 2
   
   # 結果は libcamera_detection_output/ フォルダに保存
   ```

### カスタムモデル（昆虫検出）での実行

1. **モデルダウンロード**
   ```bash
   mkdir -p weights
   python3 -c "
   from huggingface_hub import hf_hub_download
   hf_hub_download('Murasan/beetle-detection-yolov8', 'best.pt', local_dir='./weights')
   "
   ```

2. **カスタムモデルで実行**
   ```bash
   # 昆虫検出専用モデルを使用
   python3 test_simple_realtime.py --model weights/best.pt --conf 0.4
   ```

### トラブル時の対処

1. **画面が表示されない場合**
   ```bash
   # SSH経由の場合
   export DISPLAY=:0
   
   # VNC使用を検討
   # またはRaspberry Piに直接モニター接続
   ```

2. **フレーム取得に失敗する場合**
   ```bash
   # カメラの基本動作確認
   libcamera-still -o test.jpg
   
   # デバイス確認
   ls /dev/video*
   ```

3. **推論が遅い場合**
   ```bash
   # 解像度を下げる
   python3 test_simple_realtime.py --size 320x240
   
   # FPSを下げる
   python3 test_simple_realtime.py --fps 2
   ```

---

## Camera Module 3 Wide オートフォーカス問題

### 問題6: 透明な壁越しの撮影でフォーカスが合わない

**症状:**
- Camera Module 3 Wideのオートフォーカスが手前の透明な壁（虫かご等）にフォーカスしてしまう
- 対象物（昆虫）がぼやけて検出精度が低下
- 手動でフォーカス距離を設定しても期待通りにフォーカスが合わない

**原因:**
- **透明な障害物への誤フォーカス**: オートフォーカスシステムが透明な虫かごの壁を検出してそこにフォーカスを合わせてしまう
- **Camera Module 3 Wideの特殊なLensPosition範囲**: 通常のカメラと異なり0-32の範囲を持つ（一般的なカメラは0-10）
- **距離とレンズ位置の変換問題**: 物理的な距離（cm）をレンズ位置に変換する際の計算が不適切

**解決方法:**

1. **専用スクリプトの作成**
   - `test_camera_detection_picamera2_fixed.py`を作成
   - Camera Module 3 Wide用の特殊なLensPosition範囲（0-32）に対応
   - 距離からレンズ位置への変換関数を実装

2. **重要な技術的修正:**
   ```python
   def distance_to_lens_position(distance_cm, max_lens=32.0):
       """
       Camera Module 3 Wide用の変換関数
       - 32.0が最近接（約5cm）
       - 0.0が無限遠
       - 対数スケールで中間距離を計算
       """
   ```

3. **推奨フォーカス設定:**
   - **5cm**: LensPosition = 32.0（最大近接）
   - **10cm**: LensPosition ≈ 20.0
   - **20cm**: LensPosition ≈ 10.0（昆虫観察に推奨）
   - **50cm**: LensPosition ≈ 4.0
   - **100cm以上**: LensPosition = 0.0（無限遠）

4. **実行コマンド:**
   ```bash
   # 20cmの距離にフォーカス（昆虫観察用）
   python test_camera_detection_picamera2_fixed.py --distance 20
   
   # 異なる距離でテスト
   python test_camera_detection_picamera2_fixed.py --distance 10
   python test_camera_detection_picamera2_fixed.py --distance 30
   ```

5. **シャープネスベースの最適化:**
   - スクリプトは指定距離の前後でシャープネスを測定
   - 最もシャープな位置に自動調整
   - 透明な壁の影響を最小化

**成功のポイント:**
- ✅ マニュアルフォーカスモード（AfMode.Manual）の使用
- ✅ Camera Module 3 Wide特有のLensPosition範囲への対応
- ✅ 距離に応じた適切なレンズ位置の計算
- ✅ シャープネスベースの微調整機能
- ✅ リアルタイムでのフォーカス位置表示

**注意事項:**
- 透明な壁越しの撮影では、壁と対象物の距離を考慮して設定
- 実際の最適値は環境により異なるため、複数の距離設定を試すことを推奨
- フォーカス設定後は1秒程度の安定化時間が必要

---

*最終更新日: 2025-08-29*