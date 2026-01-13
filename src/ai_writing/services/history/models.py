"""Database models for generation history"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class GenerationHistory(Base):
    """Generation history model"""

    __tablename__ = "generation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Input
    keyword: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(50))  # blog, youtube, yukkuri

    # Content
    persona: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lead: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    intro: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ending: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Structured data (JSON strings)
    structure: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sections: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Output
    docs_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    local_output: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Client
    client_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # LLM settings
    llm_model: Mapped[str] = mapped_column(String(100))
    temperature: Mapped[float] = mapped_column(Float, default=0.7)

    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    # Status
    status: Mapped[str] = mapped_column(String(50), default="completed")  # completed, failed

    # Error message (if failed)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<GenerationHistory(id={self.id}, keyword='{self.keyword}', "
            f"content_type='{self.content_type}', created_at={self.created_at})>"
        )
