day_html_header = """<html lang="zh-cn">
<header>
    <meta charset="utf-8">
    <style type="text/css">
        table {
            border-spacing: 0;
            align-items: center;
            border: 1px solid #000000;
            margin: auto;
        }
        td {
            text-align: center;
        }
        caption{
            font-size: large;
            color: #0d7eff;
        }
        div {
            display: table;
            margin: auto;
        }
    </style>
</header>
"""
day_html_body = """<body>
<table border="1">
    <caption><b>{caption}</b></caption>
    <tr>
        <th width="80px">预计时间</th>
        <th width="80px">比赛级别</th>
        <th width="50%" bgcolor=#FAEBD7>对战双方</th>
    </tr>
    {body}
</table>
</body>
</html>"""

match_brief_body = """<body><div>{body}</div></body></html>"""
match_brief_today = """<tr><th width="80px">结果ID</th><th width="240px" bgcolor=#FAEBD7>对战双方</th></tr>"""
match_brief_tomorrow = """<tr><th width="80px">比赛时间</th><th width="240px" bgcolor=#FAEBD7>对战双方</th></tr>"""


def day_analyze_builder(date: str, inf: dict) -> str:
    """
    内部函数，格式化今日比赛信息

    :param date: 日期
    :param inf: 比赛信息
    :return:
    """
    _msg = ""
    for tournamentID, matchesINFO in inf["info"].items():
        _msg += f"""<tr><th colspan="3" align="center">联赛ID:{tournamentID}&nbsp;&nbsp;&nbsp;{matchesINFO['tournamentinfo']['short_name']}</th></tr>"""
        for match in matchesINFO["list"]:
            _msg += f"""<tr><td>{match['start_time']}</td><td>{match['round_name']}</td><td> {match['team_a_short_name']} <font color=red>VS</font> {match['team_b_short_name']}</td></tr>"""
    return day_html_header + day_html_body.format(caption=f"---{date}---", body=_msg)


def match_brief_builder(msg: dict) -> str:
    html = ""
    if msg["j"]:
        html += f"""<table border="1"><caption><b>今日赛报</b></caption>{match_brief_today}{msg["j"]}</table>"""
    if msg["m"]:
        html += f"""<table border="1"><caption><b>明日赛程</b></caption>{match_brief_tomorrow}{msg["m"]}</table>"""
    return day_html_header + match_brief_body.format(body=html)


class DayAnalyze:
    pass


