# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

frontend-lint-typescript-fix

## Roadmap

### frontend-lint-typescript-fix — Fix frontend linting and TypeScript type errors

Status: done

Acceptance:
- ESLint flat config works with TypeScript and React
- TypeScript compilation passes (npx tsc --noEmit)
- Frontend tests pass (npm test)

Implementation: `frontend/eslint.config.js`, `frontend/package.json`, `frontend/tests/App.test.tsx`

Tests: `frontend: npm run lint`, `frontend: npx tsc --noEmit`, `frontend: npm test`

### continue-implementation — Continue implementation and resolve known failures

Status: done

Acceptance:
- Run checks, fix failures, and implement the next planned feature

Implementation: `backend/app/main.py`, `backend/app/api/health.py`, `backend/app/api/skills.py`, `backend/app/api/planning.py`, `backend/app/services/catalog.py`, `backend/app/services/validation.py`, `backend/app/services/planning.py`, `backend/app/services/ingest.py`, `backend/app/models/skill.py`, `frontend/src/App.tsx`, `frontend/src/components/SkillsDashboard.tsx`, `frontend/src/components/ValidationPage.tsx`, `frontend/src/api/client.ts`

Tests: `backend: pytest - 17 passed`, `frontend: npm test - 4 passed`, `frontend: npx tsc --noEmit`, `frontend: npm run lint`

### mcp-server — Local MCP server exposing catalog and validation

Status: planned

Acceptance:
- MCP server starts and registers tools
- Exposes list_skills, get_skill, validate_stack, generate_plan as MCP tools
- Works with MCP clients (e.g., Cursor, Claude Desktop)

### oidc-keycloak-auth — Production-ready authentication with SAML broker support

Status: planned

Acceptance:
- Keycloak realm configuration
- OIDC login flow with JWT validation
- SAML 2.0 identity provider brokering
- Demo mode explicitly refused in production

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
