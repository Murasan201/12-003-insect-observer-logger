#!/usr/bin/env python3
"""
YOLOv8 昆虫検出モデル訓練スクリプト

このスクリプトは、カスタム昆虫データセットを使用してYOLOv8モデルのファインチューニングを実行します。
Roboflowデータセットを使用したカブトムシ検出に特化して設計されています。

使用方法:
    python train_yolo.py --data datasets/data.yaml --epochs 100
    python train_yolo.py --data datasets/data.yaml --epochs 50 --batch 16 --imgsz 640

必要なライブラリ:
    - ultralytics
    - torch
    - opencv-python
    - numpy
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 必要なライブラリのインポート
try:
    from ultralytics import YOLO  # YOLOv8モデル用
    import torch                 # PyTorch深層学習フレームワーク
    import cv2                   # OpenCVコンピュータビジョンライブラリ
    import numpy as np           # 数値計算用ライブラリ
except ImportError as e:
    print(f"エラー: 必要なライブラリがインストールされていません: {e}")
    print("依存関係をインストールしてください: pip install -r requirements.txt")
    sys.exit(1)


def setup_logging():
    """訓練プロセス用のログ設定を初期化します。"""
    # タイムスタンプ付きのログファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)  # logsディレクトリがなければ作成
    
    log_file = log_dir / f"training_{timestamp}.log"
    
    # ログ設定: ファイルとコンソールの両方に出力
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),    # ファイル出力
            logging.StreamHandler(sys.stdout)  # コンソール出力
        ]
    )
    
    return logging.getLogger(__name__)


def validate_dataset(data_path):
    """
    データセットの構造と設定を検証します。
    
    Args:
        data_path (str): data.yamlファイルのパス
        
    Returns:
        bool: データセットが有効な場合True、そうでなければFalse
    """
    data_file = Path(data_path)
    if not data_file.exists():
        logging.error(f"データセット設定ファイルが見つかりません: {data_path}")
        return False
    
    # データセットディレクトリの存在確認
    dataset_dir = data_file.parent
    required_dirs = ["train/images", "train/labels", "valid/images", "valid/labels"]
    
    for dir_path in required_dirs:
        full_path = dataset_dir / dir_path
        if not full_path.exists():
            logging.error(f"必要なディレクトリが見つかりません: {full_path}")
            return False
        
        # ディレクトリ内のファイル数をカウント
        files = list(full_path.glob("*"))
        if not files:
            logging.error(f"ディレクトリ内にファイルがありません: {full_path}")
            return False
        
        logging.info(f"{dir_path} に {len(files)} 個のファイルを発見")
    
    logging.info("データセットの検証が成功しました")
    return True


def check_system_requirements():
    """システム要件をチェックし、システム情報をログに記録します。"""
    logger = logging.getLogger(__name__)
    
    # Pythonバージョンをチェック
    python_version = sys.version
    logger.info(f"Pythonバージョン: {python_version}")
    
    # PyTorchバージョンとCUDAの利用可能性をチェック
    torch_version = torch.__version__
    cuda_available = torch.cuda.is_available()
    device_count = torch.cuda.device_count() if cuda_available else 0
    
    logger.info(f"PyTorchバージョン: {torch_version}")
    logger.info(f"CUDA利用可能: {cuda_available}")
    logger.info(f"GPU数: {device_count}")
    
    if cuda_available:
        # 各GPUの情報を表示
        for i in range(device_count):
            gpu_name = torch.cuda.get_device_name(i)
            logger.info(f"GPU {i}: {gpu_name}")
    else:
        logger.info("訓練はCPUのみで実行されます")
    
    # OpenCVバージョンをチェック
    cv2_version = cv2.__version__
    logger.info(f"OpenCVバージョン: {cv2_version}")


def train_model(data_path, model_name="yolov8n.pt", epochs=100, batch_size=16, 
                img_size=640, device="auto", project="training_results", 
                name="beetle_detection"):
    """
    指定されたパラメータでYOLOv8モデルを訓練します。
    
    Args:
        data_path (str): データセット設定ファイルのパス
        model_name (str): 使用する事前訓練モデル
        epochs (int): 訓練エポック数
        batch_size (int): 訓練時のバッチサイズ
        img_size (int): 訓練用画像サイズ
        device (str): 訓練に使用するデバイス
        project (str): プロジェクトディレクトリ名
        name (str): 実験名
        
    Returns:
        YOLO: 訓練済みモデルインスタンス
    """
    logger = logging.getLogger(__name__)
    
    logger.info("YOLOv8訓練プロセスを開始します")
    logger.info(f"モデル: {model_name}")
    logger.info(f"データセット: {data_path}")
    logger.info(f"エポック数: {epochs}")
    logger.info(f"バッチサイズ: {batch_size}")
    logger.info(f"画像サイズ: {img_size}")
    logger.info(f"デバイス: {device}")
    
    try:
        # 事前訓練モデルを読み込み
        logger.info(f"事前訓練モデルを読み込み中: {model_name}")
        model = YOLO(model_name)
        
        # 訓練開始
        start_time = time.time()
        logger.info("訓練を開始しました...")
        
        results = model.train(
            data=data_path,      # データセット設定ファイル
            epochs=epochs,       # 訓練エポック数
            batch=batch_size,    # バッチサイズ
            imgsz=img_size,      # 画像サイズ
            device=device,       # 使用デバイス
            project=project,     # プロジェクトディレクトリ
            name=name,           # 実験名
            save=True,           # モデル保存を有効化
            save_period=10,      # 10エポックごとにチェックポイント保存
            val=True,            # 検証を有効化
            plots=True,          # グラフ出力を有効化
            verbose=True         # 詳細ログを有効化
        )
        
        training_time = time.time() - start_time
        logger.info(f"訓練が {training_time:.2f} 秒で完了しました")
        logger.info(f"結果の保存先: {project}/{name}")
        
        return model, results
        
    except Exception as e:
        logger.error(f"訓練が失敗しました: {str(e)}")
        raise


def validate_model(model, data_path):
    """
    Validate trained model on test dataset.
    
    Args:
        model (YOLO): Trained model instance
        data_path (str): Path to dataset configuration
        
    Returns:
        dict: Validation results
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting model validation...")
        
        # Run validation
        validation_results = model.val(data=data_path)
        
        # Log key metrics
        if hasattr(validation_results, 'box'):
            box_metrics = validation_results.box
            logger.info(f"mAP@0.5: {box_metrics.map50:.4f}")
            logger.info(f"mAP@0.5:0.95: {box_metrics.map:.4f}")
            logger.info(f"Precision: {box_metrics.mp:.4f}")
            logger.info(f"Recall: {box_metrics.mr:.4f}")
        
        logger.info("Model validation completed")
        return validation_results
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise


