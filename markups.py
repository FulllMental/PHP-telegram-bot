from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# -- Main menu --
client_btn = KeyboardButton('💼Клиент')
worker_btn = KeyboardButton('💻Подрядчик')
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(client_btn, worker_btn)

# -- QnA menu --
salary_btn = InlineKeyboardButton('💰 Об оплате', callback_data='salary_btn')
how_to_use = InlineKeyboardButton('💡 Как пользоваться', callback_data='how_to_use')
qna_menu = InlineKeyboardMarkup().add(salary_btn, how_to_use)

# -- Worker menu -- 📑
order_obtain_btn = KeyboardButton('📑 Выбрать заказ')
end_order_btn = KeyboardButton('🏆 Сдать заказ')
qna_btn = KeyboardButton('❓ ЧаВо')
worker_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(order_obtain_btn, end_order_btn).add(qna_btn)

# -- Start work menu
start_work_btn = KeyboardButton('👌 Начать работу')
back_btn = KeyboardButton('👈 Вернуться')
worker_begining_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(start_work_btn, back_btn)

# -- Inline menu --
reserve_order_btn = InlineKeyboardButton('✅ Взять заявку', callback_data='take_order')
delete_order_btn = InlineKeyboardButton('🚫 Отказаться', callback_data='no_take_order')
comments_to_client_btn = InlineKeyboardButton('💬 Коммент Клиенту', callback_data='comment_to')
choice_menu = InlineKeyboardMarkup().add(reserve_order_btn, delete_order_btn).row(comments_to_client_btn)

# -- Redirect --
payment_btn = InlineKeyboardButton('Купить подписку на сервис', url='dvmn.org')
payment_menu = InlineKeyboardMarkup().add(payment_btn)

# -- Answer menu --
# answer_btn = InlineKeyboardButton('💬 Коммент Клиенту', callback_data='comment_to')
answer_menu = InlineKeyboardMarkup().add(comments_to_client_btn)

# -- End work menu --
end_work_btn = KeyboardButton('🏁 Завершить заказ')
work_end_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(end_work_btn, back_btn)

