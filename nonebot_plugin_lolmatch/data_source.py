import datetime
from os.path import dirname
from typing import Optional, Union

import aiohttp
import ujson as json
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot_plugin_htmlrender import get_new_page as new_page
from nonebot_plugin_htmlrender import md_to_pic
from nonebot_plugin_orm import get_session
from sqlalchemy import select

from .model import SubTournament
from .template import day_analyze_builder, make_table, tournament_brief_builder

api = "https://www.scoregg.com/services/api_url.php"
afterMatchDetail = "https://img.scoregg.com/match/result/{}.json"
headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate",
    # 'cookie':
}
tournament_params = {
    "api_path": "/services/match/web_tournament_group_list.php",
    "method": "GET",
    "platform": "web",
    "api_version": "9.9.9",
    "language_id": "1",
    "gameID": "1",
    "type": "all",
    "page": "1",
    "limit": "18",
    # 'year':
}
match_params = {
    "api_path": "services/match/web_math_list.php",
    "gameID": 1,
    # 'date': 2021-12-06,
    # tournament_id: ,
    "api_version": "9.9.9",
    "platform": "web",
}
calender_params = {
    "api_path": "services / match / web_calendar_match_list.php",
    # 'tournament_id':,
    # 'date': '2021 - 12',
    "gameID": 1,
    "api_version": "9.9.9",
    "platform": "web",
}
match_details_params = {
    "api_path": "/services/match/match_info_new.php",
    "method": "post",
    "platform": "web",
    "api_version": "9.9.9",
    "language_id": 1,
    # 'matchID':  #must need
}
state_str = ["尚未开始", "正在进行", "已结束"]


async def get_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            try:
                return await resp.json()
            except TimeoutError:
                logger.debug("获取锦标赛信息超时.")
                return None


async def create_image(html: str, locator: str, wait: int = 0) -> bytes:
    async with new_page() as page:
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(wait)
        img_raw: bytes = await page.locator(locator).screenshot()
    return img_raw


async def screenshot(url, locator):
    async with new_page() as page:
        await page.goto(url)
        return await page.locator(locator).screenshot()


