import asyncio

from bot_utils.commands import set_commands
from router import dp, bot


async def main():
    print('бот запущен')
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())