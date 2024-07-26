import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import config
from db.models.emissions import Emission

client = AsyncIOMotorClient(config['bot']['mongo'])
logging.getLogger('pymongo').setLevel(logging.WARNING)


async def connect():
    await init_beanie(database=client[config['bot']['database']],
                      document_models=[Emission])
