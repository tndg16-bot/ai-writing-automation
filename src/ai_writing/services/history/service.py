"""History service for generation tracking"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ai_writing.services.history.models import Base, GenerationHistory
from ai_writing.core.exceptions import AIWritingError


class HistoryService:
    """Service for managing generation history"""

    def __init__(self, db_url: str | None = None):
        """Initialize history service

        Args:
            db_url: Database URL (default: SQLite in data/ directory)
        """
        if db_url is None:
            # Default to SQLite
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "history.db"
            db_url = f"sqlite:///{db_path}"

        self.db_url = db_url
        self.engine = create_engine(db_url)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    def save_generation(
        self,
        keyword: str,
        content_type: str,
        context: Any,
        docs_url: str | None = None,
        local_output: str | None = None,
        client_name: str | None = None,
        status: str = "completed",
        error_message: str | None = None,
    ) -> int:
        """Save generation to history

        Args:
            keyword: Main keyword
            content_type: Content type (blog, youtube, yukkuri)
            context: GenerationContext
            docs_url: Google Docs URL
            local_output: Local output path
            client_name: Client name
            status: Generation status
            error_message: Error message (if failed)

        Returns:
            Generation ID
        """
        try:
            with Session(self.engine) as session:
                history = GenerationHistory(
                    keyword=keyword,
                    content_type=content_type,
                    persona=context.persona,
                    lead=context.lead,
                    summary=context.summary,
                    intro=context.intro,
                    ending=context.ending,
                    structure=json.dumps(context.structure, ensure_ascii=False),
                    sections=json.dumps(
                        [
                            {
                                "heading": s.heading,
                                "content": s.content,
                                "subsections": [
                                    {"heading": sub.heading, "content": sub.content}
                                    for sub in s.subsections
                                ],
                                "image_path": s.image_path,
                            }
                            for s in context.sections
                        ],
                        ensure_ascii=False,
                    ),
                    images=json.dumps(context.images, ensure_ascii=False),
                    docs_url=docs_url,
                    local_output=local_output,
                    client_name=client_name,
                    llm_model=getattr(context, "llm_model", "gpt-4"),
                    temperature=getattr(context, "temperature", 0.7),
                    status=status,
                    error_message=error_message,
                )

                session.add(history)
                session.commit()
                session.refresh(history)

                return history.id

        except Exception as e:
            raise AIWritingError(f"Failed to save generation history: {e}") from e

    def get_generation(self, generation_id: int) -> dict[str, Any] | None:
        """Get generation by ID

        Args:
            generation_id: Generation ID

        Returns:
            Generation data or None if not found
        """
        try:
            with Session(self.engine) as session:
                result = session.get(GenerationHistory, generation_id)
                if result is None:
                    return None

                return self._to_dict(result)

        except Exception as e:
            raise AIWritingError(f"Failed to get generation: {e}") from e

    def list_generations(
        self,
        limit: int = 100,
        offset: int = 0,
        content_type: str | None = None,
        keyword: str | None = None,
    ) -> list[dict[str, Any]]:
        """List generations

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            content_type: Filter by content type
            keyword: Filter by keyword (partial match)

        Returns:
            List of generation data
        """
        try:
            with Session(self.engine) as session:
                query = select(GenerationHistory)

                # Apply filters
                if content_type:
                    query = query.where(GenerationHistory.content_type == content_type)
                if keyword:
                    query = query.where(GenerationHistory.keyword.contains(keyword))

                # Order by created_at desc
                query = query.order_by(GenerationHistory.created_at.desc())

                # Apply pagination
                query = query.limit(limit).offset(offset)

                results = session.execute(query).scalars().all()

                return [self._to_dict(r) for r in results]

        except Exception as e:
            raise AIWritingError(f"Failed to list generations: {e}") from e

    def _to_dict(self, history: GenerationHistory) -> dict[str, Any]:
        """Convert GenerationHistory to dictionary"""
        return {
            "id": history.id,
            "keyword": history.keyword,
            "content_type": history.content_type,
            "persona": history.persona,
            "lead": history.lead,
            "summary": history.summary,
            "intro": history.intro,
            "ending": history.ending,
            "structure": json.loads(history.structure) if history.structure else [],
            "sections": json.loads(history.sections) if history.sections else [],
            "images": json.loads(history.images) if history.images else [],
            "docs_url": history.docs_url,
            "local_output": history.local_output,
            "client_name": history.client_name,
            "llm_model": history.llm_model,
            "temperature": history.temperature,
            "created_at": history.created_at.isoformat(),
            "updated_at": history.updated_at.isoformat(),
            "status": history.status,
            "error_message": history.error_message,
        }

    def update_status(
        self,
        generation_id: int,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """Update generation status

        Args:
            generation_id: Generation ID
            status: New status
            error_message: Error message (if failed)
        """
        try:
            with Session(self.engine) as session:
                history = session.get(GenerationHistory, generation_id)
                if history is None:
                    raise AIWritingError(f"Generation {generation_id} not found")

                history.status = status
                history.error_message = error_message
                history.updated_at = datetime.now()

                session.commit()

        except AIWritingError:
            raise
        except Exception as e:
            raise AIWritingError(f"Failed to update status: {e}") from e
