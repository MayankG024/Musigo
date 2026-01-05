"""${message}"""

revision = '${up_revision}'
% if down_revision is None:
down_revision = None
% else:
down_revision = ${repr(down_revision)}
% endif
% if branch_labels is None:
branch_labels = None
% else:
branch_labels = ${repr(branch_labels)}
% endif
% if depends_on is None:
depends_on = None
% else:
depends_on = ${repr(depends_on)}
% endif

from alembic import op
import sqlalchemy as sa


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
