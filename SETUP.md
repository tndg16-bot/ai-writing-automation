# AI Writing Automation - Setup Guide

## Phase 10: Web UI + Analysis + Automation

## Current Status

Phase 10 has been implemented with:
- ✅ FastAPI Backend (api/)
- ✅ Next.js 14 Frontend (frontend/)
- ✅ SEO Analyzer
- ✅ Automation Module (automation/)
- ✅ Tests

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/ndg16-bot/ai-writing-automation.git
cd ai-writing-automation
```

### 2. Backend Setup

```bash
# Install dependencies
cd api
pip install -e .
# Or:
pip install fastapi uvicorn websockets apscheduler

# Run server
cd api
python main.py
# Or:
uvicorn api.main:app --host 0.0.0 --port 8000
```

API will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 3. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Run development server
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

### 4. Environment Setup

Create `.env` in project root:

```bash
# Required for OpenAI API
OPENAI_API_KEY=sk-proj-xxx

# Optional for Google Docs
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=...

# Optional for Midjourney (if using)
DISCORD_BOT_TOKEN=...
DISCORD_SERVER_ID=...
MIDJOURNEY_CHANNEL_ID=...
```

## API Usage

### Content Generation

Start Generation:
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"keyword": "AI副業", "content_type": "blog", "client": "default"}'
```

Response:
```json
{
  "task_id": "uuid"
}
```

Get Progress:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/generate/ws/{task_id}');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Progress:', message);
});
});
```

Get Result:
```bash
curl http://localhost:8000/api/generate/{task_id}
```

### History & Stats

List Generations:
```bash
curl http://localhost:8000/api/history
curl "http://localhost:8000/api/history?keyword=test&limit=10"
```

Get Details:
```bash
curl http://localhost:8000/api/history/1
```

Statistics:
```bash
curl http://localhost:8000/api/stats
curl "http://localhost:8000/api/stats/content-type"
```

### SEO Analysis

```bash
curl -X POST http://localhost:8000/api/analyze/seo \
  -H "Content-Type: application/json" \
  -d '{"keyword": "AI", "markdown_content": "# AI\n\n## Start..."}'
```

## Automation

Generate Schedule File (automation_schedule.json):

```json
{
  "schedules": [
    {
      "keyword": "AI副業",
      "content_type": "blog",
      "cron": "0 9 * * 1",
      "job_id": "weekly_blog_ai"
    },
    {
      "keyword": "投資信託",
      "content_type": "blog",
      "cron": "0 10 * * 2",
      "job_id": "weekly_investment"
    }
  ]
}
```

Run Scheduler:
```bash
python automation/cli.py init
python automation/cli.py start --schedule automation_schedule.json
```

List Jobs:
```bash
python automation/cli.py list
```

Remove Job:
```bash
python automation/cli.py remove --id job_id
```

Batch Generation:

```bash
python automation/cli.py batch --keywords keywords.txt --type blog
```

## Architecture

```
ai-writing-automation/
├── api/                      # FastAPI Backend
│   ├── main.py
│   ├── models.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── tests/
│   │   └── pyproject.toml
│
├── frontend/                 # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx       # Dashboard
│   │   ├── generate/       # Generate Form
│   │   └── progress/       # Progress Page
│   ├── lib/
│   │   └── hooks/
│   │   └── package.json
│
├── automation/              # Automation
│   ├── manager.py
│   ├── cli.py
│   └── requirements.txt
│
├── src/ai_writing/
│   ├── core/
│   │   ├── config.py
│   │   ├── context.py
│   │   ├── history_manager.py
│   │   ├── database.py
│   │   └── seo_analyzer.py  # NEW
│   ├── pipeline/
│   ├── stages/
│   ├── services/
│   └── utils/
```

## Running the Application

### Development Mode (Both Backend & Frontend)

Terminal 1:
```bash
# Backend
cd api && python main.py

# Frontend (new terminal)
cd frontend && npm run dev
```

### Production Mode

Backend:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Frontend:
```bash
npm run build
npm start
```

## Troubleshooting

### API Not Responding
- Check backend is running: `curl http://localhost:8000/health`
- Check `.env` has correct API keys
- Check port 8000 is available: `netstat -ano | findstr :8000`

### Frontend Won't Connect to API
- Check backend is running first
- Check CORS is enabled (it is)
- Check WebSocket URL matches backend endpoint

### Database Locked
```bash
# Remove lock file
rm -f data/history.db-shm data/history.db-journal
rm -f data/history.db data/history.db-wal
```

### Import Errors
```bash
# Reinstall in editable mode
cd api && pip install -e .
```
