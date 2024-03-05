from nonebot import require
from tortoise import fields
from tortoise.models import Model

require("nonebot_plugin_tortoise_orm")
from nonebot_plugin_tortoise_orm import add_model

add_model("nonebot_plugin_lolmatch.model")


class SubTournament(Model):
    tournament = fields.IntField(pk=True)
    group_id = fields.JSONField()

    class Mate:
        table = "sub_tournament"
