# AI Writing Automation API

## Quick Start

### 1. Prerequisites

Ensure you have Python 3.11+ installed:
```bash
python --version
```

Install dependencies:
```bash
cd api
pip install -e .
```

### 2. Environment Setup

Create `.env` file in the project root:
```bash
cp .env.example .env
```

Required environment variables:
```bash
# OpenAI API (required)
OPENAI_API_KEY=sk-...

# Google Cloud (optional, for Google Docs)
GOOGLE_API_KEY=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=...

# Discord (optional, for Midjourney)
DISCORD_BOT_TOKEN=...
DISCORD_SERVER_ID=...
MIDJOURNEY_CHANNEL_ID=...

# Canva (optional, for Canva)
CANVA_API_KEY=...
CANVA_TEMPLATE_ID=...
```

### 3. Start the API Server

Development mode (with auto-reload):
```bash
cd api
python main.py
```

Production mode:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Content Generation
- `POST /api/generate` - Start content generation task
  - Request body: `{"keyword": "...", "content_type": "blog|youtube|yukkuri", "client": "default"}`
  - Returns: `{"task_id": "uuid"}`
  
- `GET /api/generate/{task_id}` - Get task result
- `WS /api/generate/ws/{task_id}` - WebSocket for real-time progress

### History & Stats
- `GET /api/history` - List generation history
- `GET /api/history/{id}` - Get generation details
- `DELETE /api/history/{id}` - Delete generation
- `GET /api/history/{id}/markdown` - Export as Markdown

### Statistics
- `GET /api/stats` - Overall statistics
- `GET /api/stats/content-type` - By content type
- `GET /api/stats/image-provider` - By image provider

### Analysis
- `POST /api/analyze/seo` - SEO analysis
  - Request body: `{"keyword": "...", "markdown_content": "..."}`
  - Returns SEO score and recommendations

### Health
- `GET /health` - Health check
- `GET /` - API information

## WebSocket Progress Updates

Connect to `ws://localhost:8000/api/generate/ws/{task_id}` to receive real-time updates.

Message format:
```json
{
  "type": "progress",
  "task_id": "uuid",
  "stage": "SearchIntent",
  "stage_index": 1,
  "total_stages": 6,
  "status": "running"
}
```

## Authentication

Currently disabled. To enable API key authentication, update:
- `api/dependencies.py`: Uncomment and implement `verify_api_key` function
- Update route handlers to depend on `verify_api_key`

## Rate Limiting

Rate limits are handled in:
- OpenAI API: `tenacity` retry with exponential backoff
- LLM Cache: Reduces redundant API calls

## Development

### Run Tests

```bash
cd api
pytest tests/ -v
```

### Check LSP Errors

The project has some LSP warnings that don't affect runtime:
- APScheduler imports: Lazy-loaded, optional dependency
- API imports: Resolved at runtime
- Database type hints: Null-safe returns handled
