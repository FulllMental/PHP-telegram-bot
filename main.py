import logging
from random import choice

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from environs import Env

import markups as nav
from db_queries import check_executors, get_orders, push_order, get_rate, get_inwork_orders, end_order

env = Env()
env.read_env()
token = env('TELEGRAM_BOT_TOKEN')
token2 = env('CLIENT_TELEGRAM_TOKEN')

bot = Bot(token=token)
bot2 = Bot(token=token2)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    comment_to_client = State()  # Will be represented in storage as 'Form:comment_to_client'
    estimate = State() # Will be represented in storage as 'Form:estimate'


# -- Start bot --
@dp.message_handler(commands=['start'])
async def check_auth(message: types.Message):
    user_id = message.from_user.id
    flag, executor_id = check_executors(user_id, db_filename)
    if flag:
        await bot.send_message(user_id, f'Приветствую, {message.from_user.first_name}\n\n'
                               '🚧 Данный бот 🤖 работает, как подписочный сервис, к сожалению вы не были '
                               'найдены среди авторизованных пользователей 🚧,\n'
                               'НО, не отчаивайтесь, вы тоже можете воспользоваться сервисом, нажав на кнопку ниже...',
                               reply_markup=nav.payment_menu)

    else:
        await bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}! 👋\n'
                                                    'На данный момент у нас есть много новых заказов для вас\n'
                                                    '💻 Как насчёт немного поработать?', reply_markup=nav.worker_menu)
        all_orders.clear()
        all_orders.extend(get_orders(db_filename))
        print(f'список заказов на данный момент выглядит так {all_orders}')
        approved_order.update({'executor_tg_id': user_id, 'executor_id': executor_id})


# -- All message handlers
@dp.message_handler()
async def worker_routine(message: types.Message):
    if message.text == '📑 Выбрать заказ':
        chosen_order = choice(all_orders)
        await bot.send_message(message.from_user.id, text=f'Заявка номер {chosen_order[1]}\n'
                                                          f'<i>"{chosen_order[0]}"</i>',
                               parse_mode='HTML', reply_markup=nav.choice_menu)
        approved_order.update({'client_tg_id': int(chosen_order[2]),
                               'order_id': chosen_order[1]})
    elif message.text == '👌 Начать работу':
        await bot.send_message(message.from_user.id, '⚠Вы взяли данный заказ!⚠\n\n'
                                                     f'🔑<b>Ключи от админки:</b> \n <i>{project_keys}</i>\n\n'
                                                     '<b><i>На данный момент эти ключи - заглушка</i></b>\n\n'
                                                     'Желаем удачи! 👍', parse_mode='HTML', reply_markup=nav.worker_menu)
        approved_order.update({'is_taken': True})
        push_order(db_filename, approved_order)
        print('заказ закреплён за юзером', approved_order, sep='\n')

    elif message.text == '👈 Вернуться':
        await bot.send_message(message.from_user.id, 'Вы вернулись в главное меню без сохранения изменений ❗',
                               reply_markup=nav.worker_menu)

        print('принятие заказа отменено', approved_order, sep='\n')
    elif message.text == '❓ ЧаВо':
        await bot.send_message(message.from_user.id, 'Какие вопросы у вас возникли по пользованию ботом?',
                               reply_markup=nav.qna_menu)
    elif message.text == '🏆 Сдать заказ':
        user_id = message.from_user.id
        inwork_orders = get_inwork_orders(db_filename, user_id)
        if inwork_orders:
            await bot.send_message(message.from_user.id, f'На данный момент у вас в работе:\n')
            for order in inwork_orders:
                await bot.send_message(message.from_user.id, f'<b>заказ под номером:</b> {order[0]}\n'
                                                            f'<b>Описание заказа:</b> {order[1]}',
                                    parse_mode='HTML',
                                    reply_markup=nav.work_end_menu)
            approved_order.update({'end_order_id': inwork_orders[0][0]})
        else:
            await bot.send_message(message.from_user.id, "У вас нет заказов  в работе",
                                   parse_mode='HTML',
                                   reply_markup=nav.worker_menu)

    elif message.text == '🏁 Завершить заказ':
        end_order(db_filename, approved_order)
        await bot.send_message(message.from_user.id, 'Заказ завершён, если что-то будет не так, мы где ты живёшь ❗',
                               reply_markup=nav.worker_menu)
        approved_order.clear()


