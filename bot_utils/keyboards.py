from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_welcome_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='инструкция по заполнению анкеты', callback_data='info')
    builder.button(text='выбор языка', callback_data='language_change')
    builder.button(text='регистрация', callback_data='register')
    builder.button(text='статус анкеты', callback_data='status')
    builder.button(text='отмена', callback_data='cancel')

    builder.adjust(1)
    return builder.as_markup()


def get_level_education_button():
    builder = InlineKeyboardBuilder()
    builder.button(text='primary school only', callback_data='primary school only')
    builder.button(text='high school, no degree', callback_data='high school, no degree')
    builder.button(text='high school degree', callback_data='high school degree')
    builder.button(text='vocational school', callback_data='vocational school')
    builder.button(text='some university courses', callback_data='some university courses')
    builder.button(text='university degree', callback_data='university degree')
    builder.button(text='some graduate level courses', callback_data='some graduate level courses')
    builder.button(text="master's degree", callback_data="master's degree")
    builder.button(text='some doctorate level courses', callback_data='some doctorate level courses')
    builder.button(text='doctorate degree', callback_data='doctorate degree')
    builder.adjust(1)
    return builder.as_markup()


def get_family_status_button():
    builder = InlineKeyboardBuilder()
    builder.button(text='холост/не замужем', callback_data='unmarried')
    builder.button(text='Married and my spouse is NOT a U.S.citizen or U.S. Lawful Permanent Resident (LPR)',
                   callback_data='Married and my spouse is NOT a U.S.citizen')
    builder.button(text='Married and my spouse IS a U.S.citizen or U.S. Lawful Permanent Resident (LPR)',
                   callback_data='Married and my spouse IS a U.S.citizen')
    builder.button(text='разведён/разведена', callback_data='divorced')
    builder.button(text='вдовец/вдова', callback_data='widowed')
    builder.button(text='legally separated', callback_data='legally separated')
    builder.adjust(1)
    return builder.as_markup()


def get_gender_button():
    builder = InlineKeyboardBuilder()
    builder.button(text='мужской', callback_data='male')
    builder.button(text='женский', callback_data='female')
    builder.adjust(1)
    return builder.as_markup()