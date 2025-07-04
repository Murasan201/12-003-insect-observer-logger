#!/usr/bin/env python3
"""
YOLOv8を使用した昆虫検出アプリケーション

CPUベースの昆虫検出アプリケーション。画像をバッチ処理し、
包括的なログと共に可視化結果を出力します。

作成者: Generated with Claude Code
ライセンス: MIT
"""

# 標準ライブラリのインポート
import argparse     # コマンドライン引数解析
import csv          # CSVファイル処理
import logging      # ログ出力
import os           # OS機能
import sys          # システム機能
import time         # 時刻計測
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# 外部ライブラリのインポート
import cv2          # OpenCV コンピュータビジョン
import numpy as np  # 数値計算
from ultralytics import YOLO  # YOLOv8 モデル


def setup_logging(log_dir: Path) -> Tuple[logging.Logger, str]:
    """
    コンソールとファイル出力の両方に対してログ設定を初期化します。
    
    Args:
        log_dir: ログファイルを保存するディレクトリ
        
    Returns:
        ロガーインスタンスとCSVログファイル名のタプル
    """
    # ログディレクトリが存在しない場合は作成
    log_dir.mkdir(exist_ok=True)
    
    # コンソールログの設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # 標準出力へのログ出力
        ]
    )
    logger = logging.getLogger(__name__)
    
    # タイムスタンプ付きCSVログファイル名を作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"detection_log_{timestamp}.csv"
    csv_path = log_dir / csv_filename
    
    # CSVヘッダーを作成
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'detected', 'count', 'time_ms'])
    
    logger.info(f"ログ初期化完了。CSVログ: {csv_path}")
    return logger, str(csv_path)


def load_model(model_path: str, logger: logging.Logger) -> YOLO:
    """
    推論用のYOLOv8モデルを読み込みます。
    
    Args:
        model_path: モデル重みファイルのパス
        logger: ロガーインスタンス
        
    Returns:
        読み込まれたYOLOモデル
    """
    try:
        logger.info(f"YOLOv8モデルを読み込み中: {model_path}")
        model = YOLO(model_path)
        logger.info(f"モデルの読み込みが成功しました。クラス数: {len(model.names)}")
        return model
    except Exception as e:
        logger.error(f"モデルの読み込みに失敗しました: {e}")
        sys.exit(1)


def get_image_files(input_dir: Path, logger: logging.Logger) -> List[Path]:
    """
    入力ディレクトリからすべての有効な画像ファイルを取得します。
    
    Args:
        input_dir: 入力ディレクトリパス
        logger: ロガーインスタンス
        
    Returns:
        画像ファイルパスのリスト
    """
    # サポートする画像フォーマット
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    image_files = []
    
    # 大文字・小文字両方の拡張子で検索
    for ext in valid_extensions:
        image_files.extend(input_dir.glob(f"*{ext}"))
        image_files.extend(input_dir.glob(f"*{ext.upper()}"))
    
    image_files.sort()  # ファイル名でソート
    logger.info(f"{input_dir} で {len(image_files)} 個の画像ファイルを発見")
    
    if not image_files:
        logger.warning(f"{input_dir} で画像ファイルが見つかりません")
    
    return image_files


def detect_objects(
    model: YOLO, 
    image_path: Path, 
    confidence_threshold: float = 0.25
) -> Tuple[np.ndarray, List[dict], bool]:
    """
    単一の画像に対して物体検出を実行します。
    
    Args:
        model: YOLOモデルインスタンス
        image_path: 入力画像のパス
        confidence_threshold: 検出の最低信頼度
        
    Returns:
        (注釈付き画像、検出結果リスト、検出有無)のタプル
    """
    # 画像を読み込み
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"画像を読み込めません: {image_path}")
    
    # CPUデバイスを明示的に指定して推論を実行
    results = model.predict(
        source=image,                    # 入力画像
        device='cpu',                    # CPUで推論を実行
        conf=confidence_threshold,       # 信頼度闾値
        verbose=False                    # 詳細ログを無効化
    )
    
    detections = []
    has_detections = False
    
    # 結果を処理
    for result in results:
        # 注釈付き画像を取得
        annotated_image = result.plot()
        
        # 検出情報を抽出
        if result.boxes is not None and len(result.boxes) > 0:
            has_detections = True
            
            # バウンディングボックス、クラス、信頼度を取得
            boxes = result.boxes.xyxy.cpu().numpy()        # バウンディングボックス座標
            classes = result.boxes.cls.cpu().numpy()       # クラスID
            confidences = result.boxes.conf.cpu().numpy()  # 信頼度
            
            # 各検出結果を処理
            for box, cls, conf in zip(boxes, classes, confidences):
                x1, y1, x2, y2 = map(int, box)  # 座標を整数に変換
                class_name = model.names[int(cls)]  # クラス名を取得
                
                # 検出情報を辞書として保存
                detection = {
                    'class': class_name,
                    'confidence': float(conf),
                    'bbox': [x1, y1, x2, y2]
                }
                detections.append(detection)
        else:
            # 検出結果がない場合は元の画像を返す
            annotated_image = image
    
    return annotated_image, detections, has_detections


def save_result_image(
    annotated_image: np.ndarray, 
    output_path: Path, 
    logger: logging.Logger
) -> bool:
    """
    Save annotated image to output directory.
    
    Args:
        annotated_image: Image with bounding boxes drawn
        output_path: Output file path
        logger: Logger instance
        
    Returns:
        True if save successful, False otherwise
    """
    try:
        cv2.imwrite(str(output_path), annotated_image)
        return True
    except Exception as e:
        logger.error(f"Failed to save image {output_path}: {e}")
        return False


