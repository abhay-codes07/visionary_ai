# Production Deployment Runbook

This runbook covers deploying Visionary Agent Protocol with Docker in a production-like environment.

## 1. Prerequisites

- Docker Engine 24+
- Docker Compose v2+
- Valid DNS + TLS termination for frontend and backend domains

## 2. Environment Files

Prepare:

- `backend/.env`
- `frontend/.env.production`

Backend minimum:

```env
APP_ENV=production
OPENAI_ENABLED=true
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
OPENAI_TIMEOUT_SECONDS=30
OPENAI_MAX_RETRIES=2
OPENAI_RETRY_BACKOFF_SECONDS=0.75
OPENAI_FALLBACK_TO_STUB=true
```

Frontend minimum:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.visionforge.ai
NEXT_PUBLIC_WS_URL=wss://api.visionforge.ai/api/v1/ws
```

## 3. Build Images

From `docker/`:

```bash
docker compose build --no-cache
```

## 4. Start Stack

```bash
docker compose up -d
```

## 5. Verify Health

- Backend health endpoint:
  - `GET /api/v1/health`
- Backend capabilities:
  - `GET /api/v1/vision/capabilities`
- Frontend:
  - Load homepage and verify Agent Studio + Live Agent Feed

Check compose health:

```bash
docker compose ps
```

## 6. Logs and Debug

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

## 7. Rolling Update Pattern

1. Pull latest source
2. Rebuild images
3. Restart stack with compose
4. Re-run health checks

## 8. Rollback

- Revert to previous git tag/commit
- Rebuild and redeploy compose stack
- Validate `/api/v1/health` and UI smoke paths

## 9. Post-Deploy Smoke Checklist

- REST analyze endpoint returns 200
- SSE analyze stream returns token chunks + `[DONE]`
- WebSocket `/api/v1/ws` connects and emits `connected`
- Pricing/About/Contact/Blog routes load from frontend
