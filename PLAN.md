# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-skeleton

## Roadmap

### core-skeleton — Core FastAPI/React skeleton with health endpoint

Status: done

Acceptance:
- FastAPI backend starts and responds to GET /health
- React + Vite frontend builds and serves
- Docker compose brings up both services
- Backend tests pass (pytest)
- Frontend typecheck and tests pass (vitest)

Implementation: `backend/app/main.py`, `backend/app/api/health.py`, `backend/app/core/config.py`, `backend/app/api/deps.py`, `backend/requirements.txt`, `backend/tests/test_health.py`, `frontend/package.json`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`, `frontend/tests/App.test.tsx`, `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yaml`, `.env.example`, `README.md`, `LICENSE`, `CHANGELOG.md`, `portfolio.json`

Tests: `backend/tests/test_health.py`, `frontend/tests/App.test.tsx`

### catalog-discovery — Agentic Skills Catalog discovery and search

Status: done

Acceptance:
- Backend loads skills from local JSON catalog
- GET /api/v1/skills supports pagination, filtering by category/tag
- Frontend dashboard displays searchable, paginated skill list
- Skill detail view shows description, repo, install command

Implementation: `backend/app/models/skill.py`, `backend/app/services/catalog.py`, `backend/app/api/skills.py`, `backend/app/services/ingest.py`, `backend/tests/test_skills.py`, `data/skills.sample.json`, `frontend/src/components/SkillsDashboard.tsx`, `frontend/src/components/SkillCard.tsx`

Tests: `backend/tests/test_skills.py`

### stack-validation — Stack validation and planning workflow

Status: done

Acceptance:
- POST /api/v1/validate accepts skill list, returns compatibility matrix
- Frontend validates a skill stack, shows conflicts/missing deps
- POST /api/v1/plan generates execution plan with parallel groups
- Export validated plan as JSON/Markdown

Implementation: `backend/app/services/validation.py`, `backend/app/services/planning.py`, `backend/app/api/planning.py`, `backend/tests/test_validation_planning.py`, `frontend/src/components/ValidationPage.tsx`

Tests: `backend/tests/test_validation_planning.py`

### oidc-auth — OIDC/Keycloak authentication

Status: planned

Acceptance:
- Keycloak realm import provided
- Backend validates JWT tokens on all data endpoints
- Frontend SPA PKCE login flow with logout
- Role-based access (viewer/operator/admin)

