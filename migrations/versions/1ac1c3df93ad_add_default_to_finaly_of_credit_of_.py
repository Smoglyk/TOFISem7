"""add default to finaly of credit of credit migration

Revision ID: 1ac1c3df93ad
Revises: 5428d614ee25
Create Date: 2023-12-14 03:23:58.576557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ac1c3df93ad'
down_revision: Union[str, None] = '5428d614ee25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
