# Changelog

## 1.6.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.1 — work-in-progress checkpoint

MCP server added, exposing sentinel-station capabilities via JSON-RPC 2.0 over stdio.
- MCP server tool: `list_skills` — list all skills with category/tag filtering
- MCP server tool: `get_skill` — get a single skill by ID
- MCP server tool: `validate_stack` — validate compatibility of a skill stack
- MCP server tool: `generate_plan` — generate an execution plan from a validated skill stack
- Capability negotiation on `initialize` with server info
- Proper error handling for missing skills and unknown methods

Bug fixes:
- None (existing 17 backend tests and 4 frontend tests all pass)

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## [1.1.0] - 2026-11-05

### Added
- Fixed planning API endpoint dependencies (`/api/v1/plan` and `/api/v1/plan/export`) to properly inject database sessions
- Added `get_validation_engine` and `get_planning_engine` FastAPI dependencies
- Fixed missing import of `create_validation_engine` in planning service
- Catalog ingestion script now validates JSON structure before processing

### Changed
- Updated test fixture to clear skills table between tests for proper isolation
- Planning engine now correctly uses ValidationEngine (category conflicts as warnings, not errors)

### Fixed
- Planning endpoint returning 500 due to missing session dependency injection
- Export endpoint returning empty plans due to database state issues after test runs
- Unused import lint warnings in `app/services/ingest.py`

## [1.2.0] - 2026-11-10

### Added
- Frontend ESLint flat config (`frontend/eslint.config.js`) with TypeScript and React plugin support
- Frontend TypeScript type checking now passes (`npx tsc --noEmit`)
- `@testing-library/dom` dependency for proper test imports

### Changed
- Fixed test imports in `frontend/tests/App.test.tsx` to import `screen` and `waitFor` from `@testing-library/dom`
- Updated `frontend/package.json` with ESLint TypeScript dependencies: `@typescript-eslint/parser`, `@typescript-eslint/eslint-plugin`, `typescript-eslint`
- Updated PLAN.md with completed features and roadmap for MCP server and OIDC/Keycloak auth
- Updated feature-plan.json with current feature tracking

### Fixed
- ESLint parsing errors for TypeScript files (interface, type annotations)
- TypeScript compilation errors in test file (missing `screen`, `waitFor` exports)
- All frontend checks now pass: lint, type check, tests

## [1.0.0] - 2026-10-21

### Added
- Initial FastAPI backend skeleton with health check endpoint (`GET /api/v1/health`)
- React + TypeScript + Vite frontend with typed API client
- Docker Compose configuration for local development
- Backend pytest tests (health check, OpenAPI docs)
- Frontend vitest tests (loading, success, error states)
- CI workflow configuration (placeholder for future)

### Changed
- N/A

### Fixed
- N/A

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
