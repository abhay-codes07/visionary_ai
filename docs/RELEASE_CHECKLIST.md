# Release Checklist

Use this checklist before tagging a production release.

## Build and CI

- [ ] GitHub Actions CI is green on `main`
- [ ] Backend tests pass locally (`npm run test:backend`)
- [ ] Frontend lint/tests pass locally (`npm run lint:frontend`, `npm run test:frontend`)

## Environment and Secrets

- [ ] `backend/.env` configured for target environment
- [ ] `frontend/.env.production` configured with public API/WS endpoints
- [ ] OpenAI credentials rotated and valid

## Runtime Validation

- [ ] Start stack: `npm run up`
- [ ] Run smoke checks: `npm run smoke`
- [ ] Verify `/api/v1/health` returns `ok`
- [ ] Verify `/api/v1/system/status` returns uptime + AI flags
- [ ] Verify `/api/v1/vision/capabilities` returns transport/model metadata

## Product UX Validation

- [ ] Homepage renders all required sections
- [ ] About, Contact, Blog pages load
- [ ] Agent Studio supports upload + analyze stream
- [ ] Live Agent Feed connects and streams WebSocket events

## Operational Readiness

- [ ] Deployment runbook reviewed: `docs/DEPLOYMENT_RUNBOOK.md`
- [ ] Rollback path validated on previous stable commit
- [ ] Observability/log routing configured in target infra

## Release

- [ ] Create release tag
- [ ] Publish release notes
- [ ] Monitor post-release smoke checks and error rates
