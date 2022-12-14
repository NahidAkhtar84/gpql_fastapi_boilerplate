"""all forenkey field added in model

Revision ID: 581b95d4610c
Revises: c5f616d5916a
Create Date: 2022-05-13 09:15:31.287035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '581b95d4610c'
down_revision = 'c5f616d5916a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cities', sa.Column('country_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'cities', 'countries', ['country_id'], ['id'])
    op.add_column('menus', sa.Column('module_id', sa.Integer(), nullable=True))
    op.add_column('menus', sa.Column('parent_menu', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'menus', 'modules', ['module_id'], ['id'])
    op.create_foreign_key(None, 'menus', 'menus', ['parent_menu'], ['id'])
    op.add_column('permissions', sa.Column('group_id', sa.Integer(), nullable=False))
    op.add_column('permissions', sa.Column('menu_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'permissions', 'menus', ['menu_id'], ['id'])
    op.create_foreign_key(None, 'permissions', 'groups', ['group_id'], ['id'])
    op.add_column('users', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('country_id', sa.Integer(), nullable=False))
    op.add_column('users', sa.Column('city_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('citizen_country_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'countries', ['citizen_country_id'], ['id'])
    op.create_foreign_key(None, 'users', 'organizations', ['organization_id'], ['id'])
    op.create_foreign_key(None, 'users', 'countries', ['country_id'], ['id'])
    op.create_foreign_key(None, 'users', 'cities', ['city_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'citizen_country_id')
    op.drop_column('users', 'city_id')
    op.drop_column('users', 'country_id')
    op.drop_column('users', 'organization_id')
    op.drop_constraint(None, 'permissions', type_='foreignkey')
    op.drop_constraint(None, 'permissions', type_='foreignkey')
    op.drop_column('permissions', 'menu_id')
    op.drop_column('permissions', 'group_id')
    op.drop_constraint(None, 'menus', type_='foreignkey')
    op.drop_constraint(None, 'menus', type_='foreignkey')
    op.drop_column('menus', 'parent_menu')
    op.drop_column('menus', 'module_id')
    op.drop_constraint(None, 'cities', type_='foreignkey')
    op.drop_column('cities', 'country_id')
    # ### end Alembic commands ###
