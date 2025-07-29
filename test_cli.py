#!/usr/bin/env python3
"""
CLI機能テストスクリプト

Phase 7で実装されたCLI機能の動作確認を行う。
"""

import subprocess
import sys
import json
from pathlib import Path
import time
import os


def run_command(cmd: str, capture_output: bool = True) -> tuple:
    """
    コマンド実行
    
    Args:
        cmd: 実行コマンド
        capture_output: 出力キャプチャするか
        
    Returns:
        tuple: (return_code, stdout, stderr)
    """
    print(f"🔧 実行中: {cmd}")
    
    try:
        if capture_output:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, timeout=30)
            return result.returncode, "", ""
    except subprocess.TimeoutExpired:
        print("⏰ タイムアウト")
        return -1, "", "Timeout"
    except Exception as e:
        print(f"❌ エラー: {e}")
        return -1, "", str(e)


def test_basic_cli():
    """基本CLI機能テスト"""
    print("\n" + "="*50)
    print("📋 基本CLI機能テスト")
    print("="*50)
    
    tests = [
        # ヘルプ表示
        ("python cli.py --help", "ヘルプ表示"),
        
        # 設定検証（存在しない場合はスキップ）
        ("python cli.py status --help", "statusコマンドヘルプ"),
        ("python cli.py detect --help", "detectコマンドヘルプ"),
        ("python cli.py diagnose --help", "diagnoseコマンドヘルプ"),
    ]
    
    results = []
    
    for cmd, description in tests:
        code, stdout, stderr = run_command(cmd)
        
        if code == 0:
            print(f"✅ {description}: 成功")
            results.append(True)
        else:
            print(f"❌ {description}: 失敗 (code: {code})")
            if stderr:
                print(f"   エラー: {stderr[:200]}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 基本CLI成功率: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    return success_rate > 80


def test_system_status():
    """システム状態関連テスト"""
    print("\n" + "="*50)
    print("🔍 システム状態テスト")
    print("="*50)
    
    # システムファイル存在確認
    required_files = [
        "main.py",
        "cli.py",
        "batch_runner.py",
        "config/config_manager.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 必須ファイルが不足: {missing_files}")
        return False
    
    print("✅ 必須ファイル確認完了")
    
    # 基本的な状態確認（初期化エラーが出ても構わない）
    tests = [
        ("python cli.py diagnose --help", "診断コマンドヘルプ", True),
        ("python cli.py cleanup --help", "クリーンアップヘルプ", True),
    ]
    
    results = []
    for cmd, description, required in tests:
        code, stdout, stderr = run_command(cmd)
        
        if code == 0:
            print(f"✅ {description}: 成功")
            results.append(True)
        else:
            print(f"{'❌' if required else '⚠️'} {description}: {'失敗' if required else '警告'}")
            if required:
                results.append(False)
            else:
                results.append(True)
    
    return all(results)


def test_batch_runner():
    """バッチランナーテスト"""
    print("\n" + "="*50)
    print("⚙️ バッチランナーテスト")
    print("="*50)
    
    tests = [
        ("python batch_runner.py --help", "バッチランナーヘルプ"),
        ("python batch_runner.py list", "ジョブ一覧表示"),
    ]
    
    results = []
    
    for cmd, description in tests:
        code, stdout, stderr = run_command(cmd)
        
        if code == 0:
            print(f"✅ {description}: 成功")
            results.append(True)
        else:
            print(f"❌ {description}: 失敗")
            print(f"   エラー: {stderr[:200] if stderr else 'No stderr'}")
            results.append(False)
    
    # ジョブ追加テスト（テスト用）
    test_job_name = "test_job_cli_test"
    
    print(f"\n🔧 テストジョブ操作")
    
    # ジョブ追加
    add_cmd = f'python batch_runner.py add {test_job_name} "echo test" --type daily --time 12:00'
    code, stdout, stderr = run_command(add_cmd)
    
    if code == 0:
        print(f"✅ テストジョブ追加: 成功")
        
        # ジョブ削除
        remove_cmd = f'python batch_runner.py remove {test_job_name}'
        code2, stdout2, stderr2 = run_command(remove_cmd)
        
        if code2 == 0:
            print(f"✅ テストジョブ削除: 成功")
            results.append(True)
        else:
            print(f"❌ テストジョブ削除: 失敗")
            results.append(False)
    else:
        print(f"❌ テストジョブ追加: 失敗")
        results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 バッチランナー成功率: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    return success_rate > 70


def test_config_structure():
    """設定構造テスト"""
    print("\n" + "="*50)
    print("📁 設定・ディレクトリ構造テスト")
    print("="*50)
    
    # 必要なディレクトリ
    required_dirs = [
        "config",
        "models",
        "utils",
        "logs",
        "output",
    ]
    
    # ディレクトリ作成確認
    created_dirs = []
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(dir_name)
                print(f"📁 ディレクトリ作成: {dir_name}")
            except Exception as e:
                print(f"❌ ディレクトリ作成失敗: {dir_name} - {e}")
                return False
        else:
            print(f"✅ ディレクトリ存在確認: {dir_name}")
    
    # 設定ファイル確認
    config_file = Path("config/system_config.json")
    if config_file.exists():
        print(f"✅ 設定ファイル存在: {config_file}")
        try:
            with open(config_file, 'r') as f:
                json.load(f)
            print(f"✅ 設定ファイル形式確認: 有効なJSON")
        except json.JSONDecodeError:
            print(f"⚠️ 設定ファイル形式警告: 無効なJSON")
    else:
        print(f"⚠️ 設定ファイル未作成: {config_file}")
    
    if created_dirs:
        print(f"\n📝 作成されたディレクトリ: {', '.join(created_dirs)}")
    
    return True


def create_test_report():
    """テストレポート作成"""
    print("\n" + "="*50)
    print("📊 テストレポート生成")
    print("="*50)
    
    report = {
        "test_datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "working_directory": str(Path.cwd()),
        "tests": {}
    }
    
    # 各テスト実行
    tests = [
        ("basic_cli", test_basic_cli, "基本CLI機能"),
        ("system_status", test_system_status, "システム状態機能"),
        ("batch_runner", test_batch_runner, "バッチランナー機能"),
        ("config_structure", test_config_structure, "設定・ディレクトリ構造"),
    ]
    
    overall_success = True
    
    for test_name, test_func, description in tests:
        try:
            result = test_func()
            report["tests"][test_name] = {
                "description": description,
                "result": "PASS" if result else "FAIL",
                "success": result
            }
            
            if not result:
                overall_success = False
                
        except Exception as e:
            print(f"❌ テスト実行エラー ({test_name}): {e}")
            report["tests"][test_name] = {
                "description": description,
                "result": "ERROR",
                "success": False,
                "error": str(e)
            }
            overall_success = False
    
    # レポート保存
    report_file = Path("test_report.json")
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 テストレポート保存: {report_file}")
    except Exception as e:
        print(f"❌ レポート保存エラー: {e}")
    
    # サマリー表示
    print("\n" + "="*50)
    print("🎯 テスト結果サマリー")
    print("="*50)
    
    for test_name, test_data in report["tests"].items():
        status_icon = "✅" if test_data["success"] else "❌"
        print(f"{status_icon} {test_data['description']}: {test_data['result']}")
    
    print(f"\n🏁 総合結果: {'SUCCESS' if overall_success else 'PARTIAL SUCCESS'}")
    
    if overall_success:
        print("🎉 Phase 7 CLI拡張機能の実装が完了しました！")
    else:
        print("⚠️ 一部のテストが失敗しました。実装を確認してください。")
    
    return overall_success


def main():
    """メイン関数"""
    print("🚀 Phase 7 CLI機能テスト開始")
    print("="*50)
    
    try:
        # 作業ディレクトリ確認
        cwd = Path.cwd()
        print(f"📁 作業ディレクトリ: {cwd}")
        
        # 主要ファイル確認
        main_files = ["main.py", "cli.py", "batch_runner.py"]
        missing_files = [f for f in main_files if not Path(f).exists()]
        
        if missing_files:
            print(f"❌ 必須ファイルが見つかりません: {missing_files}")
            print("正しいディレクトリでテストを実行してください。")
            return 1
        
        # テスト実行
        success = create_test_report()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ テストが中断されました")
        return 1
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())