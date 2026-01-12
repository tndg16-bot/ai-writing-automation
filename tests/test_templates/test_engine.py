"""Tests for TemplateEngine"""

import tempfile
from pathlib import Path

import pytest

from ai_writing.templates.engine import TemplateEngine
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


class TestTemplateEngineInit:
    """Tests for TemplateEngine initialization"""

    def test_init_creates_environment(self, temp_templates_dir: Path) -> None:
        """Test that initialization creates Jinja2 environment"""
        engine = TemplateEngine(temp_templates_dir)
        
        assert engine.templates_dir == temp_templates_dir
        assert engine.env is not None

    def test_init_registers_filters(self, temp_templates_dir: Path) -> None:
        """Test that custom filters are registered"""
        engine = TemplateEngine(temp_templates_dir)
        
        assert "split_lines" in engine.env.filters
        assert "first_line" in engine.env.filters


class TestSplitLinesFilter:
    """Tests for split_lines filter"""

    def test_split_lines_basic(self, template_engine: TemplateEngine) -> None:
        """Test split_lines filter with basic input"""
        result = template_engine.render_string(
            "{% for line in text|split_lines %}{{ line }}-{% endfor %}",
            {"text": "line1\nline2\nline3"}
        )
        assert result == "line1-line2-line3-"

    def test_split_lines_single_line(self, template_engine: TemplateEngine) -> None:
        """Test split_lines filter with single line"""
        result = template_engine.render_string(
            "{% for line in text|split_lines %}{{ line }}{% endfor %}",
            {"text": "single line"}
        )
        assert result == "single line"

    def test_split_lines_empty(self, template_engine: TemplateEngine) -> None:
        """Test split_lines filter with empty string"""
        result = template_engine.render_string(
            "{% for line in text|split_lines %}{{ line }}{% endfor %}",
            {"text": ""}
        )
        assert result == ""


class TestFirstLineFilter:
    """Tests for first_line filter"""

    def test_first_line_basic(self, template_engine: TemplateEngine) -> None:
        """Test first_line filter with multiple lines"""
        result = template_engine.render_string(
            "{{ text|first_line }}",
            {"text": "first\nsecond\nthird"}
        )
        assert result == "first"

    def test_first_line_single(self, template_engine: TemplateEngine) -> None:
        """Test first_line filter with single line"""
        result = template_engine.render_string(
            "{{ text|first_line }}",
            {"text": "only line"}
        )
        assert result == "only line"

    def test_first_line_empty(self, template_engine: TemplateEngine) -> None:
        """Test first_line filter with empty string"""
        result = template_engine.render_string(
            "{{ text|first_line }}",
            {"text": ""}
        )
        assert result == ""


class TestRenderTemplate:
    """Tests for render_template method"""

    def test_render_template_success(self, temp_templates_dir: Path) -> None:
        """Test successful template rendering from file"""
        # Create test template
        template_file = temp_templates_dir / "test.html"
        template_file.write_text("Hello, {{ name }}!")
        
        engine = TemplateEngine(temp_templates_dir)
        result = engine.render_template("test.html", {"name": "World"})
        
        assert result == "Hello, World!"

    def test_render_template_with_complex_context(self, temp_templates_dir: Path) -> None:
        """Test template rendering with complex context"""
        template_file = temp_templates_dir / "complex.html"
        template_file.write_text(
            "{% for item in items %}{{ item.name }}: {{ item.value }}; {% endfor %}"
        )
        
        engine = TemplateEngine(temp_templates_dir)
        context = {
            "items": [
                {"name": "a", "value": 1},
                {"name": "b", "value": 2},
            ]
        }
        result = engine.render_template("complex.html", context)
        
        assert result == "a: 1; b: 2; "

    def test_render_template_not_found(self, template_engine: TemplateEngine) -> None:
        """Test that TemplateError is raised for missing template"""
        with pytest.raises(TemplateError) as exc_info:
            template_engine.render_template("nonexistent.html", {})
        
        assert "Template not found" in str(exc_info.value)

    def test_render_template_syntax_error(self, temp_templates_dir: Path) -> None:
        """Test that TemplateError is raised for syntax errors"""
        # Create template with syntax error
        template_file = temp_templates_dir / "bad.html"
        template_file.write_text("{% for item in items %}")  # Missing endfor
        
        engine = TemplateEngine(temp_templates_dir)
        
        with pytest.raises(TemplateError) as exc_info:
            engine.render_template("bad.html", {"items": []})
        
        assert "syntax error" in str(exc_info.value).lower()


