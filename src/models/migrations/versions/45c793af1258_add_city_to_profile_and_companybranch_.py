"""add city to Profile and CompanyBranch models

Revision ID: 45c793af1258
Revises: 170a479a518b
Create Date: 2024-04-10 01:03:22.250924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45c793af1258'
down_revision: Union[str, None] = '170a479a518b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cities',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('timezone', sa.String(), nullable=True),
    sa.Column('fias_id', sa.UUID(), nullable=True),
    sa.Column('kladr_id', sa.String(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__cities')),
    sa.UniqueConstraint('fias_id', name=op.f('uq__cities__fias_id')),
    sa.UniqueConstraint('id', name=op.f('uq__cities__id')),
    sa.UniqueConstraint('kladr_id', name=op.f('uq__cities__kladr_id')),
    schema='catalog'
    )
    op.create_index(op.f('ix__cities__name'), 'cities', ['name'], unique=False, schema='catalog')
    op.add_column('company_branch', sa.Column('city_id', sa.UUID(), nullable=False), schema='catalog')
    op.create_foreign_key(op.f('fk__company_branch__city_id__cities'), 'company_branch', 'cities', ['city_id'], ['id'], source_schema='catalog', referent_schema='catalog')
    op.add_column('profiles', sa.Column('city_id', sa.UUID(), nullable=False), schema='catalog')
    op.create_foreign_key(op.f('fk__profiles__city_id__cities'), 'profiles', 'cities', ['city_id'], ['id'], source_schema='catalog', referent_schema='catalog')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk__profiles__city_id__cities'), 'profiles', schema='catalog', type_='foreignkey')
    op.drop_column('profiles', 'city_id', schema='catalog')
    op.drop_constraint(op.f('fk__company_branch__city_id__cities'), 'company_branch', schema='catalog', type_='foreignkey')
    op.drop_column('company_branch', 'city_id', schema='catalog')
    op.drop_index(op.f('ix__cities__name'), table_name='cities', schema='catalog')
    op.drop_table('cities', schema='catalog')
    # ### end Alembic commands ###
