from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# -- Main menu --
client_btn = KeyboardButton('💼Клиент')
worker_btn = KeyboardButton('💻Подрядчик')
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(client_btn, worker_btn)

# -- QnA menu --
salary_btn = KeyboardButton('💰Об оплате')
how_to_use = KeyboardButton('💡Как пользоваться')
qna_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(salary_btn, how_to_use)

# -- Worker menu -- 📑
order_obtain_btn = KeyboardButton('📑Выбрать заказ')
in_work_orders_btn = KeyboardButton('📖В работе')
comments_to_client_btn = KeyboardButton('💬Написать Клиенту')
qna_btn = KeyboardButton('❓ЧаВо')
worker_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(order_obtain_btn, in_work_orders_btn,comments_to_client_btn, qna_btn)

# -- Inline menu --
reserve_order_btn = InlineKeyboardButton('✅Взять заявку')
delete_order_btn = InlineKeyboardButton('🚫Отказаться')
choice_menu = InlineKeyboardMarkup().add(reserve_order_btn, delete_order_btn)

# -- Block --
subsciption_btn = KeyboardButton('Купить подписку на сервис')
block_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(subsciption_btn)

# -- Redirect --
payment_btn = InlineKeyboardButton('Купить подписку на сервис', url='dvmn.org')
payment_menu = InlineKeyboardMarkup().add(payment_btn)
