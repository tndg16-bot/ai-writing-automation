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
        self.scheduler: any = None
        self.config: Config | None = None
        self.history_manager: HistoryManager | None = None

    def initialize(self):
        """Initialize automation manager"""
        self.config = Config.load(self.config_path)
        self.history_manager = HistoryManager()

        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler

            self.scheduler = AsyncIOScheduler()
            self.scheduler.start()
        except ImportError:
            print("APScheduler not installed. Install with: pip install apscheduler>=3.10.0")
            self.scheduler = None

        print(f"[{datetime.now()}] Automation Manager started")

    def shutdown(self):
        """Shutdown the automation manager"""
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
            cron_expression: Cron expression (e.g., "0 9 * * *" for daily at 9am)
            keyword: Keyword to generate content for
            content_type: Content type (blog, youtube, yukkuri)
            client: Client configuration name
            job_id: Optional job identifier
        """
        if job_id is None:
            job_id = f"gen_{content_type}_{keyword}"

        # Schedule job
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.cron import CronTrigger

            if self.scheduler is None:
                self.scheduler = AsyncIOScheduler()
                self.scheduler.start()

            self.scheduler.add_job(
                self._run_scheduled_generation,
                trigger=CronTrigger.from_crontab(cron_expression),
                args=[keyword, content_type, client],
                id=job_id,
                name=f"Generate {content_type} for '{keyword}'",
                replace_existing=True,
            )

            print(
                f"[{datetime.now()}] Scheduled: {content_type} for '{keyword}' "
                f"with cron '{cron_expression}' (job_id: {job_id})"
            )
        except ImportError:
            print("APScheduler not installed. Install with: pip install apscheduler>=3.10.0")
            return

    async def _run_scheduled_generation(self, keyword: str, content_type: str, client: str):
        """Execute scheduled generation"""
        print(f"[{datetime.now()}] Running scheduled generation: {content_type} for '{keyword}'")

        # Ensure history manager is initialized
        if self.history_manager is None:
            self.history_manager = HistoryManager()

        try:
            # Select pipeline
            if content_type == "blog":
                pipeline = BlogPipeline(self.config)  # type: ignore
            elif content_type == "youtube":
                pipeline = YouTubePipeline(self.config)  # type: ignore
            elif content_type == "yukkuri":
                pipeline = YukkuriPipeline(self.config)  # type: ignore
            else:
                print(f"Unknown content type: {content_type}")
                return

            # Run pipeline
            context = await pipeline.run(keyword, content_type)

            # Save to history
            if self.history_manager:
                generation_id = self.history_manager.save_generation(context)
            else:
                generation_id = None
                print("Warning: History manager not available")

            print(
                f"[{datetime.now()}] Scheduled generation completed: generation_id={generation_id}"
            )

        except Exception as e:
            print(
                f"[{datetime.now()}] Scheduled generation failed: {keyword} ({content_type}) - {e}"
            )

    def schedule_from_file(self, schedule_file: str):
        """
        Load and schedule tasks from a JSON file

        File format:
        {
            "schedules": [
                {
                    "keyword": "AI副業",
                    "content_type": "blog",
                    "cron": "0 9 * * 1",
                    "job_id": "weekly_blog_ai_job"
                }
            ]
        }
        """
        with open(schedule_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for schedule in data.get("schedules", []):
            self.schedule_generation(
                cron_expression=schedule["cron"],
                keyword=schedule["keyword"],
                content_type=schedule.get("content_type", "blog"),
                client=schedule.get("client", "default"),
                job_id=schedule.get("job_id"),
            )

    def list_scheduled_jobs(self) -> list[dict[str, any]]:
        """Get list of all scheduled jobs"""
        jobs = []
        if self.scheduler:
            for job in self.scheduler.get_jobs():
                jobs.append(
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                        "trigger": str(job.trigger),
                    }
                )
        return jobs

    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job by ID"""
        try:
            if self.scheduler:
                self.scheduler.remove_job(job_id)
                print(f"[{datetime.now()}] Removed job: {job_id}")
                return True
            return False
        except Exception as e:
            print(f"[{datetime.now()}] Failed to remove job {job_id}: {e}")
            return False

    async def run_batch_generation(self, keywords: list[str], content_type: str = "blog"):
        """
        Run batch generation for multiple keywords

        Args:
            keywords: List of keywords to generate content for
            content_type: Content type to generate
        """
        print(
            f"[{datetime.now()}] Starting batch generation: "
            f"{len(keywords)} keywords ({content_type})"
        )

        # Ensure history manager is initialized
        if self.history_manager is None:
            self.history_manager = HistoryManager()

        results = []
        for keyword in keywords:
            try:
                if content_type == "blog":
                    pipeline = BlogPipeline(self.config)  # type: ignore
                elif content_type == "youtube":
                    pipeline = YouTubePipeline(self.config)  # type: ignore
                elif content_type == "yukkuri":
                    pipeline = YukkuriPipeline(self.config)  # type: ignore
                else:
                    raise ValueError(f"Unknown content type: {content_type}")

                context = await pipeline.run(keyword, content_type)
                if self.history_manager:
                    generation_id = self.history_manager.save_generation(context)
                else:
                    generation_id = None

                results.append(
                    {
                        "keyword": keyword,
                        "status": "completed",
                        "generation_id": generation_id,
                    }
                )

                print(f"[{datetime.now()}] Batch: Completed '{keyword}' (id: {generation_id})")

            except Exception as e:
                results.append({"keyword": keyword, "status": "failed", "error": str(e)})
                print(f"[{datetime.now()}] Batch: Failed '{keyword}' - {e}")

        print(
            f"[{datetime.now()}] Batch generation completed: "
            f"{sum(1 for r in results if r['status'] == 'completed')}/{len(keywords)} "
            f"successful"
        )

        return results


# Example schedule configuration file
DEFAULT_SCHEDULE_CONFIG = {
    "schedules": [
        {
            "keyword": "AI副業",
            "content_type": "blog",
            "cron": "0 9 * * 1",  # Every Monday at 9:00 AM
            "job_id": "weekly_blog_ai_shugyou",
        },
        {
            "keyword": "投資信託",
            "content_type": "blog",
            "cron": "0 10 * * 2",  # Every Tuesday at 10:00 AM
            "job_id": "weekly_blog_investment",
        },
    ]
}
