from databases import Database
from sqlalchemy import Table, Column, JSON, Integer, MetaData
from nonebot.log import logger

sqlite_bind = "sqlite://lol_match.db"  # 数据库位置

sqlite_pool = Database(sqlite_bind)
metadata = MetaData()


async def init_database():
    try:
        await sqlite_pool.connect()
        logger.info("数据库已连接")
    except:
        logger.info("数据库连接失败")


sub_tournament = Table(
    'sub_tournament',
    metadata,
    Column('tournament', Integer, primary_key=True),
    Column('group_id', JSON),
)
