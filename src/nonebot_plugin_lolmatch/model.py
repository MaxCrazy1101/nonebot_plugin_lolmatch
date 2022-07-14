from os.path import dirname
from databases import Database
from sqlalchemy import Table, Column, JSON, Integer, MetaData
from nonebot.log import logger

sqlite_bind = f"sqlite:///{dirname(__file__)}/lol_match.db"  # 数据库位置


sqlite_pool = Database(sqlite_bind)
metadata = MetaData()


async def connect_database():
    try:
        await sqlite_pool.connect()
        logger.info(f"数据库已连接 {sqlite_bind}")
    except:
        logger.info("数据库连接失败")


async def disconnect_database():
    if sqlite_pool is not None:
        await sqlite_pool.disconnect()
        logger.info(f"数据库已断开 {sqlite_bind}")


sub_tournament = Table(
    'sub_tournament',
    metadata,
    Column('tournament', Integer, primary_key=True),
    Column('group_id', JSON),
)
