"""Tests for DocumentRenderer"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ai_writing.templates.engine import TemplateEngine
from ai_writing.templates.renderer import DocumentRenderer
from ai_writing.core.exceptions import TemplateError


@pytest.fixture
def temp_templates_dir():
    """Create a temporary directory with test templates"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def template_engine(temp_templates_dir: Path) -> TemplateEngine:
    """Create a TemplateEngine with temporary templates directory"""
    return TemplateEngine(temp_templates_dir)


@pytest.fixture
def mock_docs_service() -> MagicMock:
    """Create a mock Google Docs service"""
    service = MagicMock()
    service.create_document.return_value = "test_doc_id"
    service.get_document_url.return_value = "https://docs.google.com/document/d/test_doc_id/edit"
    service.insert_text.return_value = {"replies": []}
    service.apply_heading_style.return_value = {"replies": []}
    service.insert_image.return_value = {"replies": []}
    return service


@pytest.fixture
def renderer(
    template_engine: TemplateEngine, mock_docs_service: MagicMock
) -> DocumentRenderer:
    """Create a DocumentRenderer with mocked dependencies"""
    return DocumentRenderer(template_engine, mock_docs_service)


class TestDocumentRendererInit:
    """Tests for DocumentRenderer initialization"""

    def test_init_stores_dependencies(
        self, template_engine: TemplateEngine, mock_docs_service: MagicMock
    ) -> None:
        """Test that initialization stores dependencies"""
        renderer = DocumentRenderer(template_engine, mock_docs_service)
        
        assert renderer.template_engine is template_engine
        assert renderer.docs_service is mock_docs_service


