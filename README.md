<!-- markdownlint-disable MD033 MD041-->
<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot_plugin_lolmatch

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
_✨ 一个有关lol比赛信息的插件 ✨_
<!-- prettier-ignore-end -->

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/nonebot/nonebot2/master/LICENSE">
    <img src="https://img.shields.io/github/license/nonebot/nonebot2" alt="license">
  </a>

## 简介

lolmatch是一个有关于lol比赛信息的插件，你可以用它来获取每天的比赛结果。本人python新手，有bug请提交issue，欢迎pr

## 注意

因为本插件使用了playwright模块，在windows平台需要在prod下运行不能热重载

使用本插件需要提供定时模块可以使用以下命令安装

```
    nb plugin install nonebot_plugin_apscheduler
```

使用本插件需要提供htmlrender插件可以使用以下命令安装

```
    nb plugin install nonebot_plugin_htmlrender
```

## 使用

        主命令 lol 查看今日比赛信息
        附带命令 本周 查看本周比赛信息
        附带命令 详情 [matchID] 查询指定比赛详细信息
        附带命令 订阅 [tournamentID] 订阅联赛 每晚检查当日结果和第二天赛程
        附带命令 查看订阅 查看已订阅的所有联赛
        附带命令 联赛 查看所有即将进行或正在进行的联赛和tournamentID

## 即刻开始

- 使用 nb-cli

```
    nb plugin install nonebot_plugin_lolmatch
```

- 使用 pip

```
    pip install nonebot_plugin_lolmatch
```

### 常见问题

### 教程/实际项目/经验分享

## 许可证

`nonebot_plugin_lolmatch` 采用 `MIT` 协议开源，协议文件参考 [LICENSE](./LICENSE)。

