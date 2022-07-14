import datetime
from os.path import dirname
from typing import Union, Optional

import aiohttp
import ujson as json
from PIL import Image

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher
from nonebot.log import logger
from sqlalchemy.schema import CreateTable
from sqlite3 import OperationalError
from nonebot_plugin_htmlrender import get_new_page as new_page
from .model import sub_tournament, sqlite_pool, connect_database
from .template import make_table

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
    "limit": "18"
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


async def create_image(html: str, wait: int = 0) -> bytes:
    async with new_page() as page:
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(wait)
        img_raw: bytes = await page.locator("#main-container > div").screenshot()
    return img_raw


class LoLMatch:
    tournament_available = []
    tournament_available_date = datetime.datetime(2021, 12, 1)

    @classmethod
    async def creat_table(cls):
        """
        初始化数据库
        :return:
        """
        await connect_database()  # 初始化数据库
        statement = CreateTable(sub_tournament)
        try:
            await sqlite_pool.execute(statement)
        except OperationalError:
            pass
        except Exception as e:
            print(e)
            pass

    @classmethod
    async def tournament_fetch(cls, tournament_id: int):
        statement = sub_tournament.select().where(
            sub_tournament.c.tournament == tournament_id
        )
        return await sqlite_pool.fetch_one(statement)

    @classmethod
    async def del_tournament(cls, tournament_id):
        statement = sub_tournament.delete().where(
            sub_tournament.c.tournament == tournament_id
        )
        await sqlite_pool.execute(statement)

    @classmethod
    async def tournament_upsert(cls, tournament_id: int, group_id: int):
        if (tournament := await cls.tournament_fetch(tournament_id)) is None:
            statement = sub_tournament.insert().values(
                tournament=tournament_id, group_id=[group_id]
            )
            await sqlite_pool.execute(statement)
            return True
        else:
            group_list = tournament["group_id"]
            if group_list is None:
                group_list = []
            if group_id not in group_list:
                group_list.append(group_id)
                statement = (
                    sub_tournament.update()
                    .where(sub_tournament.c.tournament == tournament_id)
                    .values(group_id=group_list)
                )
                await sqlite_pool.execute(statement)
                return True
            return False

    @classmethod
    async def get_sub_tournament(cls, group_id: int = None) -> list:
        """
        获取所给群号已经订阅的所有锦标赛ID
        不提供群号时返回所有
        :param group_id:
        :return:
        """
        statement = sub_tournament.select()
        result = await sqlite_pool.fetch_all(statement)
        if group_id is None:
            return result
        ans = []
        for tournament in result:
            if group_id in tournament["group_id"]:
                ans.append(tournament)
        return ans

    @classmethod
    async def show_subbed_tournament(cls, group_id: int) -> str:
        subbed = await cls.get_sub_tournament(group_id)
        print(subbed)
        if subbed:
            return "已订阅赛事ID: " + " ".join(str(x['tournament']) for x in subbed)
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
    async def get_week_matches(cls, date: str = None) -> Optional[dict]:
        """
        获取属于所给日期的一周的比赛信息
        :param date: 不提供时默认今天
        :return:
        """
        async with aiohttp.ClientSession() as session:
            if date is None:
                match_params.pop("date", 0)
            else:
                match_params["date"] = date
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
    async def show_all_tournaments(cls):
        """
        输出所有正在进行或者即将开始的锦标赛
        :return:
        """
        ava_tour = await cls.get_available_tournament()
        _msg: str = "联赛ID  联赛名称      开始时间\n"
        for tournament in ava_tour:
            _msg += f"{tournament['tournamentID']}  {tournament['short_name']}  {tournament['start_date']}\n"
        return _msg

    @classmethod
    async def show_today_matches(cls) -> str:
        """
        会返回今天所有比赛的结果，不管是否订阅.
        :return:
        """
        matches: dict = await cls.get_week_matches()
        if matches is not None:
            date = datetime.datetime.now().strftime("%Y.%m.%d")
            today_matches = matches[date]
            if isinstance(today_matches, list):
                return "今日无比赛."
            else:
                today_matches: dict
                return cls.analyze_daily(date, today_matches)
        else:
            return "今日无比赛."

    @classmethod
    def analyze_daily(cls, date: str, inf: dict) -> str:
        """
        内部函数，格式化今日比赛信息
        :param date: 日期
        :param inf: 比赛信息
        :return:
        """
        _msg = f"-----{date}-----\n"
        for tournamentID, matchesINFO in inf["info"].items():
            _msg += f"ID:{tournamentID} {matchesINFO['tournamentinfo']['short_name']}\n"
            for match in matchesINFO["list"]:
                # print(match) {match['match_id']}
                _msg += f"{match['start_time']} {match['round_name']} {match['team_a_short_name']} VS {match['team_b_short_name']}\n"
        return _msg

    @classmethod
    def match_result_handle(cls, match_inf: dict) -> str:
        """
        内部函数，构造今日比赛结果简报，提供比赛ID方便查询
        :param match_inf:
        :return:
        """
        _msg = ""
        for match in match_inf:
            _msg += f"ID:{match['match_id']} {match['start_time']} {match['team_a_short_name']} {match['team_a_win']} VS {match['team_b_win']} {match['team_b_short_name']}\n"
        return _msg

    @classmethod
    def match_predict_handle(cls, match_inf: dict) -> str:
        """
        内部函数，构造明日比赛简报
        :param match_inf:
        :return:
        """
        _msg = ""
        for match in match_inf:
            _msg += f"ID:{match['match_id']} {match['start_time']} {match['team_a_short_name']} VS {match['team_b_short_name']} 近10场 {match['near_ten']['team_a_win_count']}:{match['near_ten']['team_b_win_count']}\n"
        return _msg

    @classmethod
    async def show_week_matches(cls):
        """
        返回每周所有比赛信息
        :return:
        """
        matches: dict = await cls.get_week_matches()
        if matches is not None:
            _msg = ""
            for date, matches in matches.items():
                if isinstance(matches, list):
                    _msg += f"---{date}无比赛---\n"
                else:
                    matches: dict
                    _msg += cls.analyze_daily(date, matches)
            return _msg
        else:
            return "本周无比赛."

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

        with open(dirname(__file__) + "/short.css", "r") as f:
            css = f.read()
        html = f"""<html><head><meta charset="utf-8"><style type="text/css">
        {css}</style></head><body class="page-match"><div id="main-container" class="match-container end match-main piece after-classification">{make_table(after_match_detail["data"]["result_list"])}</div></body></html>"""

        return await create_image(html)

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
