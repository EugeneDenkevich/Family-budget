from aiogram.dispatcher.filters.state import State, StatesGroup


class Balance(StatesGroup):

    overal = State()
    daily = State()
    date = State()


class Buy(StatesGroup):

    buy = State()


class User(StatesGroup):

    login = State()
    password = State()