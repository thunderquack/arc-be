"""permissions for documents

Revision ID: dc8890adbfa0
Revises: e1dc65f870ae
Create Date: 2024-07-06 18:18:48.796910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc8890adbfa0'
down_revision: Union[str, None] = 'e1dc65f870ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document_permissions',
    sa.Column('document_id', sa.UUID(), nullable=False),
    sa.Column('permission_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
    sa.PrimaryKeyConstraint('document_id', 'permission_id')
    )
    op.drop_table('document_roles')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document_roles',
    sa.Column('document_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('role_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='document_roles_document_id_fkey'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='document_roles_role_id_fkey'),
    sa.PrimaryKeyConstraint('document_id', 'role_id', name='document_roles_pkey')
    )
    op.drop_table('document_permissions')
    # ### end Alembic commands ###