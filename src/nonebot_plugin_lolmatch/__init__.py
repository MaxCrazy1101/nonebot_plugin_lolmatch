import datetime
from nonebot.plugin import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import GroupMessageEvent, Event, Bot
from nonebot.typing import Union, T_State
from nonebot import require, get_bot, get_driver
from .data_source import LoLMatch

__author__ = "Alex Newton"
__usage__ = """
    主命令 lol 查看今日比赛信息
        附带命令 本周 查看本周比赛信息
        附带命令 详情 [matchID] 查询指定比赛详细信息
        附带命令 订阅 [tournamentID] 订阅相关系列赛 每晚检查当日结果和第二天赛程
        附带命令 赛事 查看所有即将进行或正在进行的赛事
"""
__version__ = '0.1.0'
__plugin_name__ = "LOL比赛信息插件"
scheduler = require('nonebot_plugin_apscheduler').scheduler

lol_today = on_command('lol', aliases={'LOL', "Lol"}, priority=5)
driver = get_driver()
driver.on_startup(LoLMatch.creat_table)


@lol_today.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    msg: str = str(event.get_message()).strip()
    if '本周' in msg:
        await lol_today.finish(await LoLMatch.show_week_matches())
    elif '详情' in msg:
        index_msg = msg.replace('详情', '').strip()
        try:
            index = int(index_msg)
            await lol_today.finish(await LoLMatch.show_match_details(bot, event, index))
        except ValueError:
            await lol_today.finish('检查输入matchID应为数字')
    elif '订阅' in msg:
        sub_id = msg.replace('订阅', '').strip()
        await LoLMatch.sub_tournament_group(int(sub_id), event.group_id)
    elif '赛事' in msg:
        await lol_today.finish(await LoLMatch.show_all_tournaments())
    else:
        await lol_today.finish(await LoLMatch.show_today_matches())


# 每日23点自动检查比赛
@scheduler.scheduled_job('cron', hour=23, jitter=30, id='lol_check_match')
async def match_checker():
    try:
        bot: Bot = get_bot()  # 当未连接bot时返回
    except ValueError:
        return
    subed = await LoLMatch.get_sub_tournament()  # 获得所有订阅的tournament
    sub_dict: dict = {}
    for sub in subed:
        sub_dict[sub['tournament']] = sub['group_id']
    match_data = await LoLMatch.get_week_matches()
    sub_tournament = sub_dict.keys()
    # 获取今日赛果
    _msg = ""
    today_matches: Union[list, dict] = match_data[datetime.datetime.now().strftime("%Y.%m.%d")]
    if isinstance(today_matches, list):
        pass  # 今日无比赛
    else:
        _msg += "---今日赛果---\n"
        today_matches: dict = today_matches['info']
        for tournamentID, tournament_matches in today_matches.items():
            if int(tournamentID) not in sub_tournament:
                continue  # 如果比赛不在订阅列表中不做处理
            match_result = _msg + f"{tournament_matches['tournamentinfo']['short_name']}  ID:{tournamentID}\n" + LoLMatch.match_result_handle(
                tournament_matches['list'])
            for group_id in sub_dict[int(tournamentID)]:
                await bot.send_group_msg(group_id=group_id, message=match_result)

    # 处理明日赛程
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    if tomorrow.strftime("%Y.%m.%d") not in match_data.keys():
        tomorrow_matches = (await LoLMatch.get_week_matches(str(tomorrow.date())))[tomorrow.strftime("%Y.%m.%d")]
    else:
        tomorrow_matches = match_data[tomorrow.strftime("%Y.%m.%d")]
    if isinstance(tomorrow_matches, list):
        pass  # 明日无比赛
    else:
        _msg = "---明日赛程---\n"
        tomorrow_matches: dict = tomorrow_matches['info']
        for tournamentID, tournament_matches in tomorrow_matches.items():
            if int(tournamentID) not in sub_tournament:
                continue  # 如果比赛不在订阅列表中不做处理
            match_result = _msg + f"{tournament_matches['tournamentinfo']['short_name']}  ID:{tournamentID}\n" + LoLMatch.match_predict_handle(
                tournament_matches['list'])
            for group_id in sub_dict[int(tournamentID)]:
                await bot.send_group_msg(group_id=group_id, message=match_result)
    available_tour: list = await LoLMatch.get_available_tournament()
    # 检查已结束赛事 脱离数据库
    ava_keys = []
    for tour in available_tour:
        ava_keys.append(int(tour['tournamentID']))
    for tournamentID in sub_dict.keys():
        if tournamentID not in ava_keys:
            await LoLMatch.del_tournament(tournamentID)
