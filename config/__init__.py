"""
昆虫自動観察システム - 設定管理パッケージ

このパッケージには、システム設定の読み込み・保存・検証を行う機能が含まれています。

Modules:
    config_manager: 設定ファイルの管理クラス
"""

from .config_manager import ConfigManager

__all__ = ['ConfigManager']

__version__ = '1.0.0'