from nonebot_plugin_orm import Model
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class SubTournament(Model):
    tournament: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[list] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
