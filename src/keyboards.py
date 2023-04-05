from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


start = InlineKeyboardMarkup(row_width=3)
purchase = InlineKeyboardButton(text='Покупка', callback_data='purchase')
savings = InlineKeyboardButton(text='Накопления', callback_data='savings')
change = InlineKeyboardButton(text='Изменить', callback_data='change')
start.add(purchase, savings, change)


choose_change = InlineKeyboardMarkup(row_width=3)
overal = InlineKeyboardButton(text='Общий', callback_data='change_overal')
daily = InlineKeyboardButton(text='Суточный', callback_data='change_daily')
back = InlineKeyboardButton(text='Назад', callback_data='back')
choose_change.add(overal, daily).add(back)


cancel = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text='Отмена',callback_data='cancel'))

registration = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text='Войти', callback_data='Enter'),
    InlineKeyboardButton(text='Регистрация', callback_data='register')
)