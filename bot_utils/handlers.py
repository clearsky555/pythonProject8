import os
import uuid

from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, PhotoSize
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from bot_utils.keyboards import get_welcome_kb, get_level_education_button, get_family_status_button, get_gender_button
from state import UserState
from db.database import users_manager


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'Добро пожаловать! Я бот для регистрации на лотерею green card',
        reply_markup=get_welcome_kb()
    )


@router.callback_query(F.data == 'info')
async def get_info(callback: CallbackQuery):
    text = '''
информация по заполнению анкеты 
информация по заполнению анкеты 
информация по заполнению анкеты 
информация по заполнению анкеты 
информация по заполнению анкеты 
информация по заполнению анкеты 
информация по заполнению анкеты 
информация по заполнению анкеты
    '''
    await callback.message.answer(text)


@router.callback_query(F.data == 'cancel')
async def get_cancel(callback: CallbackQuery):
    await cmd_start(callback.message)


@router.callback_query(F.data == 'register')
async def education_level(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer(
        text="ваш наивысший уровень образования/highest level of education",
        reply_markup=get_level_education_button()
    )
    await state.set_state(UserState.education_level)


@router.callback_query(UserState.education_level)
async def marital_status(callback: CallbackQuery, state: FSMContext):
    print(callback.data)

    await state.update_data(education_level=callback.data)

    await callback.message.answer(
        text="укажите ваше семейное положение",
        reply_markup=get_family_status_button()
    )
    await state.set_state(UserState.marital_status)


@router.callback_query(UserState.marital_status)
async def name(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    await state.update_data(marital_status=callback.data)

    await callback.message.answer(
        text="укажите ваше имя",
    )
    await state.set_state(UserState.name)


@router.message(UserState.name)
async def surname(message: Message, state: FSMContext):
    print(message.text)
    await state.update_data(name=message.text)
    await message.answer(
        text="укажите вашу фамилию",
    )
    await state.set_state(UserState.surname)


@router.message(UserState.surname)
async def gender(message: Message, state: FSMContext):
    print(message.text)
    await state.update_data(surname=message.text)
    await message.answer(
        text="укажите ваш пол",
        reply_markup=get_gender_button()
    )
    await state.set_state(UserState.gender)


@router.callback_query(UserState.gender)
async def birth_date(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    await state.update_data(gender=callback.data)
    await callback.message.answer(
        text="укажите вашу дату рождения в формате ГГГГ.ММ.ЧЧ, например - 2001.12.19(birth_date)",
    )
    await state.set_state(UserState.birth_date)


@router.message(UserState.birth_date)
async def birth_city(message: Message, state: FSMContext):
    print(message.text)

    await state.update_data(birth_date=message.text)

    unknowncity_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='город рождения не известен',
        callback_data='unknowncity')
    keyboard: list[list[InlineKeyboardButton]] = [
        [unknowncity_btn],
        ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)

    await message.answer(
        text="укажите ваш город рождения",
        reply_markup=markup,
    )
    await state.set_state(UserState.birth_city)


@router.message(UserState.birth_city)
async def birth_country(message: Message, state: FSMContext):
    print(message.text)
    await state.update_data(birth_city=message.text)
    await message.answer(
        text="укажите вашу страну рождения",
    )
    await state.set_state(UserState.birth_country)


@router.message(UserState.birth_country)
async def eligibility(message: Message, state: FSMContext):
    print(message.text)
    await state.update_data(birth_country=message.text)

    yes_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='yes',
        callback_data='eligibility_yes')
    no_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='no',
        callback_data='eligibility_no')
    keyboard: list[list[InlineKeyboardButton]] = [
        [yes_btn, no_btn],
        ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)
    await message.answer(
        text="Страна, в которой вы родились, допущена ли к лотерее?",
        reply_markup=markup
    )
    await state.set_state(UserState.eligibility)


@router.callback_query(F.data == 'eligibility_yes')
async def write_eligibility_yes(callback: CallbackQuery, state: FSMContext):
    await state.update_data(eligibility=callback.data)
    await ok(message=callback.message, state=state)


