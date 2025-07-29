"""
モデル管理モジュール

YOLOv8モデルの管理・ダウンロード・検証を行う。
- Hugging Faceからのモデルダウンロード
- ローカルモデルの管理・検証
- モデルバージョン管理
- モデル性能評価
- モデル変換・最適化
"""

import logging
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import shutil
import requests
from urllib.parse import urlparse

# Hugging Face Hub
try:
    from huggingface_hub import hf_hub_download, list_repo_files
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    logging.warning("huggingface_hub not available. Install with: pip install huggingface_hub")

# 機械学習ライブラリ
try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("ultralytics not available. Install with: pip install ultralytics")

# プロジェクト内モジュール
from config.config_manager import ConfigManager


@dataclass
class ModelInfo:
    """モデル情報データクラス"""
    name: str
    version: str
    path: str
    size_mb: float
    sha256_hash: str
    download_date: str
    source: str  # "local", "huggingface", "url"
    source_url: str = ""
    task: str = "detection"  # "detection", "classification", "segmentation"
    input_size: Tuple[int, int] = (640, 640)
    num_classes: int = 1
    class_names: List[str] = None
    performance_metrics: Dict[str, float] = None
    validated: bool = False
    validation_date: str = ""


@dataclass
class ModelRegistry:
    """モデルレジストリ"""
    models: Dict[str, ModelInfo]
    default_model: str = ""
    last_updated: str = ""


