from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    BigInteger,
    Date,
    ForeignKey,
    select,
    text,
    desc,
    update,
)

from config import MYSQL_URL

engine = create_engine(MYSQL_URL)
meta = MetaData()


class UsersManager:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.user = self.get_users_schema()

    def get_users_schema(self):
        users = Table(
            'users', meta,
            Column('id', Integer, primary_key=True),
            Column('telegram_user_id', BigInteger),
            Column('name', String(100)),
            Column('surname', String(100)),
            Column('gender', String(50)),
            Column('birth_date', Date),
            Column('birth_city', String(100)),
            Column('birth_country', String(100)),
            Column('eligibility', String(50)),
            Column('country_claiming_eligibility', String(50), nullable=True),
            Column('photo_url', String(255)),
            Column('marital_status', String(100)),
            Column('city', String(255)),
            Column('address_line_1', String(255)),
            Column('district', String(100)),
            Column('country', String(100)),
            Column('education_level', String(100)),

            extend_existing=True
        )
        return users

    def create_table(self):
        meta.create_all(self.engine, checkfirst=True)

    def record_user_in_db(self, data):
        ins = self.user.insert().values(
            **data
        )
        with self.engine.connect() as connect:
            connect.execute(ins)
            connect.commit()

    def get_user_id_by_telegram_user_id(self, telegram_user_id):
        query = select(self.user.columns.id).where(self.user.columns.telegram_user_id == telegram_user_id).order_by(
            desc(self.user.columns.id))

        with self.engine.connect() as connect:
            result = connect.execute(query)
            row = result.first()
            if row:
                user_id = row[0]
            else:
                user_id = None
        return user_id

    def update_user_in_db(self, user_id, new_data):
        stmt = self.user.update().where(self.user.columns.id == user_id).values(**new_data)

        with self.engine.connect() as connect:
            connect.execute(stmt)
            connect.commit()

    def get_user_by_telegram_id(self, telegram_user_id):
        query = select(self.user).where(self.user.c.telegram_user_id == telegram_user_id).order_by(
            self.user.c.id.desc())

        with self.engine.connect() as connect:
            result = connect.execute(query)
            user_data = result.fetchone()
        return user_data._mapping


    # ФУНКЦИИ ДЛЯ ИЗМЕНЕНИЯ ДАННЫХ АНКЕТЫ
    def write_name_by_telegram_id(self, telegram_user_id, new_name):

        update_stmt = self.user.update().values(name=new_name).where(
            self.user.c.telegram_user_id == telegram_user_id)

        with self.engine.connect() as connect:
            connect.execute(update_stmt)
            connect.commit()


users_manager = UsersManager(engine=engine)


class SpouseManager:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.spouse = self.get_spouse_schema()

    def get_spouse_schema(self):
        spouses = Table(
            'spouses', meta,
            Column('id', Integer, primary_key=True),
            Column('telegram_user_id', BigInteger),
            Column('name', String(100)),
            Column('surname', String(100)),
            Column('gender', String(50)),
            Column('birth_date', Date),
            Column('birth_city', String(100)),
            Column('birth_country', String(100)),
            Column('photo_url', String(255)),
            Column('user_id', Integer, ForeignKey('users.id')),

            extend_existing=True
        )
        return spouses

    def create_table(self):
        meta.create_all(self.engine, checkfirst=True)

    def record_spouse_in_db(self, data):
        ins = self.spouse.insert().values(
            **data
        )
        with self.engine.connect() as connect:
            connect.execute(ins)
            connect.commit()

    def get_spouse_by_telegram_id(self, telegram_user_id):
        query = select(self.spouse).where(self.spouse.c.telegram_user_id == telegram_user_id).order_by(
            self.spouse.c.id.desc())

        with self.engine.connect() as connect:
            result = connect.execute(query)
            user_data = result.fetchone()
        return user_data._mapping

    def get_spouse_id_by_user_id(self, user_id):
        query = select(self.spouse).where(self.spouse.c.user_id == user_id).order_by(
            desc(self.spouse.columns.id))
        with self.engine.connect() as connect:
            result = connect.execute(query)
            row = result.first()
            if row:
                spouse_id = row[0]
            else:
                spouse_id = None
        return spouse_id

    def update_spouse_in_db(self, spouse_id, new_data):
        stmt = self.spouse.update().where(self.spouse.columns.id == spouse_id).values(**new_data)
        with self.engine.connect() as connect:
            connect.execute(stmt)
            connect.commit()


spouse_manager = SpouseManager(engine=engine)


class ChildManager:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.child = self.get_child_schema()

    def get_child_schema(self):
        spouses = Table(
            'children', meta,
            Column('id', Integer, primary_key=True),
            Column('telegram_user_id', BigInteger),
            Column('name', String(100)),
            Column('surname', String(100)),
            Column('gender', String(50)),
            Column('birth_date', Date),
            Column('birth_city', String(100)),
            Column('birth_country', String(100)),
            Column('photo_url', String(255)),
            Column('user_id', Integer, ForeignKey('users.id')),

            extend_existing=True
        )
        return spouses

    def create_table(self):
        meta.create_all(self.engine, checkfirst=True)

    def record_child_in_db(self, data):
        ins = self.child.insert().values(
            **data
        )
        with self.engine.connect() as connect:
            connect.execute(ins)
            connect.commit()

    def get_children_by_telegram_id(self, telegram_user_id):
        query = select(self.child).where(self.child.c.telegram_user_id == telegram_user_id).order_by(
            self.child.c.id.desc())

        with self.engine.connect() as connect:
            result = connect.execute(query)
            user_data = result.fetchall()
        return [user._mapping for user in
                user_data]


child_manager = ChildManager(engine=engine)