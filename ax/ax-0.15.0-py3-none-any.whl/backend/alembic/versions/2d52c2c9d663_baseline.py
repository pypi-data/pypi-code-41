"""baseline

Revision ID: 2d52c2c9d663
Revises: 
Create Date: 2019-03-11 20:31:54.259802

"""
from alembic import op
import sqlalchemy as sa

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0, parentdir2)

import ax.backend.model



# revision identifiers, used by Alembic.
revision = '2d52c2c9d663'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
