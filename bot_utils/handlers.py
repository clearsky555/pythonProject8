import os
import uuid

from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, PhotoSize, FSInputFile
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from bot_utils.keyboards import get_welcome_kb, get_level_education_button, get_family_status_button, get_gender_button, get_user_edit_button
from state import UserState, SpouseState, ChildState, UserEditState
from db.database import users_manager, spouse_manager

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
        text="""
Пожалуйста, отправьте вашу фотографию.
Основные требования к фото для Грин Карты:
    1) Фотография должна быть цветной и чёткой
    2) На снимке не должен быть искажен цвет кожи
    3) Фон за человеком должен быть светлый
    4) Не должно быть тени на фоне
    5) Голова должна быть в центре снимка
    6) Голова на снимке должна занимать 50-69% от высоты фото
    7) Глаза на фото должны быть открыты, очки не допускаются
    8) Взгляд фотографируемого нейтральный
    9) Одежда должна быть повседневной, недопустимо фотографироваться в форме
    10) Нельзя фотографироваться в головных уборах закрывающих волосы
    11) Фото должно быть не старше 6 месяцев
        """,
    )

    image_from_pc = FSInputFile(path=r'/home/clear/PycharmProjects/pythonProject8/media/samples/wrong.jpg')
    await message.answer_photo(
        photo=image_from_pc,
        caption='примеры неправильных фото',
    )
    image_from_pc_2 = FSInputFile(path=r'/home/clear/PycharmProjects/pythonProject8/media/samples/right.png')
    await message.answer_photo(
        photo=image_from_pc_2,
        caption='пример правильного фото'
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

    # data = await state.get_data()
    users_manager.create_table()
    telegram_user_id = message.from_user.id
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
    country = message.text
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
        await message.answer('Данные успешно записаны в базу данных!')

    except Exception as ex:
        print(ex)
        await message.answer(f'произошла ошибка {ex}!')

    finally:
        await state.clear()


    yes_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='добавить супруга',
        callback_data='spouse_yes')
    no_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='добавить ребенка',
        callback_data='add_children')
    end_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='закончить заполнение анкеты',
        callback_data='payment')
    if marital_status == 'Married and my spouse is NOT a U.S.citizen':
        keyboard: list[list[InlineKeyboardButton]] = [
            [yes_btn, no_btn, end_btn],
        ]
    else:
        keyboard: list[list[InlineKeyboardButton]] = [
            [no_btn, end_btn],
        ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)
    await message.answer(
        text="если у вас есть супруг или ребенок, вам нужно заполнить их данные",
        reply_markup=markup
    )


# @router.callback_query(F.data == 'end')
# async def end(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     users_manager.create_table()
#     telegram_user_id = callback.from_user.id
#     education_level = data['education_level']
#     marital_status = data['marital_status']
#     name = data['name']
#     surname = data['surname']
#     gender = data['gender']
#     birth_date = data['birth_date']
#     birth_city = data['birth_city']
#     birth_country = data['birth_country']
#     eligibility = data['eligibility']
#     try:
#         country_claiming_eligibility = data['country_claiming_eligibility']
#     except KeyError:
#         country_claiming_eligibility = None
#     photo_url = data['photo_url']
#     address_line_1 = data['address_line_1']
#     city = data['city']
#     district = data['district']
#     country = data['country']
#     user_data = {
#         'telegram_user_id': telegram_user_id,
#         'name': name,
#         'surname': surname,
#         'gender': gender,
#         'birth_date': birth_date,
#         'birth_city': birth_city,
#         'birth_country': birth_country,
#         'eligibility': eligibility,
#         'country_claiming_eligibility': country_claiming_eligibility,
#         'photo_url': photo_url,
#         'marital_status': marital_status,
#         'city': city,
#         'address_line_1': address_line_1,
#         'district': district,
#         'country': country,
#         'education_level': education_level,
#     }
#     try:
#         users_manager.record_user_in_db(user_data)
#         await callback.message.answer('Данные успешно записаны в базу данных!')
#
#     except Exception as ex:
#         print(ex)
#         await callback.message.answer(f'произошла ошибка {ex}!')
#
#     finally:
#         await state.clear()


