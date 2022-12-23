"""empty message

Revision ID: d51ecd1bb946
Revises: 
Create Date: 2022-12-22 10:19:37.722951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd51ecd1bb946'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=64), nullable=True),
    sa.Column('code', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_code'), 'role', ['code'], unique=True)
    op.create_index(op.f('ix_role_nombre'), 'role', ['nombre'], unique=True)
    op.create_table('room',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('roomName', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('servicio',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('servicioName', sa.String(length=64), nullable=False),
    sa.Column('servicioCosto', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('meeting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=False),
    sa.Column('roomId', sa.Integer(), nullable=False),
    sa.Column('doctorId', sa.Integer(), nullable=False),
    sa.Column('servicioId', sa.Integer(), nullable=False),
    sa.Column('bookerId', sa.Integer(), nullable=False),
    sa.Column('pacienteId', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('startTime', sa.Integer(), nullable=False),
    sa.Column('endTime', sa.Integer(), nullable=False),
    sa.Column('estatuspago', sa.String(), nullable=False),
    sa.Column('costo', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bookerId'], ['user.id'], ),
    sa.ForeignKeyConstraint(['doctorId'], ['user.id'], ),
    sa.ForeignKeyConstraint(['pacienteId'], ['user.id'], ),
    sa.ForeignKeyConstraint(['roomId'], ['room.id'], ),
    sa.ForeignKeyConstraint(['servicioId'], ['servicio.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('user_in_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_in_role')
    op.drop_table('meeting')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('servicio')
    op.drop_table('room')
    op.drop_index(op.f('ix_role_nombre'), table_name='role')
    op.drop_index(op.f('ix_role_code'), table_name='role')
    op.drop_table('role')
    # ### end Alembic commands ###
