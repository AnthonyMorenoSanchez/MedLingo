from pathlib import Path
from alembic import op
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    sql = (Path(__file__).resolve().parents[2] / "app/models/user.sql").read_text()
    for statement in sql.split(";"):
        if statement.strip():
            op.get_bind().exec_driver_sql(statement)

def downgrade():
    for table in ["session_items", "daily_stats", "banks", "runtime_log", "attempts", "sessions", "item_stats", "question_items", "profiles"]:
        op.drop_table(table)
