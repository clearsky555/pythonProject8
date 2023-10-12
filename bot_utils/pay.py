from aiogram import Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery

from config import PAY_TOKEN


async def order(callback: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title='Покупка через Telegram бот',
        description='Для оплаты используйте данные тестовой карты: 1111 1111 1111 1026, 12/22, CVC 000',
        payload='Payment through a bot',
        provider_token=PAY_TOKEN,
        currency='rub',
        prices=[
            LabeledPrice(
                label='Доступ к секретной информации',
                amount=99000
            ),
            LabeledPrice(
                label='НДС',
                amount=20000
            ),
            LabeledPrice(
                label='Скидка',
                amount=-20000
            ),
            LabeledPrice(
                label='Бонус',
                amount=-40000
            )
        ],
        # max_tip_amount=5000,
        # suggested_tip_amounts=[1000, 2000, 3000, 4000],
        start_parameter='',
        provider_data=None,
        # photo_url='https://i.ibb.co/zGw5X0B/image.jpg',
        # photo_size=100,
        # photo_width=800,
        # photo_height=450,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=15
    )


async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# async def successful_payment(message: Message):
#     msg = f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}.' \
#           f'\r\nНаш менеджер получил заявку и уже набирает Ваш номер телефона.' \
#           f'\r\nПока можете скачать цифровую версию нашего продукта https://nztcoder.com'
#     await message.answer(msg)
#     await editing_data(message=message)