class TestRenderString:
    """Tests for render_string method"""

    def test_render_string_success(self, template_engine: TemplateEngine) -> None:
        """Test successful string template rendering"""
        result = template_engine.render_string(
            "Hello, {{ name }}!",
            {"name": "World"}
        )
        assert result == "Hello, World!"

    def test_render_string_with_filter(self, template_engine: TemplateEngine) -> None:
        """Test string template with custom filter"""
        result = template_engine.render_string(
            "{{ text|first_line }}",
            {"text": "line1\nline2"}
        )
        assert result == "line1"

    def test_render_string_with_conditionals(self, template_engine: TemplateEngine) -> None:
        """Test string template with conditionals"""
        template = "{% if show %}visible{% else %}hidden{% endif %}"
        
        assert template_engine.render_string(template, {"show": True}) == "visible"
        assert template_engine.render_string(template, {"show": False}) == "hidden"

    def test_render_string_syntax_error(self, template_engine: TemplateEngine) -> None:
        """Test that TemplateError is raised for syntax errors in string"""
        with pytest.raises(TemplateError) as exc_info:
            template_engine.render_string("{% if x %}", {"x": True})
        
        assert "syntax error" in str(exc_info.value).lower()

    def test_render_string_with_default_filter(self, template_engine: TemplateEngine) -> None:
        """Test string template with Jinja2 default filter"""
        result = template_engine.render_string(
            "{{ missing|default('fallback') }}",
            {}
        )
        assert result == "fallback"


class TestLoadTemplate:
    """Tests for load_template method"""

    def test_load_template_success(self, temp_templates_dir: Path) -> None:
        """Test successful template loading"""
        template_file = temp_templates_dir / "load_test.html"
        template_file.write_text("{{ value }}")
        
        engine = TemplateEngine(temp_templates_dir)
        template = engine.load_template("load_test.html")
        
        assert template is not None
        assert template.render(value="test") == "test"

    def test_load_template_not_found(self, template_engine: TemplateEngine) -> None:
        """Test that TemplateError is raised for missing template"""
        with pytest.raises(TemplateError) as exc_info:
            template_engine.load_template("missing.html")
        
        assert "Template not found" in str(exc_info.value)


class TestJsonTemplateRendering:
    """Tests for JSON template rendering (used by DocumentRenderer)"""

    def test_render_json_template(self, temp_templates_dir: Path) -> None:
        """Test rendering a JSON template"""
        template_file = temp_templates_dir / "test.json"
        template_file.write_text('{"title": "{{ title }}", "content": "{{ content }}"}')
        
        engine = TemplateEngine(temp_templates_dir)
        result = engine.render_template("test.json", {
            "title": "Test Title",
            "content": "Test Content"
        })
        
        import json
        data = json.loads(result)
        assert data["title"] == "Test Title"
        assert data["content"] == "Test Content"

    def test_render_json_with_loops(self, temp_templates_dir: Path) -> None:
        """Test rendering JSON template with loops"""
        template_content = '''{
    "sections": [
        {% for section in sections %}
        {"name": "{{ section.name }}"}{% if not loop.last %},{% endif %}
        {% endfor %}
    ]
}'''
        template_file = temp_templates_dir / "loop.json"
        template_file.write_text(template_content)
        
        engine = TemplateEngine(temp_templates_dir)
        result = engine.render_template("loop.json", {
            "sections": [
                {"name": "Section 1"},
                {"name": "Section 2"}
            ]
        })
        
        import json
        data = json.loads(result)
        assert len(data["sections"]) == 2
        assert data["sections"][0]["name"] == "Section 1"
        assert data["sections"][1]["name"] == "Section 2"
