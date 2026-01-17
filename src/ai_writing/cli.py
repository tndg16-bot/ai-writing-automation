"""CLI エントリーポイント"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.markdown import Markdown

app = typer.Typer(
    name="ai-writing",
    help="AIライティング自動化ツール - キーワードからGoogle Docs完成稿まで",
)
console = Console()


def _print_success(message: str) -> None:
    """成功メッセージを表示"""
    console.print(f"[green][OK][/green] {message}")


def _print_error(message: str) -> None:
    """エラーメッセージを表示"""
    console.print(f"[red][X][/red] {message}")


def _print_info(message: str) -> None:
    """情報メッセージを表示"""
    console.print(f"[blue][i][/blue] {message}")


def _print_warning(message: str) -> None:
    """警告メッセージを表示"""
    console.print(f"[yellow][!][/yellow] {message}")


def _generate_markdown(context) -> str:
    """コンテキストからMarkdownを生成"""
    lines = []

    # タイトル
    if context.selected_title:
        lines.append(f"# {context.selected_title}")
        lines.append("")

    # リード文
    if context.lead:
        lines.append(context.lead)
        lines.append("")

    # セクション
    for section in context.sections:
        lines.append(f"## {section.heading}")
        lines.append("")
        lines.append(section.content)
        lines.append("")

    # まとめ
    if context.summary:
        lines.append("## まとめ")
        lines.append("")
        lines.append(context.summary)

    return "\n".join(lines)


def _print_generation_summary(context) -> None:
    """生成結果のサマリーを表示"""
    table = Table(
        title="[bold green]生成結果サマリー[/bold green]",
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("項目", style="cyan", width=20)
    table.add_column("値", style="white")

    table.add_row("キーワード", context.keyword)
    table.add_row("コンテンツタイプ", context.content_type)

    if context.selected_title:
        table.add_row(
            "タイトル",
            context.selected_title[:50] + "..."
            if len(context.selected_title) > 50
            else context.selected_title,
        )

    if context.sections:
        table.add_row("セクション数", str(len(context.sections)))

    if context.images:
        table.add_row("画像数", str(len(context.images)))

    if "docs_url" in context.client_config:
        table.add_row(
            "Google Docs URL",
            context.client_config["docs_url"][:50] + "..."
            if len(context.client_config["docs_url"]) > 50
            else context.client_config["docs_url"],
        )

    console.print(table)


def _complete_content_type() -> list[str]:
    """コンテンツタイプの補完候補"""
    return ["blog", "youtube", "yukkuri"]


def _complete_client() -> list[str]:
    """クライアント設定の補完候補"""
    config_dir = Path("config/clients")
    if config_dir.exists():
        return ["default"] + [f.stem for f in config_dir.glob("*.yaml")]
    return ["default"]


@app.command()
def generate(
    keyword: str = typer.Argument(..., help="メインキーワード", metavar="KEYWORD"),
    content_type: str = typer.Option(
        "blog",
        "--content-type",
        "-t",
        help="コンテンツタイプ (blog | youtube | yukkuri)",
        show_default=True,
        autocompletion=_complete_content_type,
    ),
    client: str = typer.Option(
        "default",
        "--client",
        "-c",
        help="クライアント設定名",
        show_default=True,
        autocompletion=_complete_client,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="ローカル出力先（指定なしでGoogle Docs）",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="実行せずに設定を確認",
        is_flag=True,
    ),
):
    """AIライティングを実行してコンテンツを生成"""
    console.print(
        Panel(
            f"[bold blue]AI Writing Automation[/bold blue]\n[dim]キーワードからGoogle Docs完成稿までを自動生成[/dim]",
            border_style="blue",
        )
    )
    console.print()
    console.print(f"[bold]入力情報:[/bold]")
    console.print(f"  キーワード: [green]{keyword}[/green]")
    console.print(f"  コンテンツタイプ: [cyan]{content_type}[/cyan]")
    console.print(f"  クライアント: [yellow]{client}[/yellow]")
    if output:
        console.print(f"  出力先: [magenta]{output}[/magenta]")

    if dry_run:
        console.print()
        _print_warning("ドライランモード: 設定確認のみで実行はスキップします")
        console.print()
        return

    try:
        # 設定を読み込み
        from ai_writing.core.config import Config, EnvSettings
        from ai_writing.pipeline.blog import BlogPipeline
        from ai_writing.pipeline.youtube import YouTubePipeline
        from ai_writing.pipeline.yukkuri import YukkuriPipeline

        config = Config.load("config/config.yaml")

        # クライアント設定をマージ
        if client != "default":
            client_config_path = Path("config/clients") / f"{client}.yaml"
            config = Config.load_with_client("config/config.yaml", client_config_path)

        # パイプライン初期化
        if content_type == "blog":
            pipeline = BlogPipeline(config)
        elif content_type == "youtube":
            pipeline = YouTubePipeline(config)
        elif content_type == "yukkuri":
            pipeline = YukkuriPipeline(config)
        else:
            _print_error(f"未対応のコンテンツタイプ: {content_type}")
            console.print()
            _print_info("使用可能なコンテンツタイプ: blog, youtube, yukkuri")
            raise typer.Exit(1)

        # パイプライン実行
        console.print()
        console.print(Panel("[bold cyan]パイプライン実行中...[/bold cyan]", border_style="cyan"))
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            # プログレスバーを初期化
            stage_count = len(pipeline.stages)
            task = progress.add_task(
                f"[cyan]コンテンツ生成中... ({stage_count} ステージ)", total=stage_count
            )

            # パイプライン実行（コールバック付き）
            def update_progress(advance: int = 1, description: str | None = None):
                progress.update(task, advance=advance, description=description)

            context = asyncio.run(pipeline.run(keyword, progress_callback=update_progress))
            # 完了
            progress.update(task, completed=stage_count)
            progress.console.print("[green][OK][/green] すべてのステージが完了しました")

        # 生成結果サマリー表示
        console.print()
        _print_generation_summary(context)

        # Markdown出力生成
        markdown = _generate_markdown(context)

        # 結果を保存または表示
        console.print()
        if output:
            output.write_text(markdown, encoding="utf-8")
            console.print(f"  [green][OK][/green] 出力を保存しました: {output}")
        else:
            console.print("[bold]生成結果（プレビュー）:[/bold]")
            # Markdownの最初の500文字をプレビュー
            preview = markdown[:500] + "..." if len(markdown) > 500 else markdown
            console.print(Panel(Markdown(preview), title="Markdown Preview", border_style="green"))

        # Google Docs URL を表示（生成された場合）
        if "docs_url" in context.client_config:
            console.print()
            console.print(f"  [green][OK][/green] Google Docs: {context.client_config['docs_url']}")

    except Exception as e:
        console.print()
        _print_error(str(e))
        raise typer.Exit(1)


@app.command("list")
def list_clients():
    """利用可能なクライアント設定を一覧"""
    config_dir = Path("config/clients")
    if not config_dir.exists():
        _print_warning("クライアント設定ディレクトリが見つかりません")
        return

    clients = list(config_dir.glob("*.yaml"))
    if not clients:
        _print_info("クライアント設定がありません")
        return

    console.print()
    console.print("[bold cyan]利用可能なクライアント設定:[/bold cyan]")
    console.print()
    for f in clients:
        console.print(f"  - [green]{f.stem}[/green]")

    console.print()
    _print_info("デフォルト設定を使用するには: ai-writing generate KEYWORD --client default")


@app.command("validate")
def validate():
    """設定ファイルと環境変数を検証"""
    console.print()
    console.print(Panel("[bold cyan]設定検証中...[/bold cyan]", border_style="cyan"))
    console.print()

    # 環境変数チェック
    console.print("[bold]環境変数:[/bold]")
    try:
        from ai_writing.core.config import EnvSettings

        env = EnvSettings()

        if env.openai_api_key:
            masked_key = env.openai_api_key[:8] + "..." + env.openai_api_key[-4:]
            console.print(f"  [green][OK][/green] OPENAI_API_KEY が設定されています ({masked_key})")
        else:
            console.print("  [red][X][/red] OPENAI_API_KEY が未設定です")
            _print_warning("  環境変数 OPENAI_API_KEY を設定してください")

        if env.google_api_key:
            masked_key = env.google_api_key[:8] + "..." + env.google_api_key[-4:]
            console.print(f"  [green][OK][/green] GOOGLE_API_KEY が設定されています ({masked_key})")
        else:
            console.print("  [yellow][o][/yellow] GOOGLE_API_KEY が未設定です（オプション）")
    except Exception as e:
        console.print(f"  [red][X][/red] 環境変数エラー: {e}")

    # 設定ファイルチェック
    console.print()
    console.print("[bold]設定ファイル:[/bold]")
    from ai_writing.core.config import Config

    config_path = Path("config/config.yaml")
    if config_path.exists():
        try:
            config = Config.load(config_path)
            console.print("  [green][OK][/green] config.yaml を読み込みました")
            console.print(f"    LLM プロバイダー: [cyan]{config.llm.provider}[/cyan]")
            console.print(f"    LLM モデル: [cyan]{config.llm.model}[/cyan]")
        except Exception as e:
            console.print(f"  [red][X][/red] config.yaml エラー: {e}")
    else:
        console.print("  [yellow][o][/yellow] config.yaml が見つかりません（デフォルト設定を使用）")

    # クライアント設定チェック
    console.print()
    console.print("[bold]クライアント設定:[/bold]")
    client_dir = Path("config/clients")
    if client_dir.exists():
        clients = list(client_dir.glob("*.yaml"))
        if clients:
            console.print(
                f"  [green][OK][/green] {len(clients)} 件のクライアント設定が見つかりました"
            )
            for f in clients:
                console.print(f"    - [green]{f.stem}[/green]")
        else:
            _print_info("クライアント設定がありません")
    else:
        _print_info("クライアント設定ディレクトリが見つかりません")

    console.print()
    _print_success("設定検証が完了しました")


@app.command("history")
def history(
    keyword: str = typer.Option(None, "--keyword", "-k", help="キーワードで検索"),
    content_type: str = typer.Option(None, "--type", "-t", help="コンテンツタイプでフィルタリング"),
    limit: int = typer.Option(50, "--limit", "-l", help="表示する件数"),
    offset: int = typer.Option(0, "--offset", help="オフセット"),
):
    """履歴管理コマンド"""
    if keyword is None and content_type is None:
        # 履歴一覧を表示
        _history_list(limit, offset)
    else:
        # 検索
        _history_search(keyword, content_type, limit, offset)


@app.command("perf")
def perf(
    report: bool = typer.Option(
        False, "--report", "-r", is_flag=True, help="パフォーマンスレポートを表示"
    ),
    clear: bool = typer.Option(
        False, "--clear", "-c", is_flag=True, help="パフォーマンスデータをクリア"
    ),
):
    """パフォーマンス監視コマンド"""
    if report:
        _perf_report()
    if clear:
        _perf_clear()


@app.command("version")
def version():
    """バージョン情報を表示"""
    import sys
    from ai_writing import __version__

    console.print()
    console.print(
        Panel(
            f"[bold blue]AI Writing Automation[/bold blue]\n[dim]バージョン: {__version__}[/dim]",
            border_style="blue",
        )
    )
    console.print()
    console.print(f"Python: [cyan]{sys.version.split()[0]}[/cyan]")
    console.print()
    _print_info("詳細な情報: https://github.com/tndg16-bot/ai-writing-automation")


def _history_list(limit: int, offset: int) -> None:
    """履歴一覧を表示"""
    from ai_writing.core.history_manager import HistoryManager

    manager = HistoryManager()
    generations = manager.list_generations(limit=limit, offset=offset)

    if not generations:
        console.print("[yellow][!][/yellow] 履歴がありません")
        return

    # テーブルを作成
    table = Table(
        title="[bold cyan]生成履歴[/bold cyan]",
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("ID", style="cyan", width=8)
    table.add_column("キーワード", style="white")
    table.add_column("タイプ", style="green")
    table.add_column("タイトル", style="yellow")
    table.add_column("作成日", style="dim")

    for gen in generations:
        title = (
            gen.get("title", "N/A")[:30] + "..."
            if len(gen.get("title", "")) > 30
            else gen.get("title", "N/A")
        )
        created_at = gen["created_at"].split("T")[0] if gen.get("created_at") else "N/A"

        table.add_row(
            str(gen["id"]),
            gen["keyword"][:20] + "..." if len(gen["keyword"]) > 20 else gen["keyword"],
            gen["content_type"],
            title,
            created_at,
        )

    console.print()
    console.print(table)
    console.print()
    _print_info(f"合計 {len(generations)} 件の履歴を表示しました")


def _history_search(
    keyword: str | None,
    content_type: str | None,
    limit: int,
    offset: int,
) -> None:
    """履歴を検索"""
    from ai_writing.core.history_manager import HistoryManager

    manager = HistoryManager()
    generations = manager.list_generations(
        keyword=keyword,
        content_type=content_type,
        limit=limit,
        offset=offset,
    )

    if not generations:
        console.print("[yellow][!][/yellow] 該当する履歴がありません")
        return

    # 検索条件を表示
    console.print()
    if keyword:
        console.print(f'[dim]キーワード: "{keyword}"[/dim]')
    if content_type:
        console.print(f"[dim]タイプ: {content_type}[/dim]")
    console.print()

    # テーブルを作成
    table = Table(
        title="[bold cyan]検索結果[/bold cyan]",
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("ID", style="cyan", width=8)
    table.add_column("キーワード", style="white")
    table.add_column("タイプ", style="green")
    table.add_column("タイトル", style="yellow")
    table.add_column("作成日", style="dim")

    for gen in generations:
        title = (
            gen.get("title", "N/A")[:30] + "..."
            if len(gen.get("title", "")) > 30
            else gen.get("title", "N/A")
        )
        created_at = gen["created_at"].split("T")[0] if gen.get("created_at") else "N/A"

        table.add_row(
            str(gen["id"]),
            gen["keyword"][:20] + "..." if len(gen["keyword"]) > 20 else gen["keyword"],
            gen["content_type"],
            title,
            created_at,
        )

    console.print(table)
    console.print()
    _print_info(f"合計 {len(generations)} 件の履歴が見つかりました")


def _perf_report() -> None:
    """パフォーマンスレポートを表示"""
    from ai_writing.services.llm.cache import LLMCache
    from ai_writing.services.image.cache import ImageCache

    console.print()
    console.print(Panel("[bold cyan]パフォーマンスレポート[/bold cyan]", border_style="cyan"))
    console.print()

    # LLMキャッシュ統計
    llm_cache = LLMCache()
    llm_stats = llm_cache.get_stats()

    console.print("[bold]LLM キャッシュ統計:[/bold]")
    console.print(f"  ヒット数: [green]{llm_stats['hits']}[/green]")
    console.print(f"  ミス数: [red]{llm_stats['misses']}[/red]")
    console.print(f"  ヒット率: [cyan]{llm_stats['hit_rate']:.2%}[/cyan]")
    console.print(f"  キャッシュサイズ: {llm_stats['cache_volume']:,} bytes")
    console.print()

    # 画像キャッシュ統計
    image_cache = ImageCache()
    image_stats = image_cache.get_stats()

    console.print("[bold]画像キャッシュ統計:[/bold]")
    console.print(f"  エントリ数: {image_stats['size']}")
    console.print(f"  サイズ: {image_stats['volume']:,} bytes")
    console.print(f"  ディレクトリ: {image_stats['directory']}")
    console.print()

    # プロバイダー別統計
    if image_stats.get("by_provider"):
        console.print("[bold]プロバイダー別:[/bold]")
        for provider, count in image_stats["by_provider"].items():
            console.print(f"  {provider}: {count} 枚")
        console.print()


def _perf_clear() -> None:
    """パフォーマンスデータをクリア"""
    from ai_writing.services.llm.cache import LLMCache
    from ai_writing.services.image.cache import ImageCache

    console.print()
    _print_warning("パフォーマンスデータ（キャッシュ）をクリアします...")

    llm_cache = LLMCache()
    llm_cache.clear()

    image_cache = ImageCache()
    image_cache.clear()

    console.print()
    _print_success("パフォーマンスデータをクリアしました")


if __name__ == "__main__":
    app()
