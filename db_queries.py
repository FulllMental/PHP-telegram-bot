import requests
import ast
import sqlite3 as sq
from requests.auth import HTTPBasicAuth
from environs import Env
import json
import datetime


# -- Способ проверки данных через API
# def check_executor(user_id, login, password):
#     url = 'http://127.0.0.1:8000/executor/'
#     params = {
#         "username": user_id
#     }
#
#     basic = HTTPBasicAuth(login, password)
#     executors = requests.get(url, auth=basic, params=params)
#     executors.raise_for_status()
#     return bool(ast.literal_eval(executors.content.decode('utf-8')))


# -- Способ получения данных через API
# def get_orders(login, password):
#     url = 'http://127.0.0.1:8000/orders/'
#     payload = {
#         "free": True
#     }
#
#     basic = HTTPBasicAuth(login, password)
#     orders = requests.get(url, auth=basic, params=payload)
#     orders.raise_for_status()
#     answer = json.loads(orders.content)
#     for client_url in answer['results']:
#         client = requests.get(client_url['client'], auth=basic)
#         client.raise_for_status()
#         print(json.loads(client.content)['username'])


# -- Проверка исполнителя на наличие в БД
def check_executors(user_id, db_filename):
    with sq.connect(db_filename) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM controller_executor')
        result = cur.fetchall()
        cur.close()
    executors = [executor for executor in result]
    for executor in executors:
        if user_id == int(executor[1]):
            return False, executor[0]
        else:
            return True, 0


# -- Способ получения данных напрямую через файл БД (неважно включён ли сервер)
def get_orders(db_filename):
    with sq.connect(db_filename) as con:
        cur = con.cursor()
        cur.execute('SELECT text, id, client_tg_id '
                    'FROM controller_order '
                    'WHERE is_taken == 0')
        result = cur.fetchall()
        cur.close()
    return [list(order) for order in result]


# -- Отправка данных в БД
def push_order(db_filename, approved_order):
    with sq.connect(db_filename) as con:
        cur = con.cursor()
        cur.execute('UPDATE controller_order '
                    'SET is_taken=? ,estimate=? ,executor_id=?,  executor_tg_id=?'
                    'WHERE id=?',
                    (approved_order['is_taken'],
                     approved_order['estimate'],
                     approved_order['executor_id'],
                     approved_order['executor_tg_id'],
                     approved_order['order_id'])
                    )
        cur.close()


# -- Получение заказов в работе
def get_inwork_orders(db_filename, user_id):
    with sq.connect(db_filename) as con:
        cur = con.cursor()
        cur.execute('SELECT id, text '
                    'FROM controller_order '
                    f'WHERE is_complete == 0 and executor_tg_id == {user_id}')
        result = cur.fetchall()
        cur.close()
    return [list(order) for order in result]


# -- Отправка данных о завершении работы
def end_order(db_filename, approved_order):
    with sq.connect(db_filename) as con:
        cur = con.cursor()
        cur.execute('UPDATE controller_order '
                    'SET is_complete=? ,complete_date=? '
                    'WHERE id=?',
                    (True,
                     str(datetime.date.today()),
                     approved_order['end_order_id'])
                    )
        cur.close()

# -- Получение ставки
def get_rate(db_filename):
    with sq.connect(db_filename) as con:
        cur = con.cursor()
        cur.execute('SELECT rate '
                    'FROM controller_rate')
        current_rate = cur.fetchone()
        cur.close()
    return int(current_rate[0])


if __name__ == '__main__':
    env = Env()
    env.read_env()
    login = env('LOGIN')
    password = env('PASSWORD')
    db_filename = env('DB_FILENAME')


