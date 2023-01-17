"""booksinshop table

Revision ID: 821225bb30c9
Revises: da67dcd3cc3c
Create Date: 2022-05-22 19:37:59.819418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '821225bb30c9'
down_revision = 'da67dcd3cc3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('booksinshop',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shop_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('how_many', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('booksinshop')
    # ### end Alembic commands ###
