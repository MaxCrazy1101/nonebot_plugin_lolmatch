"""init db

迁移 ID: 54eff20f9cc8
父迁移:
创建时间: 2024-03-07 18:30:58.375531

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "54eff20f9cc8"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = ("nonebot_plugin_lolmatch",)
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "nonebot_plugin_lolmatch_subtournament",
        sa.Column("tournament", sa.Integer(), nullable=False),
        sa.Column(
            "group_id",
            sa.JSON().with_variant(postgresql.JSONB(), "postgresql"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "tournament", name=op.f("pk_nonebot_plugin_lolmatch_subtournament")
        ),
    )
    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("nonebot_plugin_lolmatch_subtournament")
    # ### end Alembic commands ###
