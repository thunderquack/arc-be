"""thumbnail data

Revision ID: 97cae2496046
Revises: f78d234925cf
Create Date: 2024-07-08 16:04:22.098933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97cae2496046'
down_revision: Union[str, None] = 'f78d234925cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pages', sa.Column('thumbnail_data', sa.LargeBinary(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pages', 'thumbnail_data')
    # ### end Alembic commands ###
