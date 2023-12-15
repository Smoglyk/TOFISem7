"""add default to finaly of credit of credit migration

Revision ID: 9c7dd161ca45
Revises: 15cd878ed3de
Create Date: 2023-12-14 09:36:50.754607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c7dd161ca45'
down_revision: Union[str, None] = '15cd878ed3de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('credit', sa.Column('borrower_id', sa.Integer(), nullable=True))
    op.drop_constraint('credit_account_id_fkey', 'credit', type_='foreignkey')
    op.create_foreign_key(None, 'credit', 'account', ['borrower_id'], ['id'])
    op.drop_column('credit', 'account_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('credit', sa.Column('account_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'credit', type_='foreignkey')
    op.create_foreign_key('credit_account_id_fkey', 'credit', 'account', ['account_id'], ['id'])
    op.drop_column('credit', 'borrower_id')
    # ### end Alembic commands ###
