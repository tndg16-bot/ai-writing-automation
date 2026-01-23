"""CLI for automation management"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import json
import typer
from automation.manager import AutomationManager

app = typer.Typer(
    name="automation",
    help="AI Writing Automation - Scheduled content generation",
)


@app.command()
def start(
    schedule_file: str = typer.Option(
        None, "--schedule", "-s", help="Schedule configuration JSON file"
    ),
):
    """Start the automation scheduler"""
    manager = AutomationManager()
    manager.initialize()

    if schedule_file:
        print(f"Loading schedule from: {schedule_file}")
        manager.schedule_from_file(schedule_file)

    # Display scheduled jobs
    jobs = manager.list_scheduled_jobs()
    print(f"\n{len(jobs)} jobs scheduled:")
    for job in jobs:
        print(f"  - {job['name']} (next: {job['next_run']})")

    print("\nAutomation manager running. Press Ctrl+C to stop.\n")

    # Keep running
    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        manager.shutdown()
        print("\nStopped.")


@app.command()
def run(
    keyword: str = typer.Option(..., "--keyword", "-k", help="Keyword to generate"),
    content_type: str = typer.Option(
        "blog", "--type", "-t", help="Content type: blog, youtube, yukkuri"
    ),
    client: str = typer.Option("default", "--client", "-c", help="Client configuration"),
):
    """Run a single generation task"""

    async def _run():
        manager = AutomationManager()
        manager.initialize()
        result = await manager._run_scheduled_generation(keyword, content_type, client)
        manager.shutdown()
        return result

    asyncio.run(_run())


@app.command()
def batch(
    keywords_file: str = typer.Option(
        ..., "--keywords", "-k", help="File with one keyword per line"
    ),
    content_type: str = typer.Option(
        "blog", "--type", "-t", help="Content type: blog, youtube, yukkuri"
    ),
):
    """Run batch generation from a file of keywords"""
    with open(keywords_file, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    async def _run_batch():
        manager = AutomationManager()
        manager.initialize()
        results = await manager.run_batch_generation(keywords, content_type)
        manager.shutdown()

        print(f"\nBatch Results:")
        for result in results:
            status = "✓" if result["status"] == "completed" else "✗"
            print(f"  {status} {result['keyword']}")
            if result["status"] == "failed":
                print(f"    Error: {result['error']}")
            elif "generation_id" in result:
                print(f"    Generation ID: {result['generation_id']}")

    asyncio.run(_run_batch())


@app.command("list")
def list_jobs():
    """List all scheduled jobs"""
    manager = AutomationManager()
    manager.initialize()

    jobs = manager.list_scheduled_jobs()

    if not jobs:
        print("No scheduled jobs.")
        return

    print(f"\n{len(jobs)} scheduled jobs:")
    for job in jobs:
        print(f"  ID: {job['id']}")
        print(f"  Name: {job['name']}")
        print(f"  Next Run: {job['next_run']}")
        print(f"  Trigger: {job['trigger']}")
        print()

    manager.shutdown()


@app.command("remove")
def remove_job(job_id: str = typer.Option(..., "--id", "-i", help="Job ID to remove")):
    """Remove a scheduled job"""
    manager = AutomationManager()
    manager.initialize()

    if manager.remove_job(job_id):
        print(f"Job '{job_id}' removed successfully.")
    else:
        print(f"Failed to remove job '{job_id}'.")

    manager.shutdown()


@app.command("schedule")
def schedule(
    keyword: str = typer.Option(..., "--keyword", "-k", help="Keyword for content"),
    content_type: str = typer.Option("blog", "--type", "-t", help="Content type"),
    cron: str = typer.Option(..., "--cron", "-c", help="Cron expression"),
    client: str = typer.Option("default", "--client", help="Client config"),
):
    """Schedule a new generation job"""
    manager = AutomationManager()
    manager.initialize()

    manager.schedule_generation(
        cron_expression=cron,
        keyword=keyword,
        content_type=content_type,
        client=client,
    )

    print(f"\nScheduled job successfully.")
    jobs = manager.list_scheduled_jobs()
    for job in jobs:
        if keyword in job["name"]:
            print(f"  {job['name']}")
            print(f"  Next Run: {job['next_run']}")

    manager.shutdown()


@app.command("init")
def init_schedule():
    """Generate an example schedule configuration file"""
    example_config = {
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
            {
                "keyword": "犬の飼い方",
                "content_type": "youtube",
                "cron": "0 15 * * 5",  # Every Friday at 3:00 PM
                "job_id": "weekly_youtube_dog",
            },
        ]
    }

    filename = "automation_schedule.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(example_config, f, indent=2, ensure_ascii=False)

    print(f"Created example schedule file: {filename}")
    print(f"\nEdit the file and run: automation start --schedule {filename}")


if __name__ == "__main__":
    app()