class TestRenderToDocs:
    """Tests for render_to_docs method"""

    def test_render_simple_template(
        self, temp_templates_dir: Path, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering a simple template to Google Docs"""
        # Create simple template
        template = {
            "title": "{{ title }}",
            "sections": [
                {"type": "paragraph", "text": "{{ content }}"}
            ]
        }
        template_file = temp_templates_dir / "simple.json"
        template_file.write_text(json.dumps(template))
        
        engine = TemplateEngine(temp_templates_dir)
        renderer = DocumentRenderer(engine, mock_docs_service)
        
        context = {"title": "Test Title", "content": "Test Content"}
        url = renderer.render_to_docs(context, "simple.json")
        
        assert url == "https://docs.google.com/document/d/test_doc_id/edit"
        mock_docs_service.create_document.assert_called_once_with("Test Title")

    def test_render_with_heading(
        self, temp_templates_dir: Path, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering template with heading"""
        template = {
            "title": "Test Doc",
            "sections": [
                {"type": "heading", "level": 1, "text": "Main Heading"}
            ]
        }
        template_file = temp_templates_dir / "heading.json"
        template_file.write_text(json.dumps(template))
        
        engine = TemplateEngine(temp_templates_dir)
        renderer = DocumentRenderer(engine, mock_docs_service)
        
        renderer.render_to_docs({}, "heading.json")
        
        # Verify heading was inserted
        mock_docs_service.insert_text.assert_called()
        mock_docs_service.apply_heading_style.assert_called_once()
        
        # Check heading level
        call_args = mock_docs_service.apply_heading_style.call_args
        assert call_args[0][3] == 1  # level argument

    def test_render_with_multiple_sections(
        self, temp_templates_dir: Path, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering template with multiple sections"""
        template = {
            "title": "Test Doc",
            "sections": [
                {"type": "heading", "level": 1, "text": "Title"},
                {"type": "paragraph", "text": "Intro text"},
                {"type": "heading", "level": 2, "text": "Section 1"},
                {"type": "paragraph", "text": "Section content"}
            ]
        }
        template_file = temp_templates_dir / "multi.json"
        template_file.write_text(json.dumps(template))
        
        engine = TemplateEngine(temp_templates_dir)
        renderer = DocumentRenderer(engine, mock_docs_service)
        
        renderer.render_to_docs({}, "multi.json")
        
        # Verify multiple insert_text calls
        assert mock_docs_service.insert_text.call_count >= 4
        # Verify heading styles applied
        assert mock_docs_service.apply_heading_style.call_count == 2

    def test_render_template_not_found(
        self, renderer: DocumentRenderer
    ) -> None:
        """Test that TemplateError is raised for missing template"""
        with pytest.raises(TemplateError):
            renderer.render_to_docs({}, "nonexistent.json")

    def test_render_invalid_json_template(
        self, temp_templates_dir: Path, mock_docs_service: MagicMock
    ) -> None:
        """Test that TemplateError is raised for invalid JSON"""
        # Create invalid JSON template
        template_file = temp_templates_dir / "invalid.json"
        template_file.write_text("not valid json {}")
        
        engine = TemplateEngine(temp_templates_dir)
        renderer = DocumentRenderer(engine, mock_docs_service)
        
        with pytest.raises(TemplateError) as exc_info:
            renderer.render_to_docs({}, "invalid.json")
        
        assert "Invalid JSON" in str(exc_info.value)


class TestRenderLoop:
    """Tests for loop section rendering"""

    def test_render_loop_sections(
        self, renderer: DocumentRenderer, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering loop sections by calling _render_section directly"""
        # Test loop rendering directly without Jinja2 template file
        loop_section = {
            "type": "loop",
            "variable": "items",
            "item_name": "item",
            "sections": [
                {"type": "paragraph", "text": "{{ item.name }}"}
            ]
        }
        
        context = {
            "items": [
                {"name": "Item 1"},
                {"name": "Item 2"},
                {"name": "Item 3"}
            ]
        }
        
        renderer._render_section("test_doc", loop_section, 1, context)
        
        # Verify insert_text was called for each item
        insert_calls = [
            call for call in mock_docs_service.insert_text.call_args_list
        ]
        texts_inserted = [call[0][1] for call in insert_calls]
        
        assert "Item 1" in texts_inserted
        assert "Item 2" in texts_inserted
        assert "Item 3" in texts_inserted

    def test_render_nested_loop(
        self, renderer: DocumentRenderer, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering nested loops by calling _render_section directly"""
        loop_section = {
            "type": "loop",
            "variable": "sections",
            "item_name": "section",
            "sections": [
                {"type": "heading", "level": 2, "text": "{{ section.heading }}"},
                {
                    "type": "loop",
                    "variable": "section.items",
                    "item_name": "item",
                    "sections": [
                        {"type": "paragraph", "text": "- {{ item }}"}
                    ]
                }
            ]
        }
        
        context = {
            "sections": [
                {"heading": "Section A", "items": ["a1", "a2"]},
                {"heading": "Section B", "items": ["b1"]}
            ]
        }
        
        renderer._render_section("test_doc", loop_section, 1, context)
        
        # Verify headings were inserted (2 sections)
        assert mock_docs_service.apply_heading_style.call_count == 2

    def test_render_empty_loop(
        self, renderer: DocumentRenderer, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering loop with empty items"""
        loop_section = {
            "type": "loop",
            "variable": "items",
            "item_name": "item",
            "sections": [
                {"type": "paragraph", "text": "{{ item }}"}
            ]
        }
        
        # Empty items list
        context = {"items": []}
        result_index = renderer._render_section("test_doc", loop_section, 1, context)
        
        # Index should not change for empty loop
        assert result_index == 1
        # No insert_text calls
        mock_docs_service.insert_text.assert_not_called()


class TestRenderImage:
    """Tests for image section rendering"""

    def test_render_image_with_existing_file(
        self, temp_templates_dir: Path, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering image when file exists"""
        # Create a dummy image file
        image_file = temp_templates_dir / "test_image.png"
        image_file.write_bytes(b"fake image data")
        
        template = {
            "title": "Test Doc",
            "sections": [
                {
                    "type": "image",
                    "path": str(image_file),
                    "width": 500,
                    "height": 300
                }
            ]
        }
        template_file = temp_templates_dir / "image.json"
        template_file.write_text(json.dumps(template))
        
        engine = TemplateEngine(temp_templates_dir)
        renderer = DocumentRenderer(engine, mock_docs_service)
        
        renderer.render_to_docs({}, "image.json")
        
        # Verify insert_image was called
        mock_docs_service.insert_image.assert_called_once()
        call_args = mock_docs_service.insert_image.call_args[0]
        assert call_args[1] == image_file  # path
        assert call_args[3] == 500  # width
        assert call_args[4] == 300  # height

    def test_render_image_with_nonexistent_file(
        self, temp_templates_dir: Path, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering image when file doesn't exist"""
        template = {
            "title": "Test Doc",
            "sections": [
                {
                    "type": "image",
                    "path": "/nonexistent/path/image.png",
                    "width": 500,
                    "height": 300
                }
            ]
        }
        template_file = temp_templates_dir / "missing_image.json"
        template_file.write_text(json.dumps(template))
        
        engine = TemplateEngine(temp_templates_dir)
        renderer = DocumentRenderer(engine, mock_docs_service)
        
        # Should not raise, just skip the image
        renderer.render_to_docs({}, "missing_image.json")
        
        # Verify insert_image was NOT called
        mock_docs_service.insert_image.assert_not_called()

    def test_render_image_with_condition_false(
        self, temp_templates_dir: Path, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering image with false condition"""
        template = {
            "title": "Test Doc",
            "sections": [
                {
                    "type": "image",
                    "path": "{{ image_path }}",
                    "width": 500,
                    "height": 300,
                    "condition": "{{ image_path }}"
                }
            ]
        }
        template_file = temp_templates_dir / "conditional_image.json"
        template_file.write_text(json.dumps(template))
        
        engine = TemplateEngine(temp_templates_dir)
        renderer = DocumentRenderer(engine, mock_docs_service)
        
        # Empty image_path should skip image
        renderer.render_to_docs({"image_path": ""}, "conditional_image.json")
        
        mock_docs_service.insert_image.assert_not_called()


class TestResolveVariable:
    """Tests for _resolve_variable method"""

    def test_resolve_simple_variable(self, renderer: DocumentRenderer) -> None:
        """Test resolving simple variable"""
        result = renderer._resolve_variable("{{ name }}", {"name": "test"})
        assert result == "test"

    def test_resolve_no_variable(self, renderer: DocumentRenderer) -> None:
        """Test string without variables"""
        result = renderer._resolve_variable("plain text", {})
        assert result == "plain text"

    def test_resolve_nested_variable(self, renderer: DocumentRenderer) -> None:
        """Test resolving nested variable"""
        result = renderer._resolve_variable(
            "{{ item.name }}",
            {"item": {"name": "nested"}}
        )
        assert result == "nested"

    def test_resolve_with_default(self, renderer: DocumentRenderer) -> None:
        """Test resolving with default filter"""
        result = renderer._resolve_variable(
            "{{ missing|default('fallback') }}",
            {}
        )
        assert result == "fallback"

    def test_resolve_non_string(self, renderer: DocumentRenderer) -> None:
        """Test resolving non-string value"""
        result = renderer._resolve_variable(123, {})  # type: ignore
        assert result == "123"

    def test_resolve_none_value(self, renderer: DocumentRenderer) -> None:
        """Test resolving None value"""
        result = renderer._resolve_variable(None, {})  # type: ignore
        assert result == ""


class TestGetNestedValue:
    """Tests for _get_nested_value method"""

    def test_get_simple_value(self, renderer: DocumentRenderer) -> None:
        """Test getting simple value"""
        context = {"key": "value"}
        result = renderer._get_nested_value(context, "key")
        assert result == "value"

    def test_get_nested_value(self, renderer: DocumentRenderer) -> None:
        """Test getting nested value with dot notation"""
        context = {"outer": {"inner": "deep"}}
        result = renderer._get_nested_value(context, "outer.inner")
        assert result == "deep"

    def test_get_deeply_nested_value(self, renderer: DocumentRenderer) -> None:
        """Test getting deeply nested value"""
        context = {"a": {"b": {"c": {"d": "found"}}}}
        result = renderer._get_nested_value(context, "a.b.c.d")
        assert result == "found"

    def test_get_missing_key(self, renderer: DocumentRenderer) -> None:
        """Test getting missing key returns None"""
        context = {"key": "value"}
        result = renderer._get_nested_value(context, "missing")
        assert result is None

    def test_get_missing_nested_key(self, renderer: DocumentRenderer) -> None:
        """Test getting missing nested key returns None"""
        context = {"outer": {"inner": "value"}}
        result = renderer._get_nested_value(context, "outer.missing")
        assert result is None

    def test_get_list_value(self, renderer: DocumentRenderer) -> None:
        """Test getting list value"""
        context = {"items": [1, 2, 3]}
        result = renderer._get_nested_value(context, "items")
        assert result == [1, 2, 3]


class TestBlogDefaultTemplate:
    """Integration tests with blog_default.json template structure"""

    def test_render_blog_like_structure(
        self, temp_templates_dir: Path, mock_docs_service: MagicMock
    ) -> None:
        """Test rendering a blog-like structure similar to blog_default.json
        
        Note: The actual blog_default.json template uses Jinja2 variables inside
        loop sections that are resolved during _render_section, not during the
        initial template rendering. For testing the full integration, we create
        a simplified template that doesn't have variables in loop sections.
        """
        # Simplified template without variables in loop sections
        # (loop variables are resolved during _render_section)
        template = {
            "title": "{{ selected_title or 'Default Title' }}",
            "sections": [
                {"type": "heading", "level": 1, "text": "{{ selected_title or 'Title' }}"},
                {"type": "paragraph", "text": "\n"},
                {"type": "paragraph", "text": "{{ lead or '' }}"},
                {"type": "heading", "level": 2, "text": "Summary"},
                {"type": "paragraph", "text": "{{ summary or '' }}"}
            ]
        }
        template_file = temp_templates_dir / "blog_simple.json"
        template_file.write_text(json.dumps(template))
        
        engine = TemplateEngine(temp_templates_dir)
        renderer = DocumentRenderer(engine, mock_docs_service)
        
        context = {
            "selected_title": "AI Writing Guide",
            "lead": "This is the introduction.",
            "summary": "In conclusion..."
        }
        
        url = renderer.render_to_docs(context, "blog_simple.json")
        
        assert url == "https://docs.google.com/document/d/test_doc_id/edit"
        mock_docs_service.create_document.assert_called_with("AI Writing Guide")
        
        # Main title + summary heading = 2 headings
        assert mock_docs_service.apply_heading_style.call_count == 2

    def test_render_with_loop_using_render_section(
        self, renderer: DocumentRenderer, mock_docs_service: MagicMock
    ) -> None:
        """Test blog structure with loops using direct _render_section calls"""
        # Simulate the sections that would be in blog_default.json
        sections = [
            {"type": "heading", "level": 1, "text": "AI Writing Guide"},
            {"type": "paragraph", "text": "\n"},
            {"type": "paragraph", "text": "This is the introduction."},
            {
                "type": "loop",
                "variable": "sections",
                "item_name": "section",
                "sections": [
                    {"type": "heading", "level": 2, "text": "{{ section.heading }}"},
                    {"type": "paragraph", "text": "{{ section.content }}"}
                ]
            },
            {"type": "heading", "level": 2, "text": "Summary"},
            {"type": "paragraph", "text": "In conclusion..."}
        ]
        
        context = {
            "sections": [
                {"heading": "Getting Started", "content": "Start here..."},
                {"heading": "Advanced Tips", "content": "Advanced content..."}
            ]
        }
        
        index = 1
        for section in sections:
            index = renderer._render_section("test_doc", section, index, context)
        
        # Main title + 2 section headings + summary heading = 4 headings
        assert mock_docs_service.apply_heading_style.call_count == 4
        
        # Check headings were inserted
        insert_calls = [call[0][1] for call in mock_docs_service.insert_text.call_args_list]
        assert any("AI Writing Guide" in str(text) for text in insert_calls)
        assert any("Getting Started" in str(text) for text in insert_calls)
        assert any("Advanced Tips" in str(text) for text in insert_calls)
