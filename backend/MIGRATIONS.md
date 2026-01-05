# Database migrations (Alembic)

## Prereqs
- DATABASE_URL must point to your DB (Postgres default in docker-compose):
  - postgresql+asyncpg://musicuser:musicpass@postgres:5432/musicdb
- Alembic configured in `alembic.ini` and `alembic/` directory.

## Common commands
- Autogenerate a new migration from models:
  ```bash
  alembic revision --autogenerate -m "init schema"
  ```
- Apply migrations:
  ```bash
  alembic upgrade head
  ```
- Downgrade one step:
  ```bash
  alembic downgrade -1
  ```

## Notes
- For async drivers, Alembic still runs in sync; URL string is fine.
- Ensure containers are up (`postgres`) before running migrations.
- Inside Docker, you can run migrations with a one-off exec into backend once alembic is installed.
