"""Jinja2 template engine"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound, TemplateSyntaxError

from ai_writing.core.exceptions import TemplateError


class TemplateEngine:
    """Jinja2 template engine wrapper"""

    def __init__(self, templates_dir: Path):
        """Initialize template engine

        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir), autoescape=False)
        self._register_filters()

    def _register_filters(self) -> None:
        """Register custom Jinja2 filters"""

        def split_lines(text: str) -> list[str]:
            """Split text into lines"""
            return text.split("\n")

        def first_line(text: str) -> str:
            """Get first line of text"""
            return text.split("\n")[0]

        # Register filters
        self.env.filters["split_lines"] = split_lines
        self.env.filters["first_line"] = first_line

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render template with context

        Args:
            template_name: Name of template file
            context: Context data for rendering

        Returns:
            Rendered template string

        Raises:
            TemplateError: If template not found or rendering fails
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound as e:
            raise TemplateError(f"Template not found: {template_name}") from e
        except TemplateSyntaxError as e:
            raise TemplateError(f"Template syntax error in {template_name}: {e}") from e
        except Exception as e:
            raise TemplateError(f"Failed to render template {template_name}: {e}") from e

    def render_string(self, template_string: str, context: dict[str, Any]) -> str:
        """Render template from string

        Args:
            template_string: Template as string
            context: Context data for rendering

        Returns:
            Rendered string

        Raises:
            TemplateError: If rendering fails
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**context)
        except TemplateSyntaxError as e:
            raise TemplateError(f"Template syntax error: {e}") from e
        except Exception as e:
            raise TemplateError(f"Failed to render template string: {e}") from e

    def load_template(self, template_name: str) -> Template:
        """Load template without rendering

        Args:
            template_name: Name of template file

        Returns:
            Jinja2 Template object

        Raises:
            TemplateError: If template not found
        """
        try:
            return self.env.get_template(template_name)
        except TemplateNotFound as e:
            raise TemplateError(f"Template not found: {template_name}") from e
