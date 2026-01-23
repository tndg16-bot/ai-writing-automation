# Automation Module

## Overview
Provides scheduled content generation using APScheduler.

## Features
- Cron-based scheduling
- Batch generation from keyword lists
- Job management (list, remove)
- Configuration file support

## Usage

### Start Scheduler
```bash
python automation/cli.py start --schedule automation_schedule.json
```

### Run Single Generation
```bash
python automation/cli.py run --keyword "AI副業" --type blog
```

### Batch Generation
Create `keywords.txt`:
```
AI副業
投資信託
犬の飼い方
```

Run batch:
```bash
python automation/cli.py batch --keywords keywords.txt --type blog
```

### Generate Schedule File
```bash
python automation/cli.py init
```

### List Scheduled Jobs
```bash
python automation/cli.py list
```

### Remove Job
```bash
python automation/cli.py remove --id job_id
```

## Schedule File Format
```json
{
  "schedules": [
    {
      "keyword": "AI副業",
      "content_type": "blog",
      "cron": "0 9 * * 1",
      "job_id": "weekly_blog_ai"
    }
  ]
}
```

## Cron Expression Format
```
* * * * * *
│ │ │ │ │ │
│ │ │ │ │ └─── Day of week (0-6, 0=Sunday)
│ │ │ │ └───── Month (1-12)
│ │ │ └─────── Day of month (1-31)
│ │ └────────── Hour (0-23)
│ └───────────── Minute (0-59)
```

Examples:
- `0 9 * * *` - Daily at 9:00 AM
- `0 9 * * 1` - Every Monday at 9:00 AM
- `0 */4 * * *` - Every 4 hours
- `0 0 1 * *` - Monthly on 1st at midnight
