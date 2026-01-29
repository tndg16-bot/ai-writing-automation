"""Automation module for scheduled content generation"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import asyncio
import json
from datetime import datetime

from ai_writing.pipeline.blog import BlogPipeline
from ai_writing.pipeline.youtube import YouTubePipeline
from ai_writing.pipeline.yukkuri import YukkuriPipeline
from ai_writing.core.config import Config
from ai_writing.core.history_manager import HistoryManager


class AutomationManager:
    """Manages scheduled content generation tasks"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.scheduler = None
        self.config: Config | None = None
        self.history_manager: HistoryManager | None = None

    def initialize(self):
        """Initialize automation manager"""
        self.config = Config.load(self.config_path)
        self.history_manager = HistoryManager()

        try:
            # Import APScheduler inside method to avoid import errors
            import apscheduler.schedulers.asyncio as scheduler_asyncio
            import apscheduler.triggers.cron as scheduler_cron

            self.scheduler = scheduler_asyncio.AsyncIOScheduler()
            self.scheduler.start()
        except ImportError as e:
            print(
                f"APScheduler not installed. Install with: pip install apscheduler>=3.10.0. Error: {e}"
            )
            self.scheduler = None

        print(f"[{datetime.now()}] Automation Manager started")

    def shutdown(self):
        """Shutdown automation manager"""
        if self.scheduler:
            self.scheduler.shutdown()
        print(f"[{datetime.now()}] Automation Manager stopped")

    def schedule_generation(
        self,
        cron_expression: str,
        keyword: str,
        content_type: str = "blog",
        client: str = "default",
        job_id: str | None = None,
    ):
        """
        Schedule a content generation task

        Args:
            cron_expression: Cron expression (e.g., "0 9 * *" for daily at 9am)
            keyword: Keyword to generate content for
            content_type: Content type (blog, youtube, yukkuri)
            client: Client configuration name
            job_id: Optional job identifier
        """
        if job_id is None:
            job_id = f"gen_{content_type}_{keyword}"

        # Schedule job
        if self.scheduler:
            try:
                import apscheduler.schedulers.asyncio as scheduler_asyncio
                import apscheduler.triggers.cron as scheduler_cron

                # Map content type to pipeline
                pipeline_map = {
                    "blog": BlogPipeline,
                    "youtube": YouTubePipeline,
                    "yukkuri": YukkuriPipeline,
                }

                pipeline = pipeline_map.get(content_type, BlogPipeline)

                async def run_generation():
                    try:
                        print(f"[{datetime.now()}] Starting generation: {keyword} ({content_type})")
                        context = await pipeline.run(keyword, content_type=content_type)

                        # Save to history
                        if self.history_manager:
                            self.history_manager.save_generation(
                                context, keyword, content_type, client
                            )

                        print(f"[{datetime.now()}] Generation completed: {keyword}")
                    except Exception as e:
                        print(f"[{datetime.now()}] Generation failed: {keyword}. Error: {e}")

                # Add job to scheduler
                self.scheduler.add_job(
                    run_generation,
                    trigger=scheduler_cron.CronTrigger.from_crontab(cron_expression),
                    id=job_id,
                    name=f"Generate {content_type}: {keyword}",
                )

                print(f"[{datetime.now()}] Scheduled job: {job_id}")
            except Exception as e:
                print(f"[{datetime.now()}] Failed to schedule job: {job_id}. Error: {e}")
        else:
            print("Scheduler not available. Cannot schedule jobs.")

    async def run_generation_now(
        self,
        keyword: str,
        content_type: str = "blog",
        client: str = "default",
    ):
        """Run generation immediately"""
        try:
            pipeline_map = {
                "blog": BlogPipeline,
                "youtube": YouTubePipeline,
                "yukkuri": YukkuriPipeline,
            }

            pipeline = pipeline_map.get(content_type, BlogPipeline)

            print(f"[{datetime.now()}] Starting generation: {keyword} ({content_type})")
            context = await pipeline.run(keyword, content_type=content_type)

            # Save to history
            if self.history_manager:
                self.history_manager.save_generation(context, keyword, content_type, client)

            print(f"[{datetime.now()}] Generation completed: {keyword}")
            return context
        except Exception as e:
            print(f"[{datetime.now()}] Generation failed: {keyword}. Error: {e}")
            return None