@router.callback_query(F.data == 'eligibility_no')
async def eligibility_country(callback: CallbackQuery, state: FSMContext):
    await state.update_data(eligibility=callback.data)

    await callback.message.answer(
        text="введите страну рождения супруга или родителей",
    )
    await state.set_state(UserState.country_claiming_eligibility)


@router.message(UserState.country_claiming_eligibility)
async def write_eligibility_no(message: Message, state: FSMContext):
    await state.update_data(country_claiming_eligibility=message.text)
    await ok(message=message, state=state)


async def ok(message: Message, state: FSMContext):
    await message.answer(
        text="отправьте вашу фотографию",
    )
    await state.set_state(UserState.upload_photo)


@router.message(UserState.upload_photo)
async def download_photo(message: Message, bot: Bot, state: FSMContext):

    telegram_user_id = message.from_user.id
    unique_filename = str(uuid.uuid4())
    filename = f"{unique_filename}.jpg"
    user_directory = f"media/users/{telegram_user_id}/"
    os.makedirs(user_directory, exist_ok=True)
    photo_path = os.path.join(user_directory, filename)

    await bot.download(
        message.photo[-1],
        destination=photo_path
    )

    await state.update_data(photo_url=photo_path)

    await message.answer(
        text="напишите ваш адрес",
    )
    await state.set_state(UserState.address_line_1)


@router.message(UserState.address_line_1)
async def city(message: Message, state: FSMContext):
    await state.update_data(address_line_1=message.text)

    await message.answer(
        text="введите ваш город",
    )
    await state.set_state(UserState.city)


@router.message(UserState.city)
async def district(message: Message, state: FSMContext):
    await state.update_data(city=message.text)

    await message.answer(
        text="введите ваш регион",
    )
    await state.set_state(UserState.district)


@router.message(UserState.district)
async def district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)

    await message.answer(
        text="введите вашу страну",
    )
    await state.set_state(UserState.country)


@router.message(UserState.country)
async def child_and_spouse(message: Message, state: FSMContext):

    data = await state.get_data()
    marital_status = data['marital_status']



    await state.update_data(country=message.text)

    yes_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='добавить супруга',
        callback_data='spouse_yes')
    no_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='добавить ребенка',
        callback_data='child_yes')
    end_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='закончить заполнение анкеты',
        callback_data='end')
    if marital_status == 'Married and my spouse is NOT a U.S.citizen':
        keyboard: list[list[InlineKeyboardButton]] = [
            [no_btn, end_btn],
            ]
    else:
        keyboard: list[list[InlineKeyboardButton]] = [
            [yes_btn, no_btn, end_btn],
            ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)
    await message.answer(
        text="если у вас есть супруг или ребенок, вам нужно заполнить их данные",
        reply_markup=markup
    )


@router.callback_query(F.data == 'end')
async def end(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users_manager.create_table()
    telegram_user_id = callback.message.from_user.id
    education_level = data['education_level']
    marital_status = data['marital_status']
    name = data['name']
    surname = data['surname']
    gender = data['gender']
    birth_date = data['birth_date']
    birth_city = data['birth_city']
    birth_country = data['birth_country']
    eligibility = data['eligibility']
    try:
        country_claiming_eligibility = data['country_claiming_eligibility']
    except KeyError:
        country_claiming_eligibility = None
    photo_url = data['photo_url']
    address_line_1 = data['address_line_1']
    city = data['city']
    district = data['district']
    country = data['country']
    user_data = {
        'telegram_user_id': telegram_user_id,
        'name': name,
        'surname': surname,
        'gender': gender,
        'birth_date': birth_date,
        'birth_city': birth_city,
        'birth_country': birth_country,
        'eligibility': eligibility,
        'country_claiming_eligibility': country_claiming_eligibility,
        'photo_url': photo_url,
        'marital_status': marital_status,
        'city': city,
        'address_line_1': address_line_1,
        'district': district,
        'country': country,
        'education_level': education_level,
    }
    try:
        users_manager.record_user_in_db(user_data)
        await callback.message.answer('Данные успешно записаны в базу данных!')

    except Exception as ex:
        print(ex)
        await callback.message.answer(f'произошла ошибка {ex}!')

