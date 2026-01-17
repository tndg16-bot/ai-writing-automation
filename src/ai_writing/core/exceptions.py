"""カスタム例外"""

from typing import Optional


class AIWritingError(Exception):
    """AI Writing Automation 基底例外"""

    def __init__(self, message: str, suggestions: Optional[list[str]] = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(self._get_full_message())

    def _get_full_message(self) -> str:
        """エラーメッセージと提案を結合"""
        full_msg = self.message
        if self.suggestions:
            full_msg += "\n\n[bold yellow]💡 解決策:[/bold yellow]\n"
            for i, suggestion in enumerate(self.suggestions, 1):
                full_msg += f"  {i}. {suggestion}\n"
        return full_msg


class ConfigurationError(AIWritingError):
    """設定エラー"""

    def __init__(
        self, message: str, file_path: Optional[str] = None, suggestions: Optional[list[str]] = None
    ):
        full_message = f"設定エラー: {message}"
        if file_path:
            full_message += f"\nファイル: {file_path}"

        if suggestions is None:
            suggestions = [
                "設定ファイルのパスを確認してください",
                "YAMLファイルのインデントを確認してください",
                "必要な環境変数が設定されているか確認してください",
            ]

        super().__init__(full_message, suggestions)


class LLMError(AIWritingError):
    """LLM API関連エラー"""

    def __init__(
        self, message: str, provider: Optional[str] = None, suggestions: Optional[list[str]] = None
    ):
        full_message = f"LLM API エラー: {message}"
        if provider:
            full_message += f"\nプロバイダー: {provider}"

        if suggestions is None:
            suggestions = [
                "APIキーが正しく設定されているか確認してください",
                "インターネット接続を確認してください",
                "APIの利用制限（レート制限）に達していないか確認してください",
                "APIキーの権限設定を確認してください",
            ]

        super().__init__(full_message, suggestions)


class LLMRateLimitError(LLMError):
    """レート制限エラー"""

    def __init__(self, provider: Optional[str] = None):
        message = "APIのレート制限を超えました"
        suggestions = [
            "少し待ってから再試行してください（数分〜数時間）",
            "APIの使用量プランを確認してください",
            "複数のリクエストを並列に送信しないようにしてください",
        ]
        super().__init__(message, provider, suggestions)


class LLMResponseError(LLMError):
    """レスポンスパースエラー"""

    def __init__(self, message: str, raw_response: Optional[str] = None):
        full_message = f"LLMレスポンスの解析に失敗しました: {message}"
        if raw_response:
            full_message += f"\n生のレスポンス（最初の200文字）: {raw_response[:200]}..."

        suggestions = [
            "プロンプトを見直して、より明確な指示を与えてください",
            "AIモデルを変更してみてください（GPT-3.5 → GPT-4など）",
            "プロンプトテンプレートを確認してください",
        ]
        super().__init__(full_message, None, suggestions)


class ImageGenerationError(AIWritingError):
    """画像生成エラー"""

    def __init__(
        self, message: str, provider: Optional[str] = None, suggestions: Optional[list[str]] = None
    ):
        full_message = f"画像生成エラー: {message}"
        if provider:
            full_message += f"\nプロバイダー: {provider}"

        if suggestions is None:
            suggestions = [
                "画像生成APIキーが正しく設定されているか確認してください",
                "プロンプトが適切か確認してください（NSFWコンテンツを含んでいないか）",
                "APIの使用制限を確認してください",
            ]

        super().__init__(full_message, suggestions)


class GoogleDocsError(AIWritingError):
    """Google Docs操作エラー"""

    def __init__(self, message: str, suggestions: Optional[list[str]] = None):
        if suggestions is None:
            suggestions = [
                "Google API認証を確認してください",
                "APIキーのGoogle Docs API権限を有効にしてください",
                "認証ファイルのパスを確認してください",
                "Googleアカウントへのアクセス権限を確認してください",
            ]
        super().__init__(f"Google Docs エラー: {message}", suggestions)


class TemplateError(AIWritingError):
    """テンプレートエラー"""

    def __init__(
        self,
        message: str,
        template_path: Optional[str] = None,
        suggestions: Optional[list[str]] = None,
    ):
        full_message = f"テンプレートエラー: {message}"
        if template_path:
            full_message += f"\nテンプレート: {template_path}"

        if suggestions is None:
            suggestions = [
                "テンプレートファイルのパスを確認してください",
                "Jinja2テンプレートの構文を確認してください",
                "テンプレートに必要な変数が含まれているか確認してください",
            ]

        super().__init__(full_message, suggestions)


class PipelineError(AIWritingError):
    """パイプライン実行エラー"""

    def __init__(
        self, message: str, stage: Optional[str] = None, suggestions: Optional[list[str]] = None
    ):
        full_message = f"パイプライン実行エラー: {message}"
        if stage:
            full_message += f"\n失敗したステージ: {stage}"

        if suggestions is None:
            suggestions = [
                "設定ファイルを確認してください",
                "ネットワーク接続を確認してください",
                "ログを確認して詳細なエラーメッセージを確認してください",
                "ドライランモード（--dry-run）で設定を確認してください",
            ]

        super().__init__(full_message, suggestions)


class StageError(AIWritingError):
    """ステージ実行エラー"""

    def __init__(self, message: str, stage: str, suggestions: Optional[list[str]] = None):
        if suggestions is None:
            suggestions = [
                f"{stage} ステージの設定を確認してください",
                "キーワードが適切か確認してください",
                "プロンプトテンプレートを確認してください",
            ]
        super().__init__(f"{stage} エラー: {message}", suggestions)
