#!/bin/bash
# カメラテストスクリプト実行用ラッパー
# システムのPython環境を使用してカメラアクセスの問題を回避

echo "カメラテストを実行します..."
echo "注意: このスクリプトはシステムのPython環境を使用します"
echo ""

# ultralyticsがシステムにインストールされているか確認
if ! python3 -c "import ultralytics" 2>/dev/null; then
    echo "エラー: ultralyticsがシステムにインストールされていません"
    echo "以下のコマンドでインストールしてください:"
    echo "sudo pip3 install ultralytics --break-system-packages"
    echo "または"
    echo "pip3 install --user ultralytics"
    exit 1
fi

# OpenCVがシステムにインストールされているか確認
if ! python3 -c "import cv2" 2>/dev/null; then
    echo "エラー: OpenCVがシステムにインストールされていません"
    echo "以下のコマンドでインストールしてください:"
    echo "sudo apt install python3-opencv"
    exit 1
fi

# スクリプトを実行
python3 test_camera_detection.py "$@"