def log_detection_result(
    csv_path: str,
    filename: str,
    detected: bool,
    count: int,
    processing_time: float,
    logger: logging.Logger
) -> None:
    """
    Log detection result to CSV file.
    
    Args:
        csv_path: Path to CSV log file
        filename: Image filename
        detected: Whether any objects were detected
        count: Number of detections
        processing_time: Processing time in milliseconds
        logger: Logger instance
    """
    try:
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([filename, detected, count, f"{processing_time:.1f}"])
    except Exception as e:
        logger.error(f"Failed to write to CSV log: {e}")


def process_images(
    model: YOLO,
    input_dir: Path,
    output_dir: Path,
    csv_log_path: str,
    logger: logging.Logger,
    confidence_threshold: float = 0.25
) -> None:
    """
    Process all images in the input directory.
    
    Args:
        model: YOLO model instance
        input_dir: Input directory path
        output_dir: Output directory path
        csv_log_path: Path to CSV log file
        logger: Logger instance
        confidence_threshold: Minimum confidence for detections
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Get all image files
    image_files = get_image_files(input_dir, logger)
    
    if not image_files:
        logger.warning("No images to process")
        return
    
    total_images = len(image_files)
    successful_processed = 0
    total_detections = 0
    
    logger.info(f"Starting batch processing of {total_images} images...")
    
    for i, image_path in enumerate(image_files, 1):
        try:
            # Record start time
            start_time = time.time()
            
            logger.info(f"Processing [{i}/{total_images}]: {image_path.name}")
            
            # Perform detection
            annotated_image, detections, has_detections = detect_objects(
                model, image_path, confidence_threshold
            )
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Generate output filename (always save as PNG)
            output_filename = image_path.stem + ".png"
            output_path = output_dir / output_filename
            
            # Save result image
            if save_result_image(annotated_image, output_path, logger):
                successful_processed += 1
                detection_count = len(detections)
                total_detections += detection_count
                
                # Log results
                log_detection_result(
                    csv_log_path,
                    image_path.name,
                    has_detections,
                    detection_count,
                    processing_time,
                    logger
                )
                
                # Console output
                if has_detections:
                    classes_detected = [d['class'] for d in detections]
                    logger.info(
                        f"✓ Detected {detection_count} objects: "
                        f"{', '.join(set(classes_detected))} "
                        f"(Time: {processing_time:.1f}ms)"
                    )
                else:
                    logger.info(f"✓ No objects detected (Time: {processing_time:.1f}ms)")
            
        except Exception as e:
            logger.error(f"Failed to process {image_path.name}: {e}")
            # Log failed processing
            log_detection_result(
                csv_log_path,
                image_path.name,
                False,
                0,
                0.0,
                logger
            )
    
    # Summary
    logger.info("=" * 60)
    logger.info("PROCESSING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total images: {total_images}")
    logger.info(f"Successfully processed: {successful_processed}")
    logger.info(f"Failed: {total_images - successful_processed}")
    logger.info(f"Total detections: {total_detections}")
    logger.info(f"CSV log saved to: {csv_log_path}")
    logger.info("=" * 60)


def main():
    """昆虫検出アプリケーションを実行するメイン関数。"""
    parser = argparse.ArgumentParser(
        description="YOLOv8を使用した昆虫検出アプリケーション",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python detect_insect.py --input input_images/ --output output_images/
  python detect_insect.py --input input_images/ --output results/ --model yolov8s.pt
        """
    )
    
    # 必須引数
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='処理する画像を含む入力ディレクトリ'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='処理済み画像の出力ディレクトリ'
    )
    
    # オプション引数
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8n.pt',
        help='YOLOv8モデル重みファイルのパス (デフォルト: yolov8n.pt)'
    )
    
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='検出の信頼度闾値 (デフォルト: 0.25)'
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        default='logs',
        help='ログファイル用ディレクトリ (デフォルト: logs)'
    )
    
    args = parser.parse_args()
    
    # Pathオブジェクトに変換
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    log_dir = Path(args.log_dir)
    
    # 入力ディレクトリの検証
    if not input_dir.exists():
        print(f"エラー: 入力ディレクトリ '{input_dir}' が存在しません")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"エラー: '{input_dir}' はディレクトリではありません")
        sys.exit(1)
    
    # ログ設定を初期化
    logger, csv_log_path = setup_logging(log_dir)
    
    # モデルを読み込み
    model = load_model(args.model, logger)
    
    # モデル情報をログ出力
    logger.info(f"モデルクラス: {list(model.names.values())}")
    logger.info(f"入力ディレクトリ: {input_dir}")
    logger.info(f"出力ディレクトリ: {output_dir}")
    logger.info(f"信頼度闾値: {args.conf}")
    
    # 画像を処理
    try:
        process_images(
            model=model,                      # モデルインスタンス
            input_dir=input_dir,              # 入力ディレクトリ
            output_dir=output_dir,            # 出力ディレクトリ
            csv_log_path=csv_log_path,        # CSVログパス
            logger=logger,                    # ロガー
            confidence_threshold=args.conf    # 信頼度闾値
        )
        logger.info("処理が成功しました")
    except KeyboardInterrupt:
        logger.info("ユーザーによって処理が中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"処理が失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()