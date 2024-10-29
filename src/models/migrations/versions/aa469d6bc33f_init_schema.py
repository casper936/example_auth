"""init schema

Revision ID: aa469d6bc33f
Revises: 
Create Date: 2024-03-11 23:34:33.325043

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from src.core.config.pg_settings import DBSettings

db_settings = DBSettings()


# revision identifiers, used by Alembic.
revision: str = "aa469d6bc33f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {db_settings.db_schema}")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(f"DROP SCHEMA {db_settings.db_schema} CASCADE")
    # ### end Alembic commands ###
