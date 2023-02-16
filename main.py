import logging
from aiogram import Bot, Dispatcher, executor, types
from environs import Env
import markups as nav

env = Env()
env.read_env()
token = env('TELEGRAM_BOT_TOKEN')

bot = Bot(token=token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def check_auth(message: types.Message):
    if message.from_user.full_name == 'Арсений': # -- Проверка на нахождение в базе Клиентов/Исполнителей
        await bot.send_message(message.from_user.id, f'Приветствую, {message.from_user.id}\n\n'
                                                     'Данный бот 🤖 работает, как подписочный сервис, к сожалению вы не были '
                                                     'найдены среди авторизованных пользователей 🤐,\n'
                                                     'НО, не отчаивайтесь, вы тоже можете воспользоваться сервисом, нажав на кнопку ниже...',
                               reply_markup=nav.payment_menu)
    else:
        await bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}!\n'
                                                     f'Бип-боп 🤖 проверка прошла успешно, теперь вы в нашем закрытом клубе\n'
                                                     f'Первое правило бойц... бип-боп, в смысле выберите кем сегодня хотите быть', reply_markup=nav.main_menu)


@dp.message_handler()
async def choose_role(message: types.Message):
    if message.text == '💻Подрядчик':
        await bot.send_message(message.from_user.id, 'Хэй, пс, парень, работа нужна?!', reply_markup=nav.worker_menu)
    elif message.text == '💼Клиент':
        await bot.send_message(message.from_user.id, 'Решил, сделать коллективный проект в соляного?!\n'
                                                     'прости, но сегодня данная часть на реконструкции, так что делать придётся проект самому\n'
                                                     'http://sun9-12.userapi.com/c9450/g220358/a_dcfefe22.jpg')

@dp.message_handler()
async def worker_routine(message: types.Message):
    if message.text == '📑Выбрать заказ':
        await bot.send_message(message.from_user.id, 'Сделать сайт', reply_markup=nav.choice_menu)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
