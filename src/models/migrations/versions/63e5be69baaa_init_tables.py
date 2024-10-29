"""init tables

Revision ID: 63e5be69baaa
Revises: aa469d6bc33f
Create Date: 2024-03-28 17:30:36.861316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63e5be69baaa'
down_revision: Union[str, None] = 'aa469d6bc33f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('companies',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('inn', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('created_by', sa.Text(), nullable=False),
    sa.Column('updated_by', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__companies')),
    sa.UniqueConstraint('id', name=op.f('uq__companies__id')),
    schema='catalog'
    )
    op.create_index(op.f('ix__companies__inn'), 'companies', ['inn'], unique=True, schema='catalog')
    op.create_index(op.f('ix__companies__name'), 'companies', ['name'], unique=False, schema='catalog')
    op.create_table('company_types',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('label', sa.String(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__company_types')),
    sa.UniqueConstraint('id', name=op.f('uq__company_types__id')),
    schema='catalog'
    )
    op.create_table('users',
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_blocked', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('email_verified', sa.Boolean(), nullable=False),
    sa.Column('email_verified_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__users')),
    sa.UniqueConstraint('email', name=op.f('uq__users__email')),
    sa.UniqueConstraint('id', name=op.f('uq__users__id')),
    schema='catalog'
    )
    op.create_index(op.f('ix__users__username'), 'users', ['username'], unique=True, schema='catalog')
    op.create_table('company_branch',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('timezone', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('city_id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('created_by', sa.Text(), nullable=False),
    sa.Column('updated_by', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['catalog.companies.id'], name=op.f('fk__company_branch__company_id__companies')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__company_branch')),
    sa.UniqueConstraint('id', name=op.f('uq__company_branch__id')),
    schema='catalog'
    )
    op.create_index(op.f('ix__company_branch__name'), 'company_branch', ['name'], unique=False, schema='catalog')
    op.create_table('company_company_types',
    sa.Column('company_type_id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['catalog.companies.id'], name=op.f('fk__company_company_types__company_id__companies')),
    sa.ForeignKeyConstraint(['company_type_id'], ['catalog.company_types.id'], name=op.f('fk__company_company_types__company_type_id__company_types')),
    sa.PrimaryKeyConstraint('company_type_id', 'company_id', name=op.f('pk__company_company_types')),
    schema='catalog'
    )
    op.create_table('profiles',
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('patronymic', sa.String(), nullable=True),
    sa.Column('birth_day', sa.Date(), nullable=True),
    sa.Column('timezone', sa.String(), nullable=True),
    sa.Column('city_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['catalog.users.id'], name=op.f('fk__profiles__user_id__users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__profiles')),
    sa.UniqueConstraint('id', name=op.f('uq__profiles__id')),
    sa.UniqueConstraint('user_id', name='_profile_user_id_uc'),
    schema='catalog'
    )
    op.create_table('user_social_account',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('social_id', sa.String(), nullable=False),
    sa.Column('social_name', sa.String(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['catalog.users.id'], name=op.f('fk__user_social_account__user_id__users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__user_social_account')),
    sa.UniqueConstraint('id', name=op.f('uq__user_social_account__id')),
    sa.UniqueConstraint('social_id', 'social_name', name='_social_id_social_name_uc'),
    schema='catalog'
    )
    op.create_table('users_companies',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['catalog.companies.id'], name=op.f('fk__users_companies__company_id__companies')),
    sa.ForeignKeyConstraint(['user_id'], ['catalog.users.id'], name=op.f('fk__users_companies__user_id__users')),
    sa.PrimaryKeyConstraint('user_id', 'company_id', name=op.f('pk__users_companies')),
    schema='catalog'
    )
    op.create_table('users_sign_in',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('user_agent', sa.String(), nullable=False),
    sa.Column('user_platform', sa.String(), nullable=False),
    sa.Column('user_device_type', sa.String(), nullable=False),
    sa.Column('logined_at', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['catalog.users.id'], name=op.f('fk__users_sign_in__user_id__users')),
    sa.PrimaryKeyConstraint('id', 'user_device_type', name=op.f('pk__users_sign_in')),
    schema='catalog',
    postgresql_partition_by='LIST (user_device_type)'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_sign_in', schema='catalog')
    op.drop_table('users_companies', schema='catalog')
    op.drop_table('user_social_account', schema='catalog')
    op.drop_table('profiles', schema='catalog')
    op.drop_table('company_company_types', schema='catalog')
    op.drop_index(op.f('ix__company_branch__name'), table_name='company_branch', schema='catalog')
    op.drop_table('company_branch', schema='catalog')
    op.drop_index(op.f('ix__users__username'), table_name='users', schema='catalog')
    op.drop_table('users', schema='catalog')
    op.drop_table('company_types', schema='catalog')
    op.drop_index(op.f('ix__companies__name'), table_name='companies', schema='catalog')
    op.drop_index(op.f('ix__companies__inn'), table_name='companies', schema='catalog')
    op.drop_table('companies', schema='catalog')
    # ### end Alembic commands ###