def export_model(model, formats=None, project="weights", name="best_model"):
    """
    Export trained model to various formats.
    
    Args:
        model (YOLO): Trained model instance
        formats (list): List of export formats
        project (str): Export directory
        name (str): Export filename prefix
    """
    if formats is None:
        formats = ["onnx", "torchscript"]
    
    logger = logging.getLogger(__name__)
    
    # Create weights directory
    weights_dir = Path(project)
    weights_dir.mkdir(exist_ok=True)
    
    try:
        for format_type in formats:
            logger.info(f"Exporting model to {format_type} format...")
            model.export(format=format_type)
            logger.info(f"Model exported to {format_type} format successfully")
    
    except Exception as e:
        logger.error(f"Model export failed: {str(e)}")


def main():
    """メイン訓練関数。"""
    parser = argparse.ArgumentParser(description="YOLOv8 昆虫検出モデル訓練")
    
    # 必須引数
    parser.add_argument("--data", type=str, required=True,
                        help="データセット設定ファイルのパス (data.yaml)")
    
    # オプション引数
    parser.add_argument("--model", type=str, default="yolov8n.pt",
                        help="使用する事前訓練モデル (デフォルト: yolov8n.pt)")
    parser.add_argument("--epochs", type=int, default=100,
                        help="訓練エポック数 (デフォルト: 100)")
    parser.add_argument("--batch", type=int, default=16,
                        help="訓練時のバッチサイズ (デフォルト: 16)")
    parser.add_argument("--imgsz", type=int, default=640,
                        help="訓練用画像サイズ (デフォルト: 640)")
    parser.add_argument("--device", type=str, default="auto",
                        help="使用デバイス (auto, cpu, 0, 1, 等)")
    parser.add_argument("--project", type=str, default="training_results",
                        help="プロジェクトディレクトリ名 (デフォルト: training_results)")
    parser.add_argument("--name", type=str, default="beetle_detection",
                        help="実験名 (デフォルト: beetle_detection)")
    parser.add_argument("--export", action="store_true",
                        help="訓練後にモデルをエクスポート")
    parser.add_argument("--validate", action="store_true", default=True,
                        help="訓練後に検証を実行 (デフォルト: True)")
    
    args = parser.parse_args()
    
    # ログ設定を初期化
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("YOLOv8 昆虫検出モデル訓練スクリプト")
    logger.info("=" * 60)
    
    # システム要件をチェック
    check_system_requirements()
    
    # データセットを検証
    if not validate_dataset(args.data):
        logger.error("データセットの検証が失敗しました。終了します。")
        sys.exit(1)
    
    try:
        # モデルを訓練
        model, train_results = train_model(
            data_path=args.data,
            model_name=args.model,
            epochs=args.epochs,
            batch_size=args.batch,
            img_size=args.imgsz,
            device=args.device,
            project=args.project,
            name=args.name
        )
        
        # モデルを検証
        if args.validate:
            validation_results = validate_model(model, args.data)
        
        # モデルをエクスポート
        if args.export:
            export_model(model, project="weights", name="beetle_detection_model")
        
        logger.info("訓練パイプラインが成功しました！")
        logger.info(f"モデル重みの保存先: {args.project}/{args.name}/weights/")
        
    except Exception as e:
        logger.error(f"訓練パイプラインが失敗しました: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()