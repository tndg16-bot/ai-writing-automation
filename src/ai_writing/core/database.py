"""Database management for AI Writing Automation

This module provides SQLite database access for history management.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager


class Database:
    """SQLite database manager for generation history"""

    def __init__(self, db_path: str | Path = "./data/history.db"):
        """Initialize database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _initialize(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Generations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    title TEXT,
                    lead TEXT,
                    sections_count INTEGER,
                    images_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    client_config TEXT,
                    raw_responses TEXT
                )
            """)

            # Images table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generation_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT,
                    prompt TEXT,
                    section_heading TEXT,
                    cached BOOLEAN DEFAULT 0,
                    FOREIGN KEY (generation_id) REFERENCES generations(id) ON DELETE CASCADE
                )
            """)

            # Versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generation_id INTEGER NOT NULL,
                    version_number INTEGER NOT NULL,
                    diff TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (generation_id) REFERENCES generations(id) ON DELETE CASCADE,
                    UNIQUE(generation_id, version_number)
                )
            """)

            # Create indexes for search efficiency
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_generations_keyword
                ON generations(keyword)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_generations_content_type
                ON generations(content_type)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_generations_created_at
                ON generations(created_at DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_images_generation_id
                ON images(generation_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_versions_generation_id
                ON versions(generation_id)
            """)

    # CRUD Operations for Generations

    def save_generation(self, generation_data: dict[str, Any]) -> int:
        """Save a generation record

        Args:
            generation_data: Generation data dictionary

        Returns:
            Generation ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Convert dict to JSON for storage
            client_config = json.dumps(generation_data.get("client_config", {}))
            raw_responses = json.dumps(generation_data.get("raw_responses", {}))

            cursor.execute(
                """
                INSERT INTO generations (
                    keyword, content_type, title, lead, sections_count,
                    images_count, client_config, raw_responses
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    generation_data["keyword"],
                    generation_data["content_type"],
                    generation_data.get("title"),
                    generation_data.get("lead"),
                    generation_data.get("sections_count"),
                    generation_data.get("images_count"),
                    client_config,
                    raw_responses,
                ),
            )

            return cursor.lastrowid

    def get_generation(self, generation_id: int) -> Optional[dict[str, Any]]:
        """Get generation by ID

        Args:
            generation_id: Generation ID

        Returns:
            Generation data or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM generations WHERE id = ?
            """,
                (generation_id,),
            )

            row = cursor.fetchone()
            if row is None:
                return None

            return {
                "id": row["id"],
                "keyword": row["keyword"],
                "content_type": row["content_type"],
                "title": row["title"],
                "lead": row["lead"],
                "sections_count": row["sections_count"],
                "images_count": row["images_count"],
                "created_at": row["created_at"],
                "client_config": json.loads(row["client_config"]) if row["client_config"] else {},
                "raw_responses": json.loads(row["raw_responses"]) if row["raw_responses"] else {},
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
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM generations WHERE 1=1"
            params = []

            if keyword:
                query += " AND keyword LIKE ?"
                params.append(f"%{keyword}%")

            if content_type:
                query += " AND content_type = ?"
                params.append(content_type)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)

            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "keyword": row["keyword"],
                    "content_type": row["content_type"],
                    "title": row["title"],
                    "lead": row["lead"],
                    "sections_count": row["sections_count"],
                    "images_count": row["images_count"],
                    "created_at": row["created_at"],
                    "client_config": json.loads(row["client_config"])
                    if row["client_config"]
                    else {},
                    "raw_responses": json.loads(row["raw_responses"])
                    if row["raw_responses"]
                    else {},
                }
                for row in rows
            ]

    def delete_generation(self, generation_id: int) -> bool:
        """Delete generation by ID

        Args:
            generation_id: Generation ID

        Returns:
            True if deleted, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM generations WHERE id = ?
            """,
                (generation_id,),
            )

            return cursor.rowcount > 0

    # CRUD Operations for Images

    def save_image(self, image_data: dict[str, Any]) -> int:
        """Save an image record

        Args:
            image_data: Image data dictionary

        Returns:
            Image ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO images (
                    generation_id, url, provider, model,
                    prompt, section_heading, cached
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    image_data["generation_id"],
                    image_data["url"],
                    image_data["provider"],
                    image_data.get("model"),
                    image_data.get("prompt"),
                    image_data.get("section_heading"),
                    image_data.get("cached", False),
                ),
            )

            return cursor.lastrowid

    def get_images(self, generation_id: int) -> list[dict[str, Any]]:
        """Get images for a generation

        Args:
            generation_id: Generation ID

        Returns:
            List of image records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM images WHERE generation_id = ?
                ORDER BY id
            """,
                (generation_id,),
            )

            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "generation_id": row["generation_id"],
                    "url": row["url"],
                    "provider": row["provider"],
                    "model": row["model"],
                    "prompt": row["prompt"],
                    "section_heading": row["section_heading"],
                    "cached": bool(row["cached"]),
                }
                for row in rows
            ]

    # CRUD Operations for Versions

    def save_version(self, version_data: dict[str, Any]) -> int:
        """Save a version record

        Args:
            version_data: Version data dictionary

        Returns:
            Version ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO versions (
                    generation_id, version_number, diff
                ) VALUES (?, ?, ?)
            """,
                (
                    version_data["generation_id"],
                    version_data["version_number"],
                    json.dumps(version_data.get("diff")),
                ),
            )

            return cursor.lastrowid

    def get_versions(self, generation_id: int) -> list[dict[str, Any]]:
        """Get versions for a generation

        Args:
            generation_id: Generation ID

        Returns:
            List of version records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM versions WHERE generation_id = ?
                ORDER BY version_number
            """,
                (generation_id,),
            )

            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "generation_id": row["generation_id"],
                    "version_number": row["version_number"],
                    "diff": json.loads(row["diff"]) if row["diff"] else None,
                    "created_at": row["created_at"],
                }
                for row in rows
            ]

    def get_latest_version(self, generation_id: int) -> Optional[dict[str, Any]]:
        """Get latest version for a generation

        Args:
            generation_id: Generation ID

        Returns:
            Latest version or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM versions WHERE generation_id = ?
                ORDER BY version_number DESC LIMIT 1
            """,
                (generation_id,),
            )

            row = cursor.fetchone()
            if row is None:
                return None

            return {
                "id": row["id"],
                "generation_id": row["generation_id"],
                "version_number": row["version_number"],
                "diff": json.loads(row["diff"]) if row["diff"] else None,
                "created_at": row["created_at"],
            }

    # Statistics

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics

        Returns:
            Statistics dictionary
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Count generations
            cursor.execute("SELECT COUNT(*) as count FROM generations")
            total_generations = cursor.fetchone()["count"]

            # Count by content type
            cursor.execute("""
                SELECT content_type, COUNT(*) as count
                FROM generations
                GROUP BY content_type
            """)
            by_content_type = {row["content_type"]: row["count"] for row in cursor.fetchall()}

            # Count images
            cursor.execute("SELECT COUNT(*) as count FROM images")
            total_images = cursor.fetchone()["count"]

            # Count by image provider
            cursor.execute("""
                SELECT provider, COUNT(*) as count
                FROM images
                GROUP BY provider
            """)
            by_provider = {row["provider"]: row["count"] for row in cursor.fetchall()}

            # Database size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

            return {
                "total_generations": total_generations,
                "total_images": total_images,
                "by_content_type": by_content_type,
                "by_provider": by_provider,
                "db_size_bytes": db_size,
                "db_path": str(self.db_path),
            }
