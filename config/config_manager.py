"""
昆虫自動観察システム - 設定管理モジュール

このモジュールはシステム設定の読み込み・保存・検証・管理を行います。

Classes:
    ConfigManager: 設定管理クラス
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from models.system_models import SystemConfiguration


class ConfigManager:
    """設定管理クラス
    
    システム設定ファイルの読み込み・保存・検証を行います。
    
    Attributes:
        config_path: 設定ファイルのパス
        config: 現在の設定オブジェクト
        logger: ロガーインスタンス
    """
    
    def __init__(self, config_path: str = "./config/system_config.json"):
        """ConfigManager初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        self.config_path = Path(config_path)
        self.config: Optional[SystemConfiguration] = None
        self.logger = logging.getLogger(__name__)
        
        # 設定ディレクトリが存在しない場合は作成
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> SystemConfiguration:
        """設定ファイルを読み込み
        
        Returns:
            読み込まれたシステム設定
            
        Raises:
            FileNotFoundError: 設定ファイルが存在しない場合
            json.JSONDecodeError: JSONの形式が不正な場合
            ValueError: 設定値が不正な場合
        """
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Config file not found: {self.config_path}")
                self.logger.info("Creating default configuration")
                self.config = SystemConfiguration()
                self.save_config(self.config)
                return self.config
            
            self.logger.info(f"Loading configuration from: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.config = SystemConfiguration.from_dict(config_data)
            
            # 設定値の検証
            validation_errors = self.validate_config(self.config)
            if validation_errors:
                error_message = f"Configuration validation failed: {validation_errors}"
                self.logger.error(error_message)
                raise ValueError(error_message)
            
            self.logger.info("Configuration loaded successfully")
            return self.config
            
        except json.JSONDecodeError as e:
            error_message = f"Invalid JSON in config file {self.config_path}: {e}"
            self.logger.error(error_message)
            raise json.JSONDecodeError(error_message, e.doc, e.pos)
        
        except Exception as e:
            error_message = f"Failed to load configuration: {e}"
            self.logger.error(error_message)
            raise
    
    def save_config(self, config: SystemConfiguration) -> None:
        """設定をファイルに保存
        
        Args:
            config: 保存する設定オブジェクト
            
        Raises:
            ValueError: 設定値が不正な場合
            OSError: ファイル書き込みに失敗した場合
        """
        try:
            # 設定値の検証
            validation_errors = self.validate_config(config)
            if validation_errors:
                error_message = f"Configuration validation failed: {validation_errors}"
                self.logger.error(error_message)
                raise ValueError(error_message)
            
            # バックアップファイル作成（既存ファイルがある場合）
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.json.backup')
                self.config_path.rename(backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # 設定保存
            self.logger.info(f"Saving configuration to: {self.config_path}")
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(config.to_json(indent=2))
            
            self.config = config
            self.logger.info("Configuration saved successfully")
            
        except Exception as e:
            error_message = f"Failed to save configuration: {e}"
            self.logger.error(error_message)
            
            # バックアップからの復旧を試行
            backup_path = self.config_path.with_suffix('.json.backup')
            if backup_path.exists():
                backup_path.rename(self.config_path)
                self.logger.info("Restored from backup")
            
            raise OSError(error_message)
    
    def validate_config(self, config: SystemConfiguration) -> List[str]:
        """設定値の検証
        
        Args:
            config: 検証対象の設定
            
        Returns:
            検証エラーメッセージのリスト（空の場合は検証成功）
        """
        errors = []
        
        try:
            # SystemConfiguration自体の検証
            config_errors = config.validate()
            errors.extend(config_errors)
            
            # ファイルパス存在チェック
            model_path = Path(config.model_path)
            if not model_path.exists() and not str(model_path).startswith('./weights/'):
                # weightsディレクトリのファイルは動的にダウンロードされる可能性があるため警告のみ
                self.logger.warning(f"Model file not found: {config.model_path}")
            
            # 論理的整合性チェック
            if config.confidence_threshold >= config.nms_threshold:
                errors.append("confidence_threshold should be less than nms_threshold")
            
            if config.camera_resolution_width * config.camera_resolution_height > 8294400:  # 4K以上
                errors.append("Camera resolution too high, may cause performance issues")
            
            # 環境変数による設定上書きのチェック
            env_overrides = self.get_env_config()
            if env_overrides:
                self.logger.info(f"Environment variable overrides found: {list(env_overrides.keys())}")
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors
    
    def get_env_config(self) -> Dict[str, Any]:
        """環境変数からの設定取得
        
        環境変数による設定の上書きをサポートします。
        
        Returns:
            環境変数による設定辞書
        """
        env_config = {}
        
        # 環境変数マッピング
        env_mappings = {
            'INSECT_OBSERVER_LOG_LEVEL': ('log_level', str),
            'INSECT_OBSERVER_DETECTION_INTERVAL': ('detection_interval_seconds', int),
            'INSECT_OBSERVER_MODEL_PATH': ('model_path', str),
            'INSECT_OBSERVER_CONFIDENCE_THRESHOLD': ('confidence_threshold', float),
            'INSECT_OBSERVER_CAMERA_WIDTH': ('camera_resolution_width', int),
            'INSECT_OBSERVER_CAMERA_HEIGHT': ('camera_resolution_height', int),
            'INSECT_OBSERVER_LED_BRIGHTNESS': ('ir_led_brightness', float),
            'INSECT_OBSERVER_DATA_RETENTION_DAYS': ('data_retention_days', int),
        }
        
        for env_var, (config_key, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if value_type == bool:
                        parsed_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        parsed_value = value_type(env_value)
                    
                    env_config[config_key] = parsed_value
                    self.logger.info(f"Environment override: {config_key} = {parsed_value}")
                    
                except ValueError as e:
                    self.logger.warning(f"Invalid environment variable {env_var}={env_value}: {e}")
        
        return env_config
    
    def apply_env_overrides(self, config: SystemConfiguration) -> SystemConfiguration:
        """環境変数による設定上書きを適用
        
        Args:
            config: 基準となる設定
            
        Returns:
            環境変数が適用された設定
        """
        env_overrides = self.get_env_config()
        
        if not env_overrides:
            return config
        
        # 設定の辞書表現を取得
        config_dict = config.to_dict()
        
        # 環境変数による上書き適用
        for key, value in env_overrides.items():
            # ネストした辞書構造への適用
            keys = key.split('.')
            current_dict = config_dict
            
            for k in keys[:-1]:
                if k not in current_dict:
                    current_dict[k] = {}
                current_dict = current_dict[k]
            
            current_dict[keys[-1]] = value
        
        # 更新された辞書から新しい設定オブジェクトを作成
        return SystemConfiguration.from_dict(config_dict)
    
    def reload_config(self) -> SystemConfiguration:
        """設定を再読み込み
        
        Returns:
            再読み込みされた設定
        """
        self.logger.info("Reloading configuration")
        return self.load_config()
    
    def get_config(self) -> SystemConfiguration:
        """現在の設定を取得
        
        Returns:
            現在の設定（未読み込みの場合は自動的に読み込み）
        """
        if self.config is None:
            return self.load_config()
        return self.config
    
    def create_default_config(self) -> SystemConfiguration:
        """デフォルト設定を作成
        
        Returns:
            デフォルト設定オブジェクト
        """
        self.logger.info("Creating default configuration")
        return SystemConfiguration()
    
    def update_config(self, **kwargs) -> None:
        """設定の部分更新
        
        Args:
            **kwargs: 更新する設定項目
            
        Raises:
            ValueError: 現在の設定が読み込まれていない場合
        """
        if self.config is None:
            raise ValueError("No configuration loaded. Call load_config() first.")
        
        # 現在の設定の辞書表現を取得
        config_dict = self.config.to_dict()
        
        # 更新項目を適用
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"Updated config: {key} = {value}")
            else:
                self.logger.warning(f"Unknown configuration key: {key}")
        
        # 更新された設定を保存
        self.save_config(self.config)
    
    def export_config(self, export_path: str, format: str = 'json') -> None:
        """設定をエクスポート
        
        Args:
            export_path: エクスポート先パス
            format: エクスポート形式（'json' のみサポート）
            
        Raises:
            ValueError: サポートされていない形式が指定された場合
            ValueError: 現在の設定が読み込まれていない場合
        """
        if self.config is None:
            raise ValueError("No configuration loaded. Call load_config() first.")
        
        if format.lower() != 'json':
            raise ValueError(f"Unsupported export format: {format}")
        
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Exporting configuration to: {export_path}")
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(self.config.to_json(indent=2))
        
        self.logger.info("Configuration exported successfully")
    
    def import_config(self, import_path: str) -> SystemConfiguration:
        """設定をインポート
        
        Args:
            import_path: インポート元パス
            
        Returns:
            インポートされた設定
            
        Raises:
            FileNotFoundError: インポートファイルが存在しない場合
        """
        import_path = Path(import_path)
        
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")
        
        self.logger.info(f"Importing configuration from: {import_path}")
        
        with open(import_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        imported_config = SystemConfiguration.from_dict(config_data)
        
        # インポートした設定を現在の設定として保存
        self.save_config(imported_config)
        
        self.logger.info("Configuration imported successfully")
        return imported_config
    
    def get_config_summary(self) -> Dict[str, Any]:
        """設定のサマリーを取得
        
        Returns:
            設定サマリーの辞書
        """
        if self.config is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "config_path": str(self.config_path),
            "config_version": self.config.config_version,
            "last_updated": self.config.last_updated.isoformat(),
            "detection_interval": self.config.detection_interval_seconds,
            "camera_resolution": f"{self.config.camera_resolution_width}x{self.config.camera_resolution_height}",
            "model_path": self.config.model_path,
            "confidence_threshold": self.config.confidence_threshold,
            "log_level": self.config.log_level
        }