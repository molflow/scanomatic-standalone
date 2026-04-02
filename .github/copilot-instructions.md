# Copilot Instructions for This Repository

## Environment Overview
- Repository: `scanomatic-standalone`
- Primary runtime: Python (backend) with JavaScript tooling for frontend tests/build.
- Typical development environment: Linux dev container.
- Docker Compose is used for local app startup in normal workflows.

## Project Layout (High Level)
- `scanomatic/`: Main Python package.
- `tests/`: Unit, integration, and system tests.
- `.github/workflows/`: CI definitions.
- `scripts/`: Entrypoints and helper scripts.

## Validation Commands
- Backend test and quality environments are run through `tox`.
- Common environments: `tox -e lint`, `tox -e mypy`, `tox -e unit`, `tox -e integration`, `tox -e system`.
- Frontend tests use Karma (`karma.conf.js`), lint uses ESLint.
- For incremental type checks on modified files: `./typecheck-changed.sh`.

## Runtime Notes
- App startup is commonly done with Docker Compose (`docker-compose up -d`).
- Some system/integration flows may run local services inside the container when Docker daemon access is unavailable.

## Coding Guidance
- Prefer minimal, targeted changes that match existing style.
- Keep edits scoped; avoid unrelated refactors.
- When changing behavior, update or add tests close to the affected area.
