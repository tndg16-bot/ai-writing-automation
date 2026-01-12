"""Google Docs document renderer"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol


from ai_writing.core.exceptions import TemplateError
from ai_writing.templates.engine import TemplateEngine


class GoogleDocsServiceProtocol(Protocol):
    """Protocol for Google Docs service"""

    def create_document(self, title: str) -> str:
        """Create a new document and return document ID"""
        ...

    def get_document_url(self, document_id: str) -> str:
        """Get the URL for a document"""
        ...

    def insert_text(self, doc_id: str, text: str, index: int) -> dict[str, Any]:
        """Insert text at index, return batch update response"""
        ...

    def apply_heading_style(
        self, doc_id: str, start: int, end: int, level: int
    ) -> dict[str, Any]:
        """Apply heading style to text range"""
        ...

    def insert_image(
        self,
        doc_id: str,
        image_path: Path,
        index: int,
        width: int,
        height: int,
    ) -> dict[str, Any]:
        """Insert image at index, return batch update response"""
        ...


if TYPE_CHECKING:
    from ai_writing.services.google.docs import GoogleDocsService


class DocumentRenderer:
    """Renders GenerationContext to Google Docs"""

    def __init__(
        self,
        template_engine: TemplateEngine,
        docs_service: "GoogleDocsService | GoogleDocsServiceProtocol",
    ):
        """Initialize document renderer

        Args:
            template_engine: Jinja2 template engine
            docs_service: Google Docs service for document operations
        """
        self.template_engine = template_engine
        self.docs_service = docs_service

    def render_to_docs(
        self, context: dict[str, Any], template_name: str = "blog_default.json"
    ) -> str:
        """Render context to Google Docs

        1. Load and render template with context
        2. Parse JSON template config
        3. Create document
        4. Apply sections from template
        5. Return document URL

        Args:
            context: Context data for rendering
            template_name: Name of template file

        Returns:
            URL of created Google Docs document

        Raises:
            TemplateError: If template loading or rendering fails
        """
        # 1. Load and render template with context
        try:
            rendered_template = self.template_engine.render_template(
                template_name, context
            )
        except Exception as e:
            raise TemplateError(f"Failed to render template {template_name}: {e}") from e

        # 2. Parse JSON template config
        try:
            template_config = json.loads(rendered_template)
        except json.JSONDecodeError as e:
            raise TemplateError(f"Invalid JSON in template {template_name}: {e}") from e

        # 3. Create document
        title = self._resolve_variable(
            template_config.get("title", "Untitled Document"), context
        )
        doc_id = self.docs_service.create_document(title)

        # 4. Apply sections from template
        sections = template_config.get("sections", [])
        index = 1  # Start after the title
        for section in sections:
            index = self._render_section(doc_id, section, index, context)

        # 5. Return document URL
        return self.docs_service.get_document_url(doc_id)

    def _render_section(
        self, doc_id: str, section: dict[str, Any], index: int, context: dict[str, Any]
    ) -> int:
        """Render a single section, return new index

        Section types:
        - heading: Insert heading with style
        - paragraph: Insert text
        - image: Insert image (if path exists)
        - loop: Iterate over items

        Args:
            doc_id: Document ID
            section: Section configuration
            index: Current insertion index
            context: Context data for variable resolution

        Returns:
            New index after section insertion
        """
        section_type = section.get("type", "paragraph")

        if section_type == "heading":
            text = self._resolve_variable(section.get("text", ""), context)
            level = section.get("level", 1)
            return self._insert_heading(doc_id, text, level, index)

        elif section_type == "paragraph":
            text = self._resolve_variable(section.get("text", ""), context)
            return self._insert_text(doc_id, text, index)

        elif section_type == "image":
            # Check condition if present
            condition = section.get("condition", "")
            if condition:
                resolved_condition = self._resolve_variable(condition, context)
                if not resolved_condition or resolved_condition == "None":
                    return index

            image_path = self._resolve_variable(section.get("path", ""), context)
            if not image_path or image_path == "None":
                return index

            width = section.get("width", 400)
            height = section.get("height", 300)
            return self._insert_image(doc_id, image_path, width, height, index)

        elif section_type == "loop":
            variable = section.get("variable", "")
            item_name = section.get("item_name", "item")
            inner_sections = section.get("sections", [])

            # Resolve the variable to get the iterable
            items = self._get_nested_value(context, variable)
            if not items or not isinstance(items, list):
                return index

            # Iterate over items
            for item in items:
                # Create new context with loop item
                loop_context = context.copy()
                loop_context[item_name] = item

                # Render inner sections
                for inner_section in inner_sections:
                    index = self._render_section(
                        doc_id, inner_section, index, loop_context
                    )

            return index

        else:
            # Unknown section type, skip
            return index

    def _insert_text(self, doc_id: str, text: str, index: int) -> int:
        """Insert text and return new index

        Args:
            doc_id: Document ID
            text: Text to insert
            index: Current index

        Returns:
            New index after insertion
        """
        if not text:
            return index

        self.docs_service.insert_text(doc_id, text, index)
        return index + len(text)

    def _insert_heading(self, doc_id: str, text: str, level: int, index: int) -> int:
        """Insert heading with style and return new index

        Args:
            doc_id: Document ID
            text: Heading text
            level: Heading level (1-6)
            index: Current index

        Returns:
            New index after insertion
        """
        if not text:
            return index

        # Insert text with newline
        full_text = text + "\n"
        self.docs_service.insert_text(doc_id, full_text, index)

        # Apply heading style
        start_index = index
        end_index = index + len(text)
        self.docs_service.apply_heading_style(doc_id, start_index, end_index, level)

        return index + len(full_text)

    def _insert_image(
        self, doc_id: str, image_path: str, width: int, height: int, index: int
    ) -> int:
        """Insert image and return new index

        Args:
            doc_id: Document ID
            image_path: Path to image file
            width: Image width
            height: Image height
            index: Current index

        Returns:
            New index after insertion
        """
        path = Path(image_path)
        if not path.exists():
            return index

        self.docs_service.insert_image(doc_id, path, index, width, height)
        # Image typically takes 1 index position
        return index + 1

    def _resolve_variable(self, value: str, context: dict[str, Any]) -> str:
        """Resolve {{variable}} placeholders in value

        Args:
            value: String potentially containing Jinja2 variables
            context: Context data for variable resolution

        Returns:
            Resolved string with variables replaced
        """
        if not isinstance(value, str):
            return str(value) if value is not None else ""

        if "{{" in value and "}}" in value:
            try:
                return self.template_engine.render_string(value, context)
            except Exception:
                return value
        return value

    def _get_nested_value(self, context: dict[str, Any], key: str) -> Any:
        """Get nested value from context using dot notation

        Args:
            context: Context dictionary
            key: Dot-separated key (e.g., "section.subsections")

        Returns:
            Value at nested key, or None if not found
        """
        parts = key.split(".")
        value: Any = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

            if value is None:
                return None

        return value