class ModelManager:
    """
    YOLOv8モデル管理クラス
    
    Features:
    - Hugging Faceからの自動ダウンロード
    - ローカルモデルファイル管理
    - モデル検証・ハッシュチェック
    - モデル性能評価
    - バージョン管理
    - 設定ファイル連携
    """
    
    def __init__(self, 
                 model_dir: str = "./weights",
                 config_manager: Optional[ConfigManager] = None):
        """
        モデル管理器初期化
        
        Args:
            model_dir: モデル保存ディレクトリ
            config_manager: 設定管理器
        """
        self.logger = logging.getLogger(__name__ + '.ModelManager')
        
        # ディレクトリ設定
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # 設定管理
        self.config_manager = config_manager
        
        # レジストリファイル
        self.registry_file = self.model_dir / "model_registry.json"
        
        # モデルレジストリ
        self.registry = self._load_registry()
        
        # Hugging Face設定
        self.hf_repo_id = "Murasan/beetle-detection-yolov8"
        self.available_formats = ["pytorch", "onnx", "tflite"]
        
        # 可用性チェック
        self.available = YOLO_AVAILABLE
        self.hf_available = HF_HUB_AVAILABLE
        
        if not self.available:
            self.logger.error("YOLO not available for model management")
        
        self.logger.info("Model manager initialized")
    
    def _load_registry(self) -> ModelRegistry:
        """モデルレジストリ読み込み"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # ModelInfoオブジェクトに変換
                models = {}
                for name, model_data in data.get('models', {}).items():
                    models[name] = ModelInfo(**model_data)
                
                return ModelRegistry(
                    models=models,
                    default_model=data.get('default_model', ''),
                    last_updated=data.get('last_updated', '')
                )
            else:
                # 新規レジストリ
                return ModelRegistry(models={})
                
        except Exception as e:
            self.logger.error(f"Failed to load registry: {e}")
            return ModelRegistry(models={})
    
    def _save_registry(self) -> None:
        """モデルレジストリ保存"""
        try:
            # データを辞書形式に変換
            registry_data = {
                'models': {name: asdict(info) for name, info in self.registry.models.items()},
                'default_model': self.registry.default_model,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            self.registry.last_updated = datetime.now().isoformat()
            self.logger.debug("Model registry saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}")
    
    def download_from_huggingface(self, 
                                 model_format: str = "pytorch",
                                 force_download: bool = False) -> Optional[str]:
        """
        Hugging Faceからモデルダウンロード
        
        Args:
            model_format: モデル形式 ("pytorch", "onnx", "tflite")
            force_download: 強制再ダウンロード
            
        Returns:
            Optional[str]: ダウンロード済みモデルパス
        """
        if not self.hf_available:
            self.logger.error("Hugging Face Hub not available")
            return None
        
        try:
            self.logger.info(f"Downloading model from Hugging Face: {self.hf_repo_id}")
            
            # ファイル名決定
            if model_format.lower() == "pytorch":
                filename = "best.pt"
                model_name = "beetle-detection-pytorch"
            elif model_format.lower() == "onnx":
                filename = "best.onnx"
                model_name = "beetle-detection-onnx"
            elif model_format.lower() == "tflite":
                filename = "best.tflite"
                model_name = "beetle-detection-tflite"
            else:
                raise ValueError(f"Unsupported model format: {model_format}")
            
            # 既存モデルチェック
            existing_path = self.model_dir / filename
            if existing_path.exists() and not force_download:
                if model_name in self.registry.models:
                    self.logger.info(f"Model already exists: {existing_path}")
                    return str(existing_path)
            
            # ダウンロード実行
            downloaded_path = hf_hub_download(
                repo_id=self.hf_repo_id,
                filename=filename,
                local_dir=str(self.model_dir),
                force_download=force_download
            )
            
            # モデル情報作成・登録
            model_info = self._create_model_info(
                name=model_name,
                path=downloaded_path,
                source="huggingface",
                source_url=f"https://huggingface.co/{self.hf_repo_id}"
            )
            
            if model_info:
                self.registry.models[model_name] = model_info
                
                # デフォルトモデル設定（PyTorchモデルを優先）
                if model_format.lower() == "pytorch" or not self.registry.default_model:
                    self.registry.default_model = model_name
                
                self._save_registry()
                
                self.logger.info(f"Model downloaded and registered: {downloaded_path}")
                return downloaded_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Hugging Face download failed: {e}")
            return None
    
    def add_local_model(self, 
                       model_path: str,
                       model_name: Optional[str] = None,
                       copy_to_weights: bool = True) -> bool:
        """
        ローカルモデルファイルを管理対象に追加
        
        Args:
            model_path: モデルファイルパス
            model_name: モデル名（Noneの場合はファイル名から生成）
            copy_to_weights: weightsディレクトリにコピーするか
            
        Returns:
            bool: 追加成功可否
        """
        try:
            source_path = Path(model_path)
            if not source_path.exists():
                self.logger.error(f"Model file not found: {model_path}")
                return False
            
            # モデル名決定
            if model_name is None:
                model_name = source_path.stem
            
            # 保存先パス決定
            if copy_to_weights:
                target_path = self.model_dir / source_path.name
                shutil.copy2(source_path, target_path)
                self.logger.info(f"Model copied to: {target_path}")
            else:
                target_path = source_path
            
            # モデル情報作成・登録
            model_info = self._create_model_info(
                name=model_name,
                path=str(target_path),
                source="local"
            )
            
            if model_info:
                self.registry.models[model_name] = model_info
                
                # デフォルトモデル設定（初回追加時）
                if not self.registry.default_model:
                    self.registry.default_model = model_name
                
                self._save_registry()
                
                self.logger.info(f"Local model registered: {model_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Local model addition failed: {e}")
            return False
    
    def _create_model_info(self, 
                          name: str,
                          path: str,
                          source: str,
                          source_url: str = "") -> Optional[ModelInfo]:
        """モデル情報作成"""
        try:
            model_path = Path(path)
            
            # ファイル情報取得
            file_size = model_path.stat().st_size / (1024 * 1024)  # MB
            sha256_hash = self._calculate_file_hash(model_path)
            
            # モデル検証・詳細情報取得
            model_details = self._validate_and_analyze_model(model_path)
            
            return ModelInfo(
                name=name,
                version="1.0",  # 基本バージョン
                path=str(model_path),
                size_mb=round(file_size, 2),
                sha256_hash=sha256_hash,
                download_date=datetime.now().isoformat(),
                source=source,
                source_url=source_url,
                task=model_details.get('task', 'detection'),
                input_size=tuple(model_details.get('input_size', [640, 640])),
                num_classes=model_details.get('num_classes', 1),
                class_names=model_details.get('class_names', ['insect']),
                performance_metrics=model_details.get('performance_metrics', {}),
                validated=model_details.get('validated', False),
                validation_date=datetime.now().isoformat() if model_details.get('validated') else ""
            )
            
        except Exception as e:
            self.logger.error(f"Model info creation failed: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """ファイルハッシュ計算"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Hash calculation failed: {e}")
            return ""
    
    def _validate_and_analyze_model(self, model_path: Path) -> Dict[str, Any]:
        """モデル検証・解析"""
        if not self.available:
            return {"validated": False, "error": "YOLO not available"}
        
        try:
            # YOLOモデル読み込み
            model = YOLO(str(model_path))
            
            # 基本情報取得
            details = {
                "validated": True,
                "task": getattr(model, 'task', 'detection'),
                "input_size": [640, 640],  # デフォルト
                "num_classes": 1,
                "class_names": ['insect']
            }
            
            # クラス情報取得
            if hasattr(model, 'names') and model.names:
                details["class_names"] = list(model.names.values())
                details["num_classes"] = len(model.names)
            
            # 性能メトリクス（利用可能な場合）
            if hasattr(model, 'metrics') and model.metrics:
                metrics = {}
                for key, value in model.metrics.items():
                    if isinstance(value, (int, float)):
                        metrics[key] = float(value)
                details["performance_metrics"] = metrics
            
            self.logger.debug(f"Model validation successful: {model_path}")
            return details
            
        except Exception as e:
            self.logger.error(f"Model validation failed for {model_path}: {e}")
            return {"validated": False, "error": str(e)}
    
    def get_model_path(self, model_name: Optional[str] = None) -> Optional[str]:
        """
        モデルパス取得
        
        Args:
            model_name: モデル名（Noneの場合はデフォルトモデル）
            
        Returns:
            Optional[str]: モデルファイルパス
        """
        try:
            if model_name is None:
                model_name = self.registry.default_model
            
            if not model_name or model_name not in self.registry.models:
                self.logger.error(f"Model not found: {model_name}")
                return None
            
            model_info = self.registry.models[model_name]
            model_path = Path(model_info.path)
            
            if not model_path.exists():
                self.logger.error(f"Model file not found: {model_path}")
                return None
            
            return str(model_path)
            
        except Exception as e:
            self.logger.error(f"Model path retrieval failed: {e}")
            return None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        利用可能モデル一覧取得
        
        Returns:
            List[Dict[str, Any]]: モデル情報リスト
        """
        models = []
        for name, info in self.registry.models.items():
            model_dict = asdict(info)
            model_dict['is_default'] = (name == self.registry.default_model)
            model_dict['exists'] = Path(info.path).exists()
            models.append(model_dict)
        
        return models
    
    def set_default_model(self, model_name: str) -> bool:
        """
        デフォルトモデル設定
        
        Args:
            model_name: モデル名
            
        Returns:
            bool: 設定成功可否
        """
        try:
            if model_name not in self.registry.models:
                self.logger.error(f"Model not found: {model_name}")
                return False
            
            self.registry.default_model = model_name
            self._save_registry()
            
            self.logger.info(f"Default model set to: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Default model setting failed: {e}")
            return False
    
    def remove_model(self, model_name: str, delete_file: bool = False) -> bool:
        """
        モデル削除
        
        Args:
            model_name: モデル名
            delete_file: ファイルも削除するか
            
        Returns:
            bool: 削除成功可否
        """
        try:
            if model_name not in self.registry.models:
                self.logger.error(f"Model not found: {model_name}")
                return False
            
            model_info = self.registry.models[model_name]
            
            # ファイル削除
            if delete_file:
                model_path = Path(model_info.path)
                if model_path.exists():
                    model_path.unlink()
                    self.logger.info(f"Model file deleted: {model_path}")
            
            # レジストリから削除
            del self.registry.models[model_name]
            
            # デフォルトモデル更新
            if self.registry.default_model == model_name:
                if self.registry.models:
                    self.registry.default_model = next(iter(self.registry.models.keys()))
                else:
                    self.registry.default_model = ""
            
            self._save_registry()
            
            self.logger.info(f"Model removed: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Model removal failed: {e}")
            return False
    
    def check_updates(self) -> Dict[str, Any]:
        """
        Hugging Faceでの更新チェック
        
        Returns:
            Dict[str, Any]: 更新情報
        """
        if not self.hf_available:
            return {"error": "Hugging Face Hub not available"}
        
        try:
            # リポジトリファイル一覧取得
            repo_files = list_repo_files(self.hf_repo_id)
            
            # 利用可能なモデルファイル
            available_models = {
                "pytorch": "best.pt" in repo_files,
                "onnx": "best.onnx" in repo_files,
                "tflite": "best.tflite" in repo_files
            }
            
            # ローカルモデルとの比較
            local_models = [
                name for name, info in self.registry.models.items()
                if info.source == "huggingface"
            ]
            
            return {
                "repository": self.hf_repo_id,
                "available_formats": available_models,
                "local_models": local_models,
                "last_checked": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Update check failed: {e}")
            return {"error": str(e)}
    
    def auto_setup(self) -> bool:
        """
        自動セットアップ（デフォルトモデルダウンロード）
        
        Returns:
            bool: セットアップ成功可否
        """
        try:
            self.logger.info("Starting auto setup...")
            
            # 既存モデルチェック
            if self.registry.models and self.registry.default_model:
                default_path = self.get_model_path()
                if default_path and Path(default_path).exists():
                    self.logger.info("Default model already available")
                    return True
            
            # Hugging Faceからダウンロード
            if self.hf_available:
                model_path = self.download_from_huggingface("pytorch")
                if model_path:
                    self.logger.info("Auto setup completed with Hugging Face model")
                    return True
            
            self.logger.warning("Auto setup could not download model")
            return False
            
        except Exception as e:
            self.logger.error(f"Auto setup failed: {e}")
            return False
    
    def get_model_info(self, model_name: Optional[str] = None) -> Optional[ModelInfo]:
        """
        モデル情報取得
        
        Args:
            model_name: モデル名（Noneの場合はデフォルト）
            
        Returns:
            Optional[ModelInfo]: モデル情報
        """
        if model_name is None:
            model_name = self.registry.default_model
        
        return self.registry.models.get(model_name)
    
    def cleanup(self) -> None:
        """リソース解放"""
        try:
            # レジストリ保存
            self._save_registry()
            
            self.logger.info("Model manager cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Model manager cleanup failed: {e}")


# 使用例・テスト関数
def test_model_manager():
    """モデル管理器のテスト"""
    import logging
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # モデル管理器作成
    manager = ModelManager()
    
    try:
        # 自動セットアップ
        logger.info("Testing auto setup...")
        if manager.auto_setup():
            logger.info("Auto setup successful")
        else:
            logger.warning("Auto setup failed")
        
        # モデル一覧表示
        models = manager.list_models()
        logger.info(f"Available models: {len(models)}")
        for model in models:
            logger.info(f"  - {model['name']}: {model['path']} ({'default' if model['is_default'] else 'available'})")
        
        # デフォルトモデル情報
        default_path = manager.get_model_path()
        if default_path:
            logger.info(f"Default model path: {default_path}")
            
            # モデル詳細情報
            model_info = manager.get_model_info()
            if model_info:
                logger.info(f"Model info: {model_info.name} ({model_info.size_mb:.1f}MB)")
        
        # 更新チェック
        logger.info("Checking for updates...")
        update_info = manager.check_updates()
        logger.info(f"Update info: {update_info}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        # クリーンアップ
        manager.cleanup()


if __name__ == "__main__":
    test_model_manager()