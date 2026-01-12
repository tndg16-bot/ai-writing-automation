"""CLI エントリーポイント"""
import asyncio

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="ai-writing",
    help="AIライティング自動化ツール - キーワードからGoogle Docs完成稿まで",
)
console = Console()


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


@app.command()
def generate(
    keyword: str = typer.Argument(..., help="メインキーワード"),
    content_type: str = typer.Option(
        "blog",
        "--content-type", "-t",
        help="コンテンツタイプ: blog | youtube | yukkuri",
    ),
    client: str = typer.Option(
        "default",
        "--client", "-c",
        help="クライアント設定名",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="ローカル出力先（指定なしでGoogle Docs）",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="実行せずに設定を確認",
    ),
):
    """AIライティングを実行してコンテンツを生成"""
    console.print(Panel(f"[bold blue]AI Writing Automation[/bold blue]"))
    console.print(f"キーワード: [green]{keyword}[/green]")
    console.print(f"コンテンツタイプ: [cyan]{content_type}[/cyan]")
    console.print(f"クライアント: [yellow]{client}[/yellow]")

    if dry_run:
        console.print("\n[yellow]ドライラン: 実行をスキップしました[/yellow]")
        return

    try:
        # 設定を読み込み
        from ai_writing.core.config import Config, EnvSettings
        from ai_writing.pipeline.blog import BlogPipeline

        config = Config.load("config/config.yaml")

        # クライアント設定をマージ
        if client != "default":
            client_config_path = Path("config/clients") / f"{client}.yaml"
            config = Config.load_with_client("config/config.yaml", client_config_path)

        # パイプライン初期化
        if content_type == "blog":
            pipeline = BlogPipeline(config)
        else:
            console.print(f"\n[red]エラー: 未対応のコンテンツタイプ '{content_type}'[/red]")
            raise typer.Exit(1)

        # パイプライン実行
        console.print("\n[bold]パイプライン実行中...[/bold]")
        context = asyncio.run(pipeline.run(keyword))

        # Markdown出力生成
        markdown = _generate_markdown(context)

        # 結果を保存または表示
        if output:
            output.write_text(markdown, encoding="utf-8")
            console.print(f"\n[green]✓[/green] 出力を保存しました: {output}")
        else:
            console.print("\n[bold]生成結果:[/bold]")
            console.print(Panel(markdown, title="Markdown Output"))

        # Google Docs URL を表示（生成された場合）
        if "docs_url" in context.client_config:
            console.print(
                f"\n[blue]📄 Google Docs: {context.client_config['docs_url']}[/blue]"
            )

    except Exception as e:
        console.print(f"\n[red]エラー: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_clients():
    """利用可能なクライアント設定を一覧"""
    config_dir = Path("config/clients")
    if not config_dir.exists():
        console.print("[yellow]クライアント設定が見つかりません[/yellow]")
        return

    console.print("[bold]利用可能なクライアント:[/bold]")
    for f in config_dir.glob("*.yaml"):
        console.print(f"  - {f.stem}")


@app.command()
def validate():
    """設定ファイルを検証"""
    from ai_writing.core.config import Config, EnvSettings

    console.print("[bold]設定を検証中...[/bold]")

    # 環境変数チェック
    try:
        env = EnvSettings()
        if env.openai_api_key:
            console.print("  [green]✓[/green] OPENAI_API_KEY が設定されています")
        else:
            console.print("  [red]✗[/red] OPENAI_API_KEY が未設定です")

        if env.google_api_key:
            console.print("  [green]✓[/green] GOOGLE_API_KEY が設定されています")
        else:
            console.print("  [yellow]○[/yellow] GOOGLE_API_KEY が未設定です（オプション）")
    except Exception as e:
        console.print(f"  [red]✗[/red] 環境変数エラー: {e}")

    # 設定ファイルチェック
    config_path = Path("config/config.yaml")
    if config_path.exists():
        try:
            config = Config.load(config_path)
            console.print(f"  [green]✓[/green] config.yaml を読み込みました")
            console.print(f"    LLM: {config.llm.provider} / {config.llm.model}")
        except Exception as e:
            console.print(f"  [red]✗[/red] config.yaml エラー: {e}")
    else:
        console.print("  [yellow]○[/yellow] config.yaml が見つかりません（デフォルト設定を使用）")


@app.command()
def version():
    """バージョンを表示"""
    from ai_writing import __version__

    console.print(f"ai-writing-automation v{__version__}")


if __name__ == "__main__":
    app()
