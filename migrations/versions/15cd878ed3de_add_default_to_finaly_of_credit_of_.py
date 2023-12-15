"""add default to finaly of credit of credit migration

Revision ID: 15cd878ed3de
Revises: 9222356490ac
Create Date: 2023-12-14 09:33:13.284086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15cd878ed3de'
down_revision: Union[str, None] = '9222356490ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('credit', sa.Column('account_id', sa.Integer(), nullable=True))
    op.drop_constraint('credit_borrower_id_fkey', 'credit', type_='foreignkey')
    op.create_foreign_key(None, 'credit', 'account', ['account_id'], ['id'])
    op.drop_column('credit', 'borrower_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('credit', sa.Column('borrower_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'credit', type_='foreignkey')
    op.create_foreign_key('credit_borrower_id_fkey', 'credit', 'account', ['borrower_id'], ['id'])
    op.drop_column('credit', 'account_id')
    # ### end Alembic commands ###