def make_table(result_list: dict):
    if result_list["win_teamID"] == result_list["blue_teamID"]:
        team_blue_result = "胜利"
        team_red_result = "败北"
    else:
        team_blue_result = "败北"
        team_red_result = "胜利"
    max_damage_atk = max(
        map(int, [result_list["blue_star_a_atk_o"], result_list["blue_star_b_atk_o"],
                  result_list["blue_star_c_atk_o"], result_list["blue_star_d_atk_o"],
                  result_list["blue_star_e_atk_o"], result_list["red_star_e_atk_o"],
                  result_list["red_star_d_atk_o"], result_list["red_star_c_atk_o"],
                  result_list["red_star_b_atk_o"], result_list["red_star_a_atk_o"]]))
    max_damage_def = max(
        map(int, [result_list["blue_star_a_def_o"], result_list["blue_star_b_def_o"],
                  result_list["blue_star_c_def_o"], result_list["blue_star_d_def_o"],
                  result_list["blue_star_e_def_o"], result_list["red_star_e_def_o"],
                  result_list["red_star_d_def_o"], result_list["red_star_c_def_o"],
                  result_list["red_star_b_def_o"], result_list["red_star_a_def_o"]]))

    return f"""
            <div class="table-wrap" style="">
            <table class="table blue">
                <thead>
                    <tr>
                        <th>{result_list["blue_name"]} {team_blue_result}</th>
                        <th>出装</th>
                        <th>KDA</th>
                        <th>输出</th>
                        <th>承伤</th>
                        <th>补兵</th>
                        <th>金钱</th>
                        <th>评分</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["blue_star_a_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["blue_hero_a_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["blue_a_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["blue_a_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["blue_star_a_name"]}" class="nickname mid">{result_list["blue_star_a_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["blue_star_a_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_a_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_a_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_a_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_a_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_a_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_a_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["blue_star_a_kda"]}</p>
                            <p>{result_list["blue_star_a_kills"]} / {result_list["blue_star_a_deaths"]} / {result_list["blue_star_a_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["blue_star_a_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_a_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["blue_star_a_atk_o"]} ({result_list["blue_star_a_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["blue_star_a_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_a_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["blue_star_a_def_o"]} ({result_list["blue_star_a_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["blue_star_a_hits"]}</p>
                            <p>{result_list["blue_star_a_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["blue_star_a_money"]}</p>
                        </td>
                        <td>{result_list["blue_star_a_score"]}</td>
                    </tr>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["blue_star_b_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["blue_hero_b_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["blue_b_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["blue_b_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["blue_star_b_name"]}" class="nickname mid">{result_list["blue_star_b_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["blue_star_b_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_b_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_b_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_b_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_b_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_b_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_b_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["blue_star_b_kda"]}</p>
                            <p>{result_list["blue_star_b_kills"]} / {result_list["blue_star_b_deaths"]} / {result_list["blue_star_b_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["blue_star_b_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_b_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["blue_star_b_atk_o"]} ({result_list["blue_star_b_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["blue_star_b_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_b_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["blue_star_b_def_o"]} ({result_list["blue_star_b_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["blue_star_b_hits"]}</p>
                            <p>{result_list["blue_star_b_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["blue_star_b_money"]}</p>
                        </td>
                        <td>{result_list["blue_star_b_score"]}</td>
                    </tr>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["blue_star_c_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["blue_hero_c_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["blue_c_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["blue_c_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["blue_star_c_name"]}" class="nickname mid">{result_list["blue_star_c_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["blue_star_c_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_c_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_c_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_c_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_c_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_c_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_c_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["blue_star_c_kda"]}</p>
                            <p>{result_list["blue_star_c_kills"]} / {result_list["blue_star_c_deaths"]} / {result_list["blue_star_c_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["blue_star_c_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_c_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["blue_star_c_atk_o"]} ({result_list["blue_star_c_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["blue_star_c_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_c_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["blue_star_c_def_o"]} ({result_list["blue_star_c_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["blue_star_c_hits"]}</p>
                            <p>{result_list["blue_star_c_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["blue_star_c_money"]}</p>
                        </td>
                        <td>{result_list["blue_star_c_score"]}</td>
                    </tr>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["blue_star_d_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["blue_hero_d_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["blue_d_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["blue_d_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["blue_star_d_name"]}" class="nickname mid">{result_list["blue_star_d_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["blue_star_d_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_d_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_d_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_d_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_d_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_d_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_d_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["blue_star_d_kda"]}</p>
                            <p>{result_list["blue_star_d_kills"]} / {result_list["blue_star_d_deaths"]} / {result_list["blue_star_d_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["blue_star_d_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_d_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["blue_star_d_atk_o"]} ({result_list["blue_star_d_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["blue_star_d_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_d_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["blue_star_d_def_o"]} ({result_list["blue_star_d_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["blue_star_d_hits"]}</p>
                            <p>{result_list["blue_star_d_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["blue_star_d_money"]}</p>
                        </td>
                        <td>{result_list["blue_star_d_score"]}</td>
                    </tr>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["blue_star_e_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["blue_hero_e_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["blue_e_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["blue_e_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["blue_star_e_name"]}" class="nickname mid">{result_list["blue_star_e_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["blue_star_e_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_e_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_e_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_e_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_e_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_e_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["blue_star_e_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["blue_star_e_kda"]}</p>
                            <p>{result_list["blue_star_e_kills"]} / {result_list["blue_star_e_deaths"]} / {result_list["blue_star_e_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["blue_star_e_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_e_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["blue_star_e_atk_o"]} ({result_list["blue_star_e_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["blue_star_e_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["blue_star_e_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["blue_star_e_def_o"]} ({result_list["blue_star_e_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["blue_star_e_hits"]}</p>
                            <p>{result_list["blue_star_e_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["blue_star_e_money"]}</p>
                        </td>
                        <td>{result_list["blue_star_e_score"]}</td>
                    </tr>
                </tbody>
            </table>
            <table class="table red">
                <thead>
                    <tr>
                        <th>{result_list["red_name"]} {team_red_result}</th>
                        <th>出装</th>
                        <th>KDA</th>
                        <th>输出</th>
                        <th>承伤</th>
                        <th>补兵</th>
                        <th>金钱</th>
                        <th>评分</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["red_star_a_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["red_hero_a_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["red_a_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["red_a_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["red_star_a_name"]}" class="nickname mid">{result_list["red_star_a_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["red_star_a_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_a_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_a_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_a_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_a_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_a_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_a_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["red_star_a_kda"]}</p>
                            <p>{result_list["red_star_a_kills"]} / {result_list["red_star_a_deaths"]} / {result_list["red_star_a_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["red_star_a_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_a_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["red_star_a_atk_o"]} ({result_list["red_star_a_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["red_star_a_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_a_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["red_star_a_def_o"]} ({result_list["red_star_a_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["red_star_a_hits"]}</p>
                            <p>{result_list["red_star_a_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["red_star_a_money"]}</p>
                        </td>
                        <td>{result_list["red_star_a_score"]}</td>
                    </tr>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["red_star_b_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["red_hero_b_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["red_b_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["red_b_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["red_star_b_name"]}" class="nickname mid">{result_list["red_star_b_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["red_star_b_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_b_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_b_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_b_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_b_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_b_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_b_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["red_star_b_kda"]}</p>
                            <p>{result_list["red_star_b_kills"]} / {result_list["red_star_b_deaths"]} / {result_list["red_star_b_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["red_star_b_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_b_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["red_star_b_atk_o"]} ({result_list["red_star_b_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["red_star_b_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_b_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["red_star_b_def_o"]} ({result_list["red_star_b_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["red_star_b_hits"]}</p>
                            <p>{result_list["red_star_b_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["red_star_b_money"]}</p>
                        </td>
                        <td>{result_list["red_star_b_score"]}</td>
                    </tr>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["red_star_c_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["red_hero_c_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["red_c_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["red_c_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["red_star_c_name"]}" class="nickname mid">{result_list["red_star_c_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["red_star_c_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_c_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_c_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_c_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_c_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_c_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_c_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["red_star_c_kda"]}</p>
                            <p>{result_list["red_star_c_kills"]} / {result_list["red_star_c_deaths"]} / {result_list["red_star_c_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["red_star_c_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_c_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["red_star_c_atk_o"]} ({result_list["red_star_c_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["red_star_c_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_c_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["red_star_c_def_o"]} ({result_list["red_star_c_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["red_star_c_hits"]}</p>
                            <p>{result_list["red_star_c_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["red_star_c_money"]}</p>
                        </td>
                        <td>{result_list["red_star_c_score"]}</td>
                    </tr>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["red_star_d_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["red_hero_d_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["red_d_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["red_d_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["red_star_d_name"]}" class="nickname mid">{result_list["red_star_d_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["red_star_d_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_d_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_d_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_d_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_d_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_d_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_d_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["red_star_d_kda"]}</p>
                            <p>{result_list["red_star_d_kills"]} / {result_list["red_star_d_deaths"]} / {result_list["red_star_d_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["red_star_d_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_d_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["red_star_d_atk_o"]} ({result_list["red_star_d_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["red_star_d_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_d_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["red_star_d_def_o"]} ({result_list["red_star_d_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["red_star_d_hits"]}</p>
                            <p>{result_list["red_star_d_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["red_star_d_money"]}</p>
                        </td>
                        <td>{result_list["red_star_d_score"]}</td>
                    </tr>
                    <tr>
                        <td><a target="_blank"><div class="avatar player mid"><img src="{result_list["red_star_e_player_image"]}"></div></a>
                            <div class="avatar hero mid"><img src="{result_list["red_hero_e_pic"]}" class="role-icon mid"><span class="lv">18</span></div>
                            <div class="jn-icon-wrap mid">
                                <div class="property-img"><img src="{result_list["red_e_skill_1"]}" class="jn-icon"></div>
                                <div class="property-img"><img src="{result_list["red_e_skill_2"]}" class="jn-icon"></div>
                            </div> <a target="_blank"><span title="{result_list["red_star_e_name"]}" class="nickname mid">{result_list["red_star_e_name"]}</span></a>
                        </td>
                        <td>
                            <div class="property-img mid"><img src="{result_list["red_star_e_equip_1"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_e_equip_2"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_e_equip_3"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_e_equip_4"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_e_equip_5"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_e_equip_6"]}"></div>
                            <div class="property-img mid"><img src="{result_list["red_star_e_equip_7"]}"></div>
                        </td>
                        <td class="kda">
                            <p>{result_list["red_star_e_kda"]}</p>
                            <p>{result_list["red_star_e_kills"]} / {result_list["red_star_e_deaths"]} / {result_list["red_star_e_assists"]}</p>
                        </td>
                        <td class="damage atk">
                            <p>{result_list["red_star_e_atk_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_e_atk_o"]) * 100 / max_damage_atk}%;"></div>
                                <div class="pop-data">
                                    <div>总输出 (分均)</div>
                                    <p>{result_list["red_star_e_atk_o"]} ({result_list["red_star_e_atk_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="damage def">
                            <p>{result_list["red_star_e_def_p"]}%</p>
                            <div class="data-bar">
                                <div class="rate-bar" style="width: {int(result_list["red_star_e_def_o"]) * 100 / max_damage_def}%;"></div>
                                <div class="pop-data">
                                    <div>总承伤 (分均)</div>
                                    <p>{result_list["red_star_e_def_o"]} ({result_list["red_star_e_def_m"]})</p>
                                </div>
                            </div>
                        </td>
                        <td class="hits">
                            <p>{result_list["red_star_e_hits"]}</p>
                            <p>{result_list["red_star_e_adc_m"]}/分</p>
                        </td>
                        <td>
                            <p>{result_list["red_star_e_money"]}</p>
                        </td>
                        <td>{result_list["red_star_e_score"]}</td>
                    </tr>
                </tbody>
            </table>
        </div>
"""
