from aiogram import Dispatcher, Bot, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.mongo import MongoStorage

from config import config
from db import database

router = Router()
admin = Router()

bot_properties = DefaultBotProperties(
    link_preview_is_disabled=True,
    parse_mode=ParseMode.HTML
)
main_bot = Bot(config['bot']['token'], default=bot_properties)

dispatcher = Dispatcher(storage=MongoStorage(database.client, config['bot']['database']))
dispatcher.include_router(router)
dispatcher.include_router(admin)


async def start():
    await dispatcher.start_polling(main_bot)
