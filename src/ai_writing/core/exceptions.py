"""カスタム例外"""


class AIWritingError(Exception):
    """AI Writing Automation 基底例外"""

    pass


class ConfigurationError(AIWritingError):
    """設定エラー"""

    pass


class LLMError(AIWritingError):
    """LLM API関連エラー"""

    pass


class LLMRateLimitError(LLMError):
    """レート制限エラー"""

    pass


class LLMResponseError(LLMError):
    """レスポンスパースエラー"""

    pass


class ImageGenerationError(AIWritingError):
    """画像生成エラー"""

    pass


class GoogleDocsError(AIWritingError):
    """Google Docs操作エラー"""

    pass


class TemplateError(AIWritingError):
    """テンプレートエラー"""

    pass


class PipelineError(AIWritingError):
    """パイプライン実行エラー"""

    pass
