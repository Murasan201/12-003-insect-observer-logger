"""
昆虫自動観察システム - 拡張CLIインターフェース

Click ライブラリを使用した高度なコマンドラインインターフェース。
対話的操作、バッチ処理、スケジューリング機能を提供。
"""

import click
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich import box
import threading
import signal

# プロジェクト内モジュール
from main import InsectObserverSystem, setup_logging


console = Console()


class CLIController:
    """CLI操作用コントローラー"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.system: Optional[InsectObserverSystem] = None
        self.monitoring_active = False
        self.monitoring_thread = None
        
    def initialize_system(self) -> bool:
        """システム初期化"""
        try:
            self.system = InsectObserverSystem(self.config_path)
            return self.system.initialize_system()
        except Exception as e:
            console.print(f"[red]システム初期化エラー: {e}[/red]")
            return False
    
    def cleanup(self):
        """クリーンアップ処理"""
        if self.system:
            self.system.shutdown_system()
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)


# メイングループ
@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), 
              default='./config/system_config.json',
              help='設定ファイルパス')
@click.option('--log-level', '-l', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help='ログレベル')
@click.pass_context
def cli(ctx, config, log_level):
    """昆虫自動観察システム - 拡張CLIインターフェース"""
    # ログ設定
    setup_logging(log_level)
    
    # コンテキストにコントローラーを保存
    ctx.obj = CLIController(config)


@cli.command()
@click.option('--interval', '-i', type=int, default=60,
              help='検出間隔（秒）')
@click.option('--duration', '-d', type=int, default=0,
              help='実行時間（分）。0は無制限')
@click.option('--daemon', is_flag=True,
              help='デーモンモードで実行')
@click.pass_obj
def run(controller: CLIController, interval, duration, daemon):
    """連続観察モードで実行"""
    if daemon:
        console.print("[yellow]デーモンモードはまだ実装されていません[/yellow]")
        return
    
    console.print(Panel.fit(
        f"🐛 昆虫観察システム - 連続モード\n"
        f"検出間隔: {interval}秒\n"
        f"実行時間: {'無制限' if duration == 0 else f'{duration}分'}",
        title="システム起動",
        border_style="green"
    ))
    
    if not controller.initialize_system():
        console.print("[red]システム初期化に失敗しました[/red]")
        return
    
    try:
        # 終了時刻計算
        end_time = None
        if duration > 0:
            end_time = datetime.now() + timedelta(minutes=duration)
        
        # メインループ実行
        controller.system.run_main_loop()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]ユーザーによって中断されました[/yellow]")
    finally:
        controller.cleanup()


@cli.command()
@click.option('--save-image', is_flag=True, help='検出画像を保存')
@click.option('--output-dir', '-o', type=click.Path(), 
              default='./output', help='出力ディレクトリ')
@click.option('--no-led', is_flag=True, help='LED照明を使用しない')
@click.pass_obj
def detect(controller: CLIController, save_image, output_dir, no_led):
    """単発検出を実行"""
    console.print("[blue]単発検出を実行中...[/blue]")
    
    if not controller.initialize_system():
        console.print("[red]システム初期化に失敗しました[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("検出処理中...", total=None)
        
        result = controller.system.run_single_detection()
        progress.update(task, completed=True)
    
    if "error" in result:
        console.print(f"[red]検出エラー: {result['error']}[/red]")
    else:
        # 結果テーブル表示
        table = Table(title="検出結果", box=box.ROUNDED)
        table.add_column("項目", style="cyan")
        table.add_column("値", style="green")
        
        table.add_row("タイムスタンプ", result.get('timestamp', 'N/A'))
        table.add_row("検出数", str(result.get('detection_count', 0)))
        table.add_row("処理時間", f"{result.get('processing_time_ms', 0):.1f} ms")
        table.add_row("成功", "✓" if result.get('success', False) else "✗")
        
        console.print(table)
    
    controller.cleanup()


@cli.command()
@click.argument('date_or_range', required=False)
@click.option('--output-format', '-f', 
              type=click.Choice(['csv', 'json', 'html']),
              default='csv', help='出力形式')
@click.option('--include-charts', is_flag=True, help='グラフを含める')
@click.option('--export-images', is_flag=True, help='画像データをエクスポート')
@click.pass_obj
def analyze(controller: CLIController, date_or_range, output_format, 
            include_charts, export_images):
    """データ分析を実行"""
    # 日付処理
    if not date_or_range:
        date_or_range = (datetime.now() - timedelta(days=1)).date().isoformat()
    
    if ':' in date_or_range:
        # 期間分析
        start_date, end_date = date_or_range.split(':')
        console.print(f"[blue]期間分析: {start_date} ～ {end_date}[/blue]")
        console.print("[yellow]期間分析はまだ実装されていません[/yellow]")
        return
    else:
        # 単日分析
        console.print(f"[blue]{date_or_range} のデータを分析中...[/blue]")
        
        if not controller.initialize_system():
            console.print("[red]システム初期化に失敗しました[/red]")
            return
        
        with console.status("分析処理中..."):
            success = controller.system.run_analysis_for_date(date_or_range)
        
        if success:
            console.print(f"[green]✓ 分析が完了しました[/green]")
        else:
            console.print(f"[red]✗ 分析に失敗しました[/red]")
        
        controller.cleanup()


@cli.command()
@click.option('--json', 'output_json', is_flag=True, help='JSON形式で出力')
@click.option('--detailed', is_flag=True, help='詳細情報を表示')
@click.option('--watch', '-w', is_flag=True, help='リアルタイム監視モード')
@click.pass_obj
def status(controller: CLIController, output_json, detailed, watch):
    """システム状態を表示"""
    if not controller.initialize_system():
        console.print("[red]システム初期化に失敗しました[/red]")
        return
    
    if watch:
        # リアルタイム監視モード
        _watch_system_status(controller)
    else:
        # 単発表示
        status_data = controller.system.get_system_status()
        
        if output_json:
            console.print_json(json.dumps(status_data, indent=2, ensure_ascii=False))
        else:
            _display_status_table(status_data, detailed)
    
    controller.cleanup()


def _display_status_table(status_data: Dict[str, Any], detailed: bool = False):
    """ステータステーブル表示"""
    # システム状態テーブル
    system_table = Table(title="システム状態", box=box.ROUNDED)
    system_table.add_column("項目", style="cyan")
    system_table.add_column("値", style="green")
    
    sys_status = status_data.get('system_status', {})
    system_table.add_row("稼働状態", "稼働中" if sys_status.get('is_running') else "停止")
    system_table.add_row("稼働時間", f"{sys_status.get('uptime_seconds', 0):.0f}秒")
    system_table.add_row("総検出数", str(sys_status.get('total_detections', 0)))
    system_table.add_row("処理画像数", str(sys_status.get('total_images_processed', 0)))
    system_table.add_row("最終検出", sys_status.get('last_detection_time', 'なし'))
    system_table.add_row("エラー数", str(sys_status.get('error_count', 0)))
    
    console.print(system_table)
    
    if detailed:
        # ハードウェア状態
        hw_data = status_data.get('hardware', {})
        if hw_data:
            hw_table = Table(title="ハードウェア状態", box=box.ROUNDED)
            hw_table.add_column("コンポーネント", style="cyan")
            hw_table.add_column("状態", style="green")
            hw_table.add_column("詳細", style="yellow")
            
            # カメラ
            cam_status = hw_data.get('camera', {})
            hw_table.add_row(
                "カメラ",
                "初期化済" if cam_status.get('initialized') else "未初期化",
                f"{cam_status.get('resolution', 'N/A')}"
            )
            
            # LED
            led_status = hw_data.get('led', {})
            hw_table.add_row(
                "IR LED",
                "利用可能" if led_status.get('available') else "利用不可",
                f"明度: {led_status.get('brightness', 0):.1f}"
            )
            
            # システム
            sys_info = hw_data.get('system', {})
            hw_table.add_row(
                "CPU温度",
                f"{sys_info.get('temperature', 0):.1f}°C",
                ""
            )
            
            console.print(hw_table)


def _watch_system_status(controller: CLIController):
    """リアルタイムシステム監視"""
    console.print("[yellow]リアルタイム監視モード (Ctrl+C で終了)[/yellow]\n")
    
    try:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                status_data = controller.system.get_system_status()
                
                # 表示内容を構築
                layout = Table.grid(padding=1)
                
                # メインステータス
                main_panel = _create_status_panel(status_data)
                layout.add_row(main_panel)
                
                # ハードウェア状態
                hw_panel = _create_hardware_panel(status_data.get('hardware', {}))
                layout.add_row(hw_panel)
                
                live.update(layout)
                time.sleep(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]監視を終了しました[/yellow]")


def _create_status_panel(status_data: Dict[str, Any]) -> Panel:
    """ステータスパネル作成"""
    sys_status = status_data.get('system_status', {})
    
    content = f"""