@router.callback_query(F.data == 'spouse_yes')
async def spouse_name(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer(
        text="введите имя вашего супруга",
    )
    await state.set_state(SpouseState.name)


@router.message(SpouseState.name)
async def spouse_surname(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        text="укажите фамилию вашего супруга",
    )
    await state.set_state(SpouseState.surname)


@router.message(SpouseState.surname)
async def spouse_birth_data(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer(
        text="укажите дату рождения вашего супруга",
    )
    await state.set_state(SpouseState.birth_date)


@router.message(SpouseState.birth_date)
async def spouse_gender(message: Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await message.answer(
        text="укажите пол вашего супруга",
        reply_markup=get_gender_button()
    )
    await state.set_state(SpouseState.gender)


@router.callback_query(SpouseState.gender)
async def spouse_birth_city(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)

    unknowncity_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='город рождения не известен',
        callback_data='spouse_unknowncity')
    keyboard: list[list[InlineKeyboardButton]] = [
        [unknowncity_btn],
    ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)

    await callback.message.answer(
        text="укажите город рождения вашего супруга",
        reply_markup=markup,
    )
    await state.set_state(SpouseState.birth_city)


@router.message(SpouseState.birth_city)
async def spouse_birth_country(message: Message, state: FSMContext):
    await state.update_data(birth_city=message.text)
    await message.answer(
        text="укажите страну рождения вашего супруга",
    )
    await state.set_state(SpouseState.birth_country)


@router.message(SpouseState.birth_country)
async def spouse_photo(message: Message, state: FSMContext):
    await state.update_data(birth_country=message.text)
    await message.answer(
        text="отправьте фотографию вашего супруга",
    )
    await state.set_state(SpouseState.upload_photo)


@router.message(SpouseState.upload_photo)
async def spouse_download_photo(message: Message, bot: Bot, state: FSMContext):
    telegram_user_id = message.from_user.id
    unique_filename = str(uuid.uuid4())
    filename = f"{unique_filename}.jpg"
    user_directory = f"media/users/{telegram_user_id}/spouse/"
    os.makedirs(user_directory, exist_ok=True)
    photo_path = os.path.join(user_directory, filename)

    await bot.download(
        message.photo[-1],
        destination=photo_path
    )

    await state.update_data(photo_url=photo_path)

    data = await state.get_data()
    spouse_manager.create_table()
    name = data['name']
    surname = data['surname']
    gender = data['gender']
    birth_date = data['birth_date']
    birth_city = data['birth_city']
    birth_country = data['birth_country']
    photo_url = data['photo_url']
    user_id = users_manager.get_user_id_by_telegram_user_id(telegram_user_id)
    print(user_id)
    spouse_data = {
        'telegram_user_id': telegram_user_id,
        'name': name,
        'surname': surname,
        'gender': gender,
        'birth_date': birth_date,
        'birth_city': birth_city,
        'birth_country': birth_country,
        'photo_url': photo_url,
        'user_id': user_id,
    }
    try:
        spouse_manager.record_spouse_in_db(spouse_data)
        await message.answer('Данные о супруге успешно записаны в базу данных!')

    except Exception as ex:
        print(ex)
        await message.answer(f'произошла ошибка {ex}!')

    finally:
        await state.clear()

    unknowncity_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='продолжить заполнение',
        callback_data='add_children')
    keyboard: list[list[InlineKeyboardButton]] = [
        [unknowncity_btn],
    ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)

    await message.answer(
        text='чтобы продолжить заполнять анкету, вам нужно добавить сведения о детях',
        reply_markup=markup,
    )
    # await state.set_state(ChildState.number_of_children)


@router.callback_query(F.data == 'add_children')
async def common_number_of_children(callback: CallbackQuery, state: FSMContext):

    nochild_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='если у вас нет детей, нажмите сюда (завершить заполнение анкеты)',
        callback_data='payment')
    keyboard: list[list[InlineKeyboardButton]] = [
        [nochild_btn],
    ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)

    await callback.message.answer(
        text='введите количество ваших детей',
        reply_markup=markup
    )
    await state.set_state(ChildState.number_of_children)


