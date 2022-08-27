import asyncio
import datetime
from copy import copy

from nonebot.plugin import PluginMetadata, on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot, MessageSegment, \
    NetworkError
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import Union
from nonebot import require, get_bot, get_driver
from pydantic import BaseModel

from .data_source import LoLMatch, create_image
from .model import disconnect_database
from .template import match_brief_builder


class Config(BaseModel):
    custom: str = ""


__plugin_meta__ = PluginMetadata(
    name="LOLMatch",
    description="查询英雄联盟的联赛和比赛信息",
    usage="""
    主命令 lol 查看今日比赛信息
        附带命令 本周 查看本周比赛信息
        附带命令 详情 [matchID] 查询指定比赛详细信息
        附带命令 订阅 [tournamentID] 订阅相关系列赛 每晚检查当日结果和第二天赛程
        附带命令 取消订阅 [tournamentID] 订阅相关系列赛 每晚检查当日结果和第二天赛程
        附带命令 联赛 查看所有即将进行或正在进行的赛事以获取 [tournamentID]
""",
    config=Config,
    extra={"author": "Alex Newton"},
)

scheduler = require("nonebot_plugin_apscheduler").scheduler

lol_today = on_command("lol", aliases={"LOL", "Lol"}, priority=5)
driver = get_driver()
driver.on_startup(LoLMatch.creat_table)
driver.on_shutdown(disconnect_database)


@lol_today.handle()
async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    msg: str = args.extract_plain_text().strip()
    if "本周" in msg:
        await lol_today.finish(await LoLMatch.show_week_matches())
    elif "查看订阅" in msg:
        try:
            await lol_today.finish(
                await LoLMatch.show_subbed_tournament(event.group_id)
            )
        except ValueError:
            await lol_today.finish("检查输入联赛ID应为数字")
    elif "详情" in msg:
        index_msg = msg.replace("详情", "").strip()
        try:
            index = int(index_msg)
            await lol_today.finish(await LoLMatch.show_match_details(matcher, index))
        except ValueError:
            await lol_today.finish("检查输入比赛ID应为数字")
    elif "取消订阅" in msg:
        sub_id = msg.replace("取消订阅", '').strip()
        await lol_today.finish(
            await LoLMatch.cancel_tournament_group(int(sub_id), event.group_id))
    elif "订阅" in msg:
        sub_id = msg.replace("订阅", "").strip()
        await lol_today.finish(
            await LoLMatch.sub_tournament_group(int(sub_id), event.group_id)
        )
    elif "联赛" in msg:
        await lol_today.finish(await LoLMatch.show_all_tournaments())
    else:
        await lol_today.finish(await LoLMatch.show_all_today_matches())


# 每日23点自动检查比赛
@scheduler.scheduled_job("cron", hour=23, jitter=180, id="lol_check_match")
async def match_checker():
    try:
        bot: Bot = get_bot()  # 当未连接bot时返回
    except ValueError:
        return
    subbed = await LoLMatch.get_sub_tournament()  # 获得所有订阅的tournament
    sub_dict: dict = {}
    for sub in subbed:
        sub_dict[sub.tournament] = sub.group_id
    match_data = await LoLMatch.get_week_matches()
    sub_tournament = sub_dict.keys()

    msg_container = {}
    # 获取今日赛果
    today_matches: Union[list, dict] = match_data[
        datetime.datetime.now().strftime("%Y.%m.%d")
    ]
    if isinstance(today_matches, list):
        pass  # 今日无比赛
    else:
        today_matches: dict = today_matches["info"]
        for tournamentID, tournament_matches in today_matches.items():
            if int(tournamentID) not in sub_tournament:
                continue  # 如果比赛不在订阅列表中不做处理
            match_result = (
                    f"""<tr><th colspan="2" align="center">联赛ID: {tournamentID}&nbsp;&nbsp;&nbsp;&nbsp;{tournament_matches['tournamentinfo']['short_name']}</th></tr>"""
                    + "".join(
                f"""<tr><td>{match['match_id']}</td><td>{match['team_a_short_name']} {match['team_a_win']} <font color=red>VS</font> {match['team_b_win']} {match['team_b_short_name']}</td></tr>"""
                for match in tournament_matches["list"])
            )
            for group_id in sub_dict[int(tournamentID)]:
                tmp = msg_container.get(group_id, {"j": "", "m": ""})
                tmp["j"] += match_result
                msg_container[group_id] = tmp

    # 检查已结束赛事 脱离数据库
    available_tour: list = await LoLMatch.get_available_tournament()
    ava_keys = []
    for tour in available_tour:
        ava_keys.append(int(tour["tournamentID"]))
    for tournamentID in sub_dict.keys():
        if tournamentID not in ava_keys:
            await LoLMatch.del_tournament(tournamentID)

    # 处理明日赛程
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    if tomorrow.strftime("%Y.%m.%d") not in match_data.keys():
        tomorrow_matches = (await LoLMatch.get_week_matches(str(tomorrow.date())))[
            tomorrow.strftime("%Y.%m.%d")
        ]
    else:
        tomorrow_matches = match_data[tomorrow.strftime("%Y.%m.%d")]
    if isinstance(tomorrow_matches, list):
        pass  # 明日无比赛
    else:
        tomorrow_matches: dict = tomorrow_matches["info"]
        for tournamentID, tournament_matches in tomorrow_matches.items():
            if int(tournamentID) not in sub_tournament:
                continue  # 如果比赛不在订阅列表中不做处理
            match_result = (
                    f"""<tr><th colspan="2" align="center">联赛ID: {tournamentID}&nbsp;&nbsp;&nbsp;&nbsp;{tournament_matches['tournamentinfo']['short_name']}</th></tr>"""
                    + "".join(
                f"""<tr><td>{match['start_time']}</td><td>{match['team_a_short_name']} <font color=red>VS</font> {match['team_b_short_name']}</td></tr>"""
                for match in tournament_matches["list"])
            )
            for group_id in sub_dict[int(tournamentID)]:
                tmp = msg_container.get(group_id, {"j": "", "m": ""})
                tmp["m"] += match_result
                msg_container[group_id] = tmp

    for (group_id, msg) in msg_container.items():
        match_result = await create_image(match_brief_builder(msg), locator="div")
        try:
            await bot.send_group_msg(group_id=group_id, message=MessageSegment.image(match_result))
        except NetworkError:
            logger.warning(
                f"{__plugin_meta__.name} 向群 {group_id} 发送 {match_result} 失败"
            )
        # 停1秒
        await  asyncio.sleep(1)