🟢 稼働状態: {'稼働中' if sys_status.get('is_running') else '停止'}
⏱️  稼働時間: {sys_status.get('uptime_seconds', 0):.0f}秒
📸 処理画像: {sys_status.get('total_images_processed', 0)}枚
🐛 総検出数: {sys_status.get('total_detections', 0)}匹
🕐 最終検出: {sys_status.get('last_detection_time', 'なし')}
⚠️  エラー数: {sys_status.get('error_count', 0)}
    """.strip()
    
    return Panel(content, title="システム状態", border_style="green")


def _create_hardware_panel(hw_data: Dict[str, Any]) -> Panel:
    """ハードウェアパネル作成"""
    cam_status = hw_data.get('camera', {})
    led_status = hw_data.get('led', {})
    sys_info = hw_data.get('system', {})
    
    content = f"""
📷 カメラ: {'✓' if cam_status.get('initialized') else '✗'} {cam_status.get('resolution', 'N/A')}
💡 IR LED: {'✓' if led_status.get('available') else '✗'} 明度: {led_status.get('brightness', 0):.1f}
🌡️  CPU温度: {sys_info.get('temperature', 0):.1f}°C
💾 ストレージ: {sys_info.get('storage_free_gb', 0):.1f}GB 空き
    """.strip()
    
    return Panel(content, title="ハードウェア", border_style="blue")


@cli.command()
@click.option('--full', is_flag=True, help='完全診断を実行')
@click.option('--output-file', '-o', type=click.Path(),
              help='結果をファイルに保存')
@click.pass_obj
def diagnose(controller: CLIController, full, output_file):
    """システム診断を実行"""
    console.print("[blue]システム診断を実行中...[/blue]")
    
    if not controller.initialize_system():
        console.print("[red]システム初期化に失敗しました[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # 診断項目
        checks = [
            ("ハードウェアチェック", _check_hardware),
            ("モデルチェック", _check_model),
            ("ストレージチェック", _check_storage),
            ("設定チェック", _check_config),
        ]
        
        if full:
            checks.extend([
                ("カメラテスト", _test_camera),
                ("検出テスト", _test_detection),
            ])
        
        results = {}
        
        for check_name, check_func in checks:
            task = progress.add_task(f"{check_name}...", total=None)
            result = check_func(controller)
            results[check_name] = result
            progress.update(task, completed=True)
    
    # 結果表示
    _display_diagnosis_results(results)
    
    # ファイル保存
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        console.print(f"[green]診断結果を {output_file} に保存しました[/green]")
    
    controller.cleanup()


def _check_hardware(controller: CLIController) -> Dict[str, Any]:
    """ハードウェアチェック"""
    hw_status = controller.system.hardware_controller.get_detailed_status()
    return {
        "camera_initialized": hw_status.get('camera', {}).get('initialized', False),
        "led_available": hw_status.get('led', {}).get('available', False),
        "temperature": hw_status.get('system', {}).get('temperature', 0),
        "status": "OK" if hw_status.get('camera', {}).get('initialized', False) else "NG"
    }


def _check_model(controller: CLIController) -> Dict[str, Any]:
    """モデルチェック"""
    model_status = controller.system.model_manager.check_model_status()
    return {
        "model_exists": model_status.get('model_exists', False),
        "model_path": model_status.get('model_path', ''),
        "status": "OK" if model_status.get('model_exists', False) else "NG"
    }


def _check_storage(controller: CLIController) -> Dict[str, Any]:
    """ストレージチェック"""
    import shutil
    stat = shutil.disk_usage('.')
    free_gb = stat.free / (1024**3)
    return {
        "free_space_gb": round(free_gb, 2),
        "total_space_gb": round(stat.total / (1024**3), 2),
        "usage_percent": round((stat.used / stat.total) * 100, 1),
        "status": "OK" if free_gb > 1.0 else "WARNING"
    }


def _check_config(controller: CLIController) -> Dict[str, Any]:
    """設定チェック"""
    config_path = Path(controller.config_path)
    return {
        "config_exists": config_path.exists(),
        "config_readable": config_path.is_file() if config_path.exists() else False,
        "status": "OK" if config_path.exists() else "NG"
    }


def _test_camera(controller: CLIController) -> Dict[str, Any]:
    """カメラテスト"""
    try:
        image = controller.system.hardware_controller.capture_image()
        return {
            "capture_success": image is not None,
            "image_shape": image.shape if image is not None else None,
            "status": "OK" if image is not None else "NG"
        }
    except Exception as e:
        return {
            "capture_success": False,
            "error": str(e),
            "status": "NG"
        }


def _test_detection(controller: CLIController) -> Dict[str, Any]:
    """検出テスト"""
    try:
        result = controller.system.run_single_detection()
        return {
            "detection_success": result.get('success', False),
            "processing_time_ms": result.get('processing_time_ms', 0),
            "status": "OK" if result.get('success', False) else "NG"
        }
    except Exception as e:
        return {
            "detection_success": False,
            "error": str(e),
            "status": "NG"
        }


def _display_diagnosis_results(results: Dict[str, Dict[str, Any]]):
    """診断結果表示"""
    table = Table(title="システム診断結果", box=box.ROUNDED)
    table.add_column("診断項目", style="cyan")
    table.add_column("状態", justify="center")
    table.add_column("詳細", style="yellow")
    
    for check_name, result in results.items():
        status = result.get('status', 'UNKNOWN')
        status_icon = {
            'OK': '[green]✓[/green]',
            'NG': '[red]✗[/red]',
            'WARNING': '[yellow]⚠[/yellow]',
            'UNKNOWN': '[grey]?[/grey]'
        }.get(status, '[grey]?[/grey]')
        
        # 詳細情報
        details = []
        for k, v in result.items():
            if k != 'status':
                details.append(f"{k}: {v}")
        
        table.add_row(
            check_name,
            status_icon,
            '\n'.join(details[:3])  # 最初の3項目のみ表示
        )
    
    console.print(table)
    
    # サマリー
    ok_count = sum(1 for r in results.values() if r.get('status') == 'OK')
    total_count = len(results)
    
    if ok_count == total_count:
        console.print("\n[green]✓ すべての診断項目が正常です[/green]")
    else:
        console.print(f"\n[yellow]⚠ {total_count}項目中{ok_count}項目が正常です[/yellow]")


@cli.command()
@click.option('--dry-run', is_flag=True, help='実際の削除は行わない')
@click.option('--older-than', type=int, default=30,
              help='指定日数より古いデータを削除')
@click.pass_obj
def cleanup(controller: CLIController, dry_run, older_than):
    """古いデータをクリーンアップ"""
    console.print(f"[blue]{older_than}日より古いデータをクリーンアップ中...[/blue]")
    
    # 対象ディレクトリ
    cleanup_dirs = [
        Path("./logs"),
        Path("./output"),
        Path("./data/detections"),
        Path("./data/processed")
    ]
    
    cutoff_date = datetime.now() - timedelta(days=older_than)
    files_to_delete = []
    total_size = 0
    
    # ファイル検索
    with console.status("ファイルを検索中..."):
        for dir_path in cleanup_dirs:
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        files_to_delete.append(file_path)
                        total_size += file_path.stat().st_size
    
    if not files_to_delete:
        console.print("[green]削除対象のファイルはありません[/green]")
        return
    
    # 確認表示
    console.print(f"\n削除対象: {len(files_to_delete)}ファイル")
    console.print(f"合計サイズ: {total_size / (1024**2):.1f} MB")
    
    if dry_run:
        console.print("\n[yellow]--dry-run モード: 実際の削除は行いません[/yellow]")
        # ファイルリスト表示（最初の10件）
        for file_path in files_to_delete[:10]:
            console.print(f"  - {file_path}")
        if len(files_to_delete) > 10:
            console.print(f"  ... 他 {len(files_to_delete) - 10} ファイル")
    else:
        # 確認プロンプト
        if not Confirm.ask("\n本当に削除しますか？"):
            console.print("[yellow]キャンセルされました[/yellow]")
            return
        
        # 削除実行
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("削除中...", total=len(files_to_delete))
            
            deleted_count = 0
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    console.print(f"[red]削除エラー: {file_path} - {e}[/red]")
                progress.update(task, advance=1)
        
        console.print(f"[green]✓ {deleted_count}ファイルを削除しました[/green]")


@cli.command()
@click.pass_obj
def interactive(controller: CLIController):
    """対話モードを開始"""
    console.print(Panel.fit(
        "🐛 昆虫観察システム - 対話モード\n"
        "helpでコマンド一覧を表示",
        title="対話モード",
        border_style="green"
    ))
    
    if not controller.initialize_system():
        console.print("[red]システム初期化に失敗しました[/red]")
        return
    
    # コマンドマップ
    commands = {
        'help': _show_interactive_help,
        'status': lambda: _display_status_table(controller.system.get_system_status()),
        'detect': lambda: _interactive_detect(controller),
        'analyze': lambda: _interactive_analyze(controller),
        'config': lambda: _show_config(controller),
        'exit': lambda: None,
        'quit': lambda: None,
    }
    
    try:
        while True:
            # プロンプト
            command = Prompt.ask("\n[cyan]insect-observer[/cyan]").strip().lower()
            
            if command in ['exit', 'quit']:
                break
            
            if command in commands:
                result = commands[command]()
                if result is False:
                    break
            else:
                console.print(f"[red]不明なコマンド: {command}[/red]")
                console.print("helpでコマンド一覧を表示")
                
    except KeyboardInterrupt:
        console.print("\n[yellow]対話モードを終了します[/yellow]")
    finally:
        controller.cleanup()


def _show_interactive_help():
    """対話モードヘルプ表示"""
    help_text = """