@router.message(ChildState.number_of_children)
async def before_spouse_number_of_children(message: Message, state: FSMContext):
    await state.update_data(number_of_children=message.text)
    if int(message.text) == 0:
        await message.answer(
            text="анкета заполнена!",
        )
        await state.clear()
    else:
        unknowncity_btn: InlineKeyboardButton = InlineKeyboardButton(
            text='продолжить заполнять анкету на детей',
            callback_data='next_child')
        keyboard: list[list[InlineKeyboardButton]] = [
            [unknowncity_btn],
        ]
        markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=keyboard)
        await message.answer(
            text=f"количество ваших детей: {message.text}, вам нужно заполнить анкету на ваших детей.",
            reply_markup=markup
        )


@router.callback_query(F.data == 'next_child')
async def spouse_number_of_children(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    print(data)
    # ТУТ НАДО ДОБАВИТЬ ЛОГИКУ ДЛЯ СОХРАНЕНИЯ ДАННЫХ В БАЗУ
    await callback.message.answer(
        text=f"введите имя вашего ребенка",
    )

    await state.set_state(ChildState.name)


@router.message(ChildState.name)
async def child_surname(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(
        text='введите фамилию вашего ребенка'
    )
    await state.set_state(ChildState.surname)


@router.message(ChildState.surname)
async def child_birthdate(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer(
        text="укажите дату рождения вашего ребенка",
    )
    await state.set_state(ChildState.birth_date)


@router.message(ChildState.birth_date)
async def child_gender(message: Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await message.answer(
        text="укажите пол вашего ребенка",
        reply_markup=get_gender_button()
    )
    await state.set_state(ChildState.gender)


@router.callback_query(ChildState.gender)
async def child_birth_city(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)

    unknowncity_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='город рождения не известен',
        callback_data='child_unknowncity')
    keyboard: list[list[InlineKeyboardButton]] = [
        [unknowncity_btn],
    ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)

    await callback.message.answer(
        text="укажите город рождения вашего ребенка",
        reply_markup=markup,
    )
    await state.set_state(ChildState.birth_city)


@router.message(ChildState.birth_city)
async def spouse_birth_country(message: Message, state: FSMContext):
    await state.update_data(birth_city=message.text)
    await message.answer(
        text="укажите страну рождения вашего ребенка",
    )
    await state.set_state(ChildState.birth_country)


@router.message(ChildState.birth_country)
async def spouse_photo(message: Message, state: FSMContext):
    await state.update_data(birth_country=message.text)
    await message.answer(
        text="отправьте фотографию вашего ребенка",
    )
    await state.set_state(ChildState.upload_photo)


@router.message(ChildState.upload_photo)
async def child_download_photo(message: Message, bot: Bot, state: FSMContext):
    telegram_user_id = message.from_user.id
    unique_filename = str(uuid.uuid4())
    filename = f"{unique_filename}.jpg"
    user_directory = f"media/users/{telegram_user_id}/child/"
    os.makedirs(user_directory, exist_ok=True)
    photo_path = os.path.join(user_directory, filename)

    await bot.download(
        message.photo[-1],
        destination=photo_path
    )

    await state.update_data(photo_url=photo_path)
    # ОТНИМАЕМ ОТ number_of_children ОДИН, ПОТОМ СОХРАНЯЕМ number_of_children, И ПЕРЕДАЁМ ЗНАЧЕНИЕ В ФУНКЦИЮ

    data = await state.get_data()
    number_of_children = data['number_of_children']
    remaining_number_of_children = int(number_of_children) - 1

    if remaining_number_of_children == 0:
        child_ok_btn: InlineKeyboardButton = InlineKeyboardButton(
            text='завершить заполнение анкеты',
            callback_data='payment')
        keyboard: list[list[InlineKeyboardButton]] = [
            [child_ok_btn],
        ]


    else:
        unknowncity_btn: InlineKeyboardButton = InlineKeyboardButton(
            text='продолжить заполнять анкету на детей',
            callback_data='next_child')
        keyboard: list[list[InlineKeyboardButton]] = [
            [unknowncity_btn],
        ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)

    await message.answer(
        text=f"количество анкет на детей, которое вам осталось заполнить: {remaining_number_of_children}",
        reply_markup=markup
    )

    await state.update_data(number_of_children=remaining_number_of_children)


@router.callback_query(F.data == 'payment')
async def payment(callback: CallbackQuery):

    text = ('Вы заполнили анкету для участия в green card 2023! После оплаты вы сможете посмотреть вашу анкету и'
            ' отредактировать её при необходимости!')
    payment_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='оплата',
        callback_data='payment_done')
    keyboard: list[list[InlineKeyboardButton]] = [
        [payment_btn],
    ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)
    await callback.message.answer(
        text,
        reply_markup=markup
    )


@router.callback_query(F.data == 'payment_done')
async def editing_data(callback: CallbackQuery):
    telegram_user_id = callback.from_user.id
    data = users_manager.get_user_by_telegram_id(telegram_user_id)
    print(data)
    photo_url = data['photo_url']

    await callback.message.answer(
        text=f'''
Пожалуйста, проверьте правильность заполнения вашей анкеты
имя = {data['name']}
фамилия = {data['surname']}
пол = {data['gender']}
уровень образования = {data['education_level']}
семейный статус = {data['marital_status']}
день рождения = {data['birth_date']}
город рождения = {data['birth_city']}
страна рождения = {data['birth_country']}
допущена ли страна до участия в green card = {data['eligibility']}
выбранная страна если нет допуска = {data['country_claiming_eligibility']}
адрес = {data['address_line_1']}
город = {data['city']}
район = {data['district']}
страна = {data['country']}
        '''
    )

    photo = FSInputFile(path=photo_url)
    await callback.message.answer_photo(
        photo=photo,
        caption='ваше фото',
    )
    await callback.message.answer(
        text='если в анкете есть неточности, нажмите на одну из соответствующих кнопок',
        reply_markup=get_user_edit_button()
    )

    if data['marital_status'] == 'Married and my spouse is NOT a U.S.citizen':
        spouse_data = spouse_manager.get_spouse_by_telegram_id(telegram_user_id)

        await callback.message.answer(
            text=f'''
        Пожалуйста, проверьте правильность заполнения анкеты вашего супруга
        имя = {spouse_data['name']}
        фамилия = {spouse_data['surname']}
        пол = {spouse_data['gender']}
        день рождения = {spouse_data['birth_date']}
        город рождения = {spouse_data['birth_city']}
        страна рождения = {spouse_data['birth_country']}
                '''
        )

        spouse_photo_url = spouse_data['photo_url']

        photo = FSInputFile(path=spouse_photo_url)

        await callback.message.answer_photo(
            photo=photo,
            caption='фото вашего супруга',
        )

@router.callback_query(F.data == 'user_name_edit')
async def user_name_edit(callback: CallbackQuery, state: FSMContext):
    telegram_user_id = callback.from_user.id
    await callback.message.answer(
        text="введите исправленное имя",
    )

    await state.set_state(UserEditState.name)


@router.message(UserEditState.name)
async def user_name_write(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    print(telegram_user_id)
    data = users_manager.get_user_by_telegram_id(telegram_user_id)
    print(data)
    print(message.text)
    name = message.text
    users_manager.write_name_by_telegram_id(telegram_user_id, name)

    text = ('имя исправлено!')
    payment_btn: InlineKeyboardButton = InlineKeyboardButton(
        text='вернуться к анкете',
        callback_data='payment_done')
    keyboard: list[list[InlineKeyboardButton]] = [
        [payment_btn],
    ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=keyboard)
    await message.answer(
        text,
        reply_markup=markup
    )

# @dp.message(F.contact)
# async def func_contact(msg: Message):
#     await msg.answer(f'Контакт:{msg.contact.phone_number}')