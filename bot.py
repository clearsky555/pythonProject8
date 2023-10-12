import asyncio

from aiogram import F
from aiogram.enums import ContentType
from aiogram.filters import Command

from bot_utils.commands import set_commands
from bot_utils.handlers import editing_data
from bot_utils.pay import pre_checkout_query, order
from router import dp, bot


async def main():
    print('бот запущен')

    dp.callback_query.register(order, F.data == 'payment_done')
    dp.pre_checkout_query.register(pre_checkout_query)
    dp.message.register(editing_data, F.content_type == ContentType.SUCCESSFUL_PAYMENT)

    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())