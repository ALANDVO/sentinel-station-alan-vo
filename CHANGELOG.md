# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [1.1.0] - 2026-10-29

### Added
- GET `/api/v1/skills/categories` endpoint returning all unique skill categories
- GET `/api/v1/skills/tags` endpoint returning all unique skill tags
- Frontend API client methods `getCategories()` and `getTags()`
- Dynamic category dropdown in SkillsDashboard populated from API

### Changed
- Reordered skills API routes to fix path parameter collision (specific routes before `/skills/{skill_id}`)
- Frontend SkillsDashboard now fetches categories dynamically instead of hardcoded list
- Updated frontend tests with mocks for skills list and categories endpoints

### Fixed
- Route ordering issue where `/skills/categories` and `/skills/tags` were incorrectly matched by `/skills/{skill_id}`

