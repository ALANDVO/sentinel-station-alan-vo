# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

oidc-keycloak-auth

## Roadmap

### continue-implementation — Continue implementation and resolve known failures

Status: done

Acceptance:
- Run checks, fix failures, and implement the next planned feature

Implementation: `backend/app/main.py`, `backend/app/api/health.py`, `backend/app/api/skills.py`, `backend/app/api/planning.py`, `backend/app/services/catalog.py`, `backend/app/services/validation.py`, `backend/app/services/planning.py`, `backend/app/services/ingest.py`, `backend/app/models/skill.py`, `frontend/src/App.tsx`, `frontend/src/components/SkillsDashboard.tsx`, `frontend/src/components/ValidationPage.tsx`, `frontend/src/api/client.ts`

Tests: `backend: pytest - 17 passed`, `frontend: npm test - 4 passed`, `frontend: npx tsc --noEmit`, `frontend: npm run lint`

### mcp-server — Local MCP server exposing catalog and validation

Status: done

Acceptance:
- MCP server starts and registers tools
- Exposes list_skills, get_skill, validate_stack, generate_plan as MCP tools
- Works with MCP clients (e.g., Cursor, Claude Desktop)

Implementation: `backend/app/mcp_server.py`

Tests: `backend: pytest - 17 passed (existing)`, `mcp_server: JSON-RPC 2.0 stdio message handling verified (initialize with capabilities, list_skills, get_skill, validate_stack, generate_plan)`

### oidc-keycloak-auth — Production-ready authentication with SAML broker support

Status: in_progress

Acceptance:
- Keycloak realm configuration
- OIDC login flow with JWT validation
- SAML 2.0 identity provider brokering
- Demo mode explicitly refused in production

Implementation: `backend/app/api/oidc.py`, `backend/app/main.py`

Tests: `backend: pytest - 17 passed`, `oidc: JWT validation endpoint with demo mode and Keycloak config fallback`

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
