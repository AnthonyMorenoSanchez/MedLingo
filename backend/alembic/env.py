from alembic import context
from app.config import Settings
from app.db import engine
eng = engine(context.config.attributes.get("database_path", Settings().path("user_db")))
with eng.connect() as connection:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
eng.dispose()
