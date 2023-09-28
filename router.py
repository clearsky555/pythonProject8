from aiogram import Bot, Dispatcher

from bot_utils import handlers
from config import TOKEN

from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# router

dp.include_router(handlers.router)