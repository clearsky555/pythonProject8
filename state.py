from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    education_level = State()
    marital_status = State()
    name = State()
    surname = State()
    gender = State()
    birth_date = State()
    birth_city = State()
    birth_country = State()
    eligibility = State()
    country_claiming_eligibility = State()
    upload_photo = State()
    address_line_1 = State()
    city = State()
    district = State()
    country = State()