@dp.callback_query_handler(text='salary_btn')
async def comment_to_client(message: types.Message):
    rate = get_rate(db_filename)
    await bot.send_message(message.from_user.id, "💸 На данный момент стандартная ставка за 1им выполненный заказ составляет:\n\n"
                                                 f"<b>{rate}р.</b>",
                           parse_mode='HTML')


@dp.callback_query_handler(text='how_to_use')
async def comment_to_client(message: types.Message):
    await bot.send_message(message.from_user.id, '- Нажав на кнопку <b>"📑 Выбрать заказ"</b> - для вас подбирается заявка\n'
                                                 '- Нажав на кнопку <b>"📖 В работе"</b> вы можете посмотреть список своих текущих заказов')


# -- Take-Order InlineButton
@dp.callback_query_handler(text='take_order')
async def take_order(message: types.Message):
    await bot.send_message(message.from_user.id, f'Отлично, давайте уточним некоторые данные:\n\n'
                           '⏱ Напишите, сколько времени вам потребуется для выполнения\n',
                           reply_markup=nav.worker_menu)
    await Form.estimate.set()


@dp.message_handler(content_types=['text'], state=Form.estimate)
async def worker_routine(message: types.Message, state: FSMContext):
    logging.warning('worker_routine func!')
    async with state.proxy():
        await bot.send_message(message.from_user.id, 'Отлично! Осталось нажать <b>"👌 Начать работу"</b>'
                                                     ' заказ будет закреплён за вами и можно приступать.'
                                                     ' Или можно просто <b>"👈 Вернуться"</b> в меню',
                               parse_mode='HTML', reply_markup=nav.worker_begining_menu)
        approved_order.update({'estimate': message.text})
    await state.finish()


# -- Refuse to Take-Order InlineButton
@dp.callback_query_handler(text='no_take_order')
async def no_take_order(callback: types.CallbackQuery):
    await callback.message.delete()
    print(f'отказ от заказа {approved_order}')


# -- comment to client InlineButton
@dp.callback_query_handler(text='comment_to')
async def comment_to_client(message: types.Message):
    await bot.send_message(message.from_user.id, "💬 Ваше следующее сообщение будет отправлено клиенту")
    await Form.comment_to_client.set()


@dp.message_handler(content_types=['text'], state=Form.comment_to_client)
async def worker_comment(message: types.Message, state: FSMContext):
    logging.warning('worker_comment func!')
    async with state.proxy():
        client_tg_id = approved_order['client_tg_id']
        await bot2.send_message(client_tg_id, 'Здравствуйте, наш специалист собирается взяться за вашу заявку, '
                                          'но у него возникли вопросы.\n\n'
                                          '❓ <b>Вопрос звучит так:</b>\n'
                                          f'<i>"{message.text}"</i>\n\n'
                                          'Ответить вы можете через соответствующий функционал ниже',
                               parse_mode='HTML', reply_markup=nav.answer_menu)
        await bot.send_message(message.from_user.id, 'Сообщение было отправлено клиенту...')
    await state.finish()


if __name__ == '__main__':
    login = env('LOGIN')
    password = env('PASSWORD')
    db_filename = env('DB_FILENAME')
    client_bot_token = env('CLIENT_TELEGRAM_TOKEN')

    project_keys = 'Login: Big, Password: password' # -- Не реализовано, жду изменения бд

    all_orders = []
    approved_order = {}

    executor.start_polling(dp, skip_updates=True)