class LoLMatch:
    tournament_available = []
    tournament_available_date = datetime.datetime(2021, 12, 1)

    @classmethod
    async def tournament_fetch(cls, tournament_id: int) -> Optional[SubTournament]:
        """
        获得订阅改赛事的群
        :param tournament_id: 赛事id
        :return:
        """
        group = None
        async with get_session() as session:
            group = await session.scalar(
                select(SubTournament).where(SubTournament.tournament == tournament_id)
            )
        return group
        # return await SubTournament.filter(tournament=tournament_id).first()

    @classmethod
    async def tournament_delete(cls, tournament_id: int) -> None:
        """
        赛事结束，删除该的订阅条目
        :param tournament_id: 锦标赛id
        :return:
        """
        async with get_session() as session:
            results = await session.scalars(
                select(SubTournament).where(SubTournament.tournament == tournament_id)
            )
            if tournament := results.one_or_none():
                await session.delete(tournament)
                await session.commit()

    @classmethod
    async def tournament_upsert(cls, tournament_id: int, group_id: int) -> bool:
        """
        更新订阅的赛事信息
        :param tournament_id: 锦标赛ID
        :param group_id: 群号
        :return: True 为添加成功 False为赛事添加失败
        """

        async with get_session() as session:
            statement = select(SubTournament).where(
                SubTournament.tournament == tournament_id
            )
            results = await session.scalars(statement)
            if sub_tournament := results.one_or_none():
                group_id_list = sub_tournament.group_id
                if group_id in group_id_list:
                    return False
                sub_tournament.group_id = group_id_list.append(group_id)
            else:
                sub_tournament = SubTournament(
                    tournament=tournament_id, group_id=[group_id]
                )
                session.add(sub_tournament)
            await session.commit()
        return True

    @classmethod
    async def tournament_cancel(cls, tournament_id: int, group_id: int) -> bool:
        """
        取消订阅的赛事信息
        :param tournament_id: 锦标赛ID
        :param group_id: 群号
        :return: True 为取消成功 False为赛事不存在
        """
        if (tournament := await cls.tournament_fetch(tournament_id)) is None:
            return False
        else:
            group_list = tournament.group_id
            if group_list is None:
                return False
            if group_id in group_list:
                group_list.remove(group_id)
                tournament.group_id = group_list
                await tournament.save()
            else:
                return False
        return True

    @classmethod
    async def get_sub_tournament(cls, group_id: int = None) -> list[SubTournament]:
        """
        获取所给群号已经订阅的所有锦标赛ID
        不提供群号时返回所有
        :param group_id:
        :return:
        """
        async with get_session() as session:
            result = await session.scalars(select(SubTournament))
            if group_id is None:
                return result.fetchall()
            ans = []
            for tournament in result.all():
                if group_id in tournament.group_id:
                    ans.append(tournament)
            return ans

    @classmethod
    async def show_subbed_tournament(cls, group_id: int) -> str:
        subbed = await cls.get_sub_tournament(group_id)
        print(subbed)
        if subbed:
            return "已订阅赛事ID: " + " ".join(str(x.tournament) for x in subbed)
        else:
            return "没有订阅"

    @classmethod
    async def get_available_tournament(cls) -> list:
        """
        获取正在进行的和尚未开始的锦标赛
        :return:
        """
        if (
            LoLMatch.tournament_available_date + datetime.timedelta(hours=1)
            > datetime.datetime.now()
        ):
            return cls.tournament_available
        async with aiohttp.ClientSession() as session:
            async with session.post(url=api, data=tournament_params) as resp:
                try:
                    data_json = json.loads(await resp.read())
                except TimeoutError:
                    logger.debug("获取锦标赛信息超时.")
                    return []
        if data_json["code"] == "200":
            cls.tournament_available = [
                tournament
                for tournament in data_json["data"]["list"]
                if tournament["status"] != 2
            ]
            cls.tournament_available_date = datetime.datetime.now()
            return cls.tournament_available
        else:
            return []

    @classmethod
    async def get_week_matches(
        cls, date: str = None, tournament_id: int = None
    ) -> Optional[dict]:
        """
        获取属于所给日期的一周的比赛信息

        :param tournament_id: 可选的联赛id
        :param date: 不提供时默认今天
        :return:
        """
        async with aiohttp.ClientSession() as session:
            if date is None:
                match_params.pop("date", 0)
            else:
                match_params["date"] = date
            if tournament_id is None:
                match_params.pop("tournament_id", 0)
            else:
                match_params["tournament_id"] = tournament_id
            async with session.post(url=api, data=match_params) as resp:
                try:
                    data_json = json.loads(await resp.read())
                except TimeoutError:
                    logger.debug("获取比赛信息超时.")
                    return None
        if data_json["code"] == "200":
            return data_json["data"]["list"]
        else:
            raise f"数据错误 code:{data_json['code']}"

    @classmethod
    async def show_all_tournaments(cls) -> MessageSegment:
        """
        输出所有正在进行或者即将开始的联赛

        :return: 被MessageSegment包装结果图片
        """
        ava_tour = await cls.get_available_tournament()
        if ava_tour:
            _msg: str = "|联赛ID|联赛名称|开始时间|\n"
            _msg += "|:-:|:-:|:-:|\n"
            for tournament in ava_tour:
                _msg += f"|{tournament['tournamentID']}|{tournament['short_name']}|{tournament['start_date']}|\n"
            return MessageSegment.image(await md_to_pic(md=_msg))
        else:
            return MessageSegment.text("没有正在进行或者即将开始的联赛")

    @classmethod
    async def show_all_today_matches(cls) -> MessageSegment:
        """
        会返回今天所有比赛的结果，不管是否订阅.

        :return:
        """
        matches: dict = await cls.get_week_matches()
        if matches:
            date = datetime.datetime.now().strftime("%Y.%m.%d")
            today_matches = matches[date]
            if isinstance(today_matches, list):
                return MessageSegment.text("今日无比赛.")
            else:
                today_matches: dict
                return MessageSegment.image(
                    await create_image(
                        day_analyze_builder(date, today_matches), locator="table"
                    )
                )
        else:
            return MessageSegment.text("今日无比赛.")

    @classmethod
    async def show_week_matches(cls) -> MessageSegment:
        """
        返回每周所有比赛信息
        :return:
        """
        matches: dict = await cls.get_week_matches()
        if matches is not None:
            _msg = MessageSegment.text("本周咨询:\n")
            for date, matches in matches.items():
                if isinstance(matches, list):
                    _msg += f"---{date}无比赛---\n"
                else:
                    matches: dict
                    _msg += MessageSegment.image(
                        await create_image(
                            day_analyze_builder(date, matches), locator="table"
                        )
                    )
            return _msg
        else:
            return MessageSegment.text("本周无比赛.")

    @classmethod
    async def show_tournament_match(cls, tournament_id):
        """
        处理过去一周指定联赛ID的所有比赛

        :return:
        """

        table = """<caption><b>近期赛果</b></caption><tr><th width="100px">比赛日期</th>
        <th width="80px">结果ID</th><th width="220px" bgcolor=#FAEBD7>对战双方</th></tr>"""
        result = await cls.get_week_matches(tournament_id=tournament_id)
        count = 0
        flag = False
        while count < 5:
            for day in result.values().__reversed__():
                if not isinstance(day, dict):
                    continue
                for match in day["info"][str(tournament_id)]["list"]:
                    if match["has_real_time"] == 0:
                        break
                    count += 1
                    table += f"""<tr><td>{match["start_date"]}</td><td>{match["match_id"]}</td>
        <td> {match["team_a_short_name"]} {match["team_a_win"]} <font color=red>VS</font> {match["team_b_win"]} {match["team_b_short_name"]}</td></tr>"""
            if flag:
                break
            flag = True
            prev = datetime.datetime.now() - datetime.timedelta(days=7)
            result = await cls.get_week_matches(
                tournament_id=tournament_id, date=str(prev.date())
            )
        return MessageSegment.image(
            await create_image(tournament_brief_builder(table), "table")
        )

    @classmethod
    async def get_match_details(cls, match_id: Union[int, str]) -> Optional[dict]:
        """
        获得比赛详细信息
        :param match_id:比赛ID
        :return:
        """
        match_details_params["matchID"] = match_id
        async with aiohttp.ClientSession() as session:
            async with session.post(url=api, data=match_details_params) as resp:
                try:
                    data_json = json.loads(await resp.read())
                except TimeoutError:
                    logger.debug("获取比赛细节信息超时.")
                    return None
        if data_json["code"] == "40304":
            return None
        return data_json["data"]

    @classmethod
    async def after_match_detail_screenshot(cls, result_id: int):
        after_match_detail = await get_json(afterMatchDetail.format(result_id))

        with open(dirname(__file__) + "/short.css", "r", encoding="utf-8") as f:
            css = f.read()
        html = f"""<html><head><meta charset="utf-8"><style type="text/css">
        {css}</style></head><body class="page-match"><div id="main-container" class="match-container end match-main piece after-classification">{make_table(after_match_detail["data"]["result_list"])}</div></body></html>"""

        return await create_image(html, locator="#main-container > div")

    @classmethod
    async def show_match_details(
        cls, matcher: Matcher, match_id: Union[int, str]
    ) -> Union[str, MessageSegment]:
        """
        返回所提供比赛ID的具体信息，包括每小场的截图
        :param matcher:
        :param match_id: 比赛ID
        :return:
        """
        matches_data = await cls.get_match_details(match_id)
        if matches_data is None:
            return "获取比赛信息失败，请检查输入."
        match_state: int = int(matches_data["status"])
        _msg = f"ID:{matches_data['matchID']} {state_str[match_state]} {matches_data['tournament_name']}\n"
        if match_state == 2:
            await matcher.send("正在截取结果!")
            _msg += f"----比赛结果----\n{matches_data['team_a_short_name']} {matches_data['team_a_win']} VS {matches_data['team_b_win']} {matches_data['team_b_short_name']}\n"
            return MessageSegment.text(_msg) + await cls.match_detail_screenshot(
                matches_data["result_list"]
            )

    @classmethod
    async def match_detail_screenshot(cls, result_list):
        """
        截图比赛赛后信息，返回一个比赛ID中所有小场的截图
        :param match_id: 要截图的比赛ID 必须提供
        :param match_round: 比赛打了多少把,必须提供
        :return:
        """
        result = None
        for result_id in result_list:
            result += MessageSegment.image(
                await cls.after_match_detail_screenshot(result_id["resultID"])
            )
        return result

    @classmethod
    async def sub_tournament_group(cls, tournament_id: Optional[int], group_id: int):
        if tournament_id is None:
            all_available = [
                lambda x: int(i["tournamentID"])
                for i in await cls.get_available_tournament()
            ]
        else:
            all_available = [tournament_id]
        for tournament in all_available:
            if await cls.tournament_upsert(tournament, group_id):
                return f"联赛ID {tournament_id} 订阅成功"
            else:
                return f"联赛ID {tournament_id} 已经订阅"

    @classmethod
    async def cancel_tournament_group(cls, tournament_id: Optional[int], group_id: int):
        if tournament_id is None:
            all_available = [
                lambda x: int(i["tournamentID"])
                for i in await cls.get_available_tournament()
            ]
        else:
            all_available = [tournament_id]
        for tournament in all_available:
            if await cls.tournament_cancel(tournament, group_id):
                return f"联赛ID {tournament_id} 取消订阅"
            else:
                return f"联赛ID {tournament_id} 没有订阅"