[bold cyan]利用可能なコマンド:[/bold cyan]

  help     - このヘルプを表示
  status   - システム状態を表示
  detect   - 単発検出を実行
  analyze  - データ分析を実行
  config   - 現在の設定を表示
  exit     - 対話モードを終了
  quit     - 対話モードを終了
    """
    console.print(help_text)


def _interactive_detect(controller: CLIController):
    """対話的検出実行"""
    save_image = Confirm.ask("検出画像を保存しますか？", default=False)
    
    with console.status("検出中..."):
        result = controller.system.run_single_detection()
    
    if "error" in result:
        console.print(f"[red]エラー: {result['error']}[/red]")
    else:
        console.print(f"[green]✓ 検出完了: {result.get('detection_count', 0)}匹検出[/green]")


def _interactive_analyze(controller: CLIController):
    """対話的分析実行"""
    date_str = Prompt.ask(
        "分析対象日付 (YYYY-MM-DD)",
        default=(datetime.now() - timedelta(days=1)).date().isoformat()
    )
    
    with console.status(f"{date_str} を分析中..."):
        success = controller.system.run_analysis_for_date(date_str)
    
    if success:
        console.print(f"[green]✓ 分析完了[/green]")
    else:
        console.print(f"[red]✗ 分析失敗[/red]")


def _show_config(controller: CLIController):
    """設定表示"""
    config_data = controller.system.config_manager.get_all_settings()
    
    # JSON表示
    json_str = json.dumps(config_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="現在の設定", border_style="blue"))


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--validate-only', is_flag=True, help='検証のみ実行')
@click.pass_obj
def config(controller: CLIController, config_file, validate_only):
    """設定ファイルの検証・適用"""
    console.print(f"[blue]設定ファイルを検証中: {config_file}[/blue]")
    
    try:
        # 設定読み込み
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 必須フィールドチェック
        required_fields = ['system', 'hardware', 'detection', 'analysis']
        missing = [f for f in required_fields if f not in config_data]
        
        if missing:
            console.print(f"[red]必須フィールドが不足: {', '.join(missing)}[/red]")
            return
        
        console.print("[green]✓ 設定ファイルは有効です[/green]")
        
        if not validate_only:
            # 設定適用
            if Confirm.ask("この設定を適用しますか？"):
                import shutil
                shutil.copy2(config_file, controller.config_path)
                console.print("[green]✓ 設定を適用しました[/green]")
        
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON解析エラー: {e}[/red]")
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")


if __name__ == '__main__':
    cli()