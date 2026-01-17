"""History Manager for AI Writing Automation

This module provides functionality to save and retrieve generation history.
"""

import json
from typing import Any, Optional

from ai_writing.core.context import GenerationContext, Section
from ai_writing.core.database import Database


class HistoryManager:
    """Manager for generation history

    Handles saving and retrieving generation history from database.
    """

    def __init__(self, db_path: str = "./data/history.db"):
        """Initialize history manager

        Args:
            db_path: Path to SQLite database
        """
        self.db = Database(db_path)

    def save_generation(self, context: GenerationContext) -> int:
        """Save generation to database

        Args:
            context: Generation context to save

        Returns:
            Generation ID
        """
        # Prepare generation data
        generation_data = {
            "keyword": context.keyword,
            "content_type": context.content_type,
            "title": context.selected_title,
            "lead": context.lead,
            "sections_count": len(context.sections),
            "images_count": len(context.images),
            "client_config": context.client_config,
            "raw_responses": context.raw_responses,
        }

        # Save generation
        generation_id = self.db.save_generation(generation_data)

        # Save images
        for image in context.images:
            image_data = {
                "generation_id": generation_id,
                **image,
            }
            self.db.save_image(image_data)

        # Check if this is a version of an existing generation
        existing = self.db.list_generations(
            keyword=context.keyword,
            content_type=context.content_type,
            limit=100,
        )

        # Find other generations with same keyword
        same_keyword = [
            g for g in existing if g["keyword"] == context.keyword and g["id"] != generation_id
        ]

        if same_keyword:
            # This is a new version
            version_data = {
                "generation_id": generation_id,
                "version_number": len(same_keyword) + 1,
                "diff": self._calculate_diff(same_keyword[-1], generation_data),
            }
            self.db.save_version(version_data)

        return generation_id

    def get_generation(self, generation_id: int) -> Optional[dict[str, Any]]:
        """Get generation by ID

        Args:
            generation_id: Generation ID

        Returns:
            Generation data or None
        """
        generation = self.db.get_generation(generation_id)
        if generation is None:
            return None

        # Load images
        images = self.db.get_images(generation_id)

        # Load versions
        versions = self.db.get_versions(generation_id)

        return {
            **generation,
            "images": images,
            "versions": versions,
        }

    def list_generations(
        self,
        keyword: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List generations with optional filters

        Args:
            keyword: Filter by keyword (partial match)
            content_type: Filter by content type
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of generation records
        """
        return self.db.list_generations(
            keyword=keyword,
            content_type=content_type,
            limit=limit,
            offset=offset,
        )

    def delete_generation(self, generation_id: int) -> bool:
        """Delete generation by ID

        Args:
            generation_id: Generation ID

        Returns:
            True if deleted, False otherwise
        """
        return self.db.delete_generation(generation_id)

    def get_stats(self) -> dict[str, Any]:
        """Get generation statistics

        Returns:
            Statistics dictionary
        """
        return self.db.get_stats()

    def _calculate_diff(self, old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
        """Calculate diff between two generations

        Args:
            old: Old generation data
            new: New generation data

        Returns:
            Diff dictionary
        """
        diff = {
            "title_changed": old.get("title") != new.get("title"),
            "lead_changed": old.get("lead") != new.get("lead"),
            "sections_count_changed": old.get("sections_count") != new.get("sections_count"),
            "images_count_changed": old.get("images_count") != new.get("images_count"),
        }

        if diff["title_changed"]:
            diff["old_title"] = old.get("title")
            diff["new_title"] = new.get("title")

        if diff["lead_changed"]:
            diff["old_lead"] = old.get("lead")
            diff["new_lead"] = new.get("lead")

        return diff

    def export_generation(self, generation_id: int) -> Optional[str]:
        """Export generation as Markdown

        Args:
            generation_id: Generation ID

        Returns:
            Markdown string or None
        """
        generation = self.get_generation(generation_id)
        if generation is None:
            return None

        lines = []

        # Title
        if generation.get("title"):
            lines.append(f"# {generation['title']}")
            lines.append("")

        # Lead
        if generation.get("lead"):
            lines.append(generation["lead"])
            lines.append("")

        # Sections
        if "images" in generation and generation["images"]:
            lines.append("## Generated Images")
            lines.append("")

            for i, image in enumerate(generation["images"], 1):
                lines.append(f"{i}. {image.get('section_heading', 'N/A')}")
                lines.append(f"   URL: {image['url']}")
                lines.append(f"   Provider: {image['provider']}")
                lines.append(f"   Model: {image.get('model', 'N/A')}")
                lines.append("")

        # Metadata
        lines.append("---")
        lines.append("")
        lines.append(f"**Keyword**: {generation['keyword']}")
        lines.append(f"**Content Type**: {generation['content_type']}")
        lines.append(f"**Created**: {generation['created_at']}")
        lines.append("")

        return "\n".join(lines)
