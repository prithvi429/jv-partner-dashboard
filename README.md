## JV Partner Dashboard

An end-to-end toolkit for discovering partner technologies, mapping stakeholders, running outreach campaigns, and scheduling JV partnership meetings.

This project pairs a small FastAPI backend with a Streamlit frontend and a lightweight SQLAlchemy data layer. It's designed to help business development teams manage partner discovery, outreach, and meeting workflows.

## Key features

- Centralized data model for Products, Companies, Stakeholders, Outreaches, Meetings and Deals
- FastAPI REST endpoints for integrations and automation
- Streamlit dashboard for quick human-in-the-loop interactions
- Pluggable service stubs for Gmail, Hunter, Calendly, LinkedIn, and OpenAI
- Alembic migrations to version and apply schema changes

## Quick start (local)

1. Create and activate a virtual environment (recommended):

	Windows (PowerShell):

	```powershell
	python -m venv .venv; .\.venv\Scripts\Activate.ps1
	```

2. Install dependencies:

	```powershell
	pip install -r requirements.txt
	```

3. Initialize the database (SQLite by default) and run migrations:

	```powershell
	alembic upgrade head
	```

4. Run the backend API (FastAPI):

	```powershell
	uvicorn backend:app --reload
	```

5. Run the Streamlit frontend:

	```powershell
	streamlit run app.py
	```

## Database & migrations — this is where it's important

Migration scripts live under `migrations/versions/` and are applied with Alembic. Migration files use the Alembic operations API, which is why the statement

```
from alembic import op
```

appears at the top of many migration files. That import provides the `op` helper used to create and drop tables, add indexes, and run other schema operations. If `from alembic import op` fails, it usually means:

- Alembic is not installed in your active environment (install with `pip install alembic`)
- The environment's Python path is different from the one you used to run Alembic/pytest
- There's a syntax or naming problem in the migration file itself

If you see an import error referencing `alembic`, first confirm your virtual environment is active and `alembic` is present. Then run the failing migration or tests again to capture the traceback. For migrations added by this project, see:

- `migrations/versions/0001_initial_migration_create_jv_tables_placeholder.py`

The migration creates enums and the core tables (`products`, `companies`, `stakeholders`, `outreaches`, `meetings`, `deals`) used by the app.

## Project structure

Top-level layout (important files and folders):

- `app.py` — Streamlit frontend
- `backend.py` — FastAPI backend (REST endpoints)
- `models.py` — SQLAlchemy models
- `database.py` — DB engine + session helpers
- `utils.py` — helpers for third-party APIs and utilities
- `services/` — thin wrappers around 3rd-party APIs (Hunter, Gmail, Calendly, OpenAI, LinkedIn)
- `routers/` — FastAPI routers organized by domain (deals, outreaches, meetings, analytics)
- `migrations/` — Alembic migrations
- `tests/` — unit and integration tests

## Development notes

- Keep your `.env` file (API keys, DB URL) out of version control.
- Use Alembic for schema changes instead of hand-editing the database schema.
- Add unit tests in `tests/` for new models, utils, and API routes.

## Contributing

If you'd like to contribute, please open an issue describing the change and submit a PR with tests. Run `pytest` before opening a PR to ensure no regressions.

## License

This repository includes a `LICENSE` file — follow its terms for reuse and contributions.

---

If you'd like, I can also add a small troubleshooting section that runs the common commands and checks for `alembic` import issues on Windows PowerShell.
