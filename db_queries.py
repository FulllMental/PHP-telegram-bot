import requests
from urllib.parse import urljoin
import sqlite3 as sq
from requests.auth import HTTPBasicAuth
from environs import Env
import json
import datetime


# ✅-- Способ проверки данных через API
def check_executor_api(user_id, login, password, server_url): # Нужен тг_ид и ид
    url = urljoin(server_url, 'executor')
    params = {
        "username": user_id
    }

    basic = HTTPBasicAuth(login, password)
    executors = requests.get(url, auth=basic, params=params)
    executors.raise_for_status()
    executor = json.loads(executors.content)
    if executor:
        return False, executor['id']
    return True, 0


# # -- Проверка исполнителя на наличие в БД
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


# ✅-- Способ получения данных через API
def get_orders_api(login, password, server_url): # На выходе список словарей
    url = urljoin(server_url, 'orders')
    payload = {
        "free": True
    }

    basic = HTTPBasicAuth(login, password)
    orders = requests.get(url, auth=basic, params=payload)
    orders.raise_for_status()
    return json.loads(orders.content)['results']


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


# ✅-- Отправка данных в БД по API
def push_order_api(login, password, server_url, approved_order):
    url = urljoin(server_url, f'orders/{approved_order["order_id"]}/')
    data = {
        'is_taken': approved_order['is_taken'],
        'estimate': approved_order['estimate'],
        'executor': urljoin(server_url, f'executors/{approved_order["executor_id"]}/'),
        'executor_tg_id': approved_order['executor_tg_id']
    }

    basic = HTTPBasicAuth(login, password)
    refresh_order = requests.patch(url, auth=basic, data=data)
    refresh_order.raise_for_status()


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


# ✅-- Получение заказов в работе по API
def get_inwork_orders_api(login, password, server_url, user_id):
    url = urljoin(server_url, 'orders')

    basic = HTTPBasicAuth(login, password)
    response = requests.get(url, auth=basic)
    response.raise_for_status()
    all_orders = json.loads(response.content)['results']
    return [order for order in all_orders if order['executor_tg_id'] == user_id and order['is_taken'] and not order['is_complete']]


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


# -- Отправка данных о завершении работы через API
def end_order_api(login, password, server_url, approved_order):
    url = urljoin(server_url, f'orders/{approved_order["end_order_id"]}/')
    data = {
        'is_complete': True,
        'complete_date': str(datetime.date.today()),
    }

    basic = HTTPBasicAuth(login, password)
    refresh_order = requests.patch(url, auth=basic, data=data)
    refresh_order.raise_for_status()


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


# ✅-- Получение ставки API
def get_rate_api(login, password, server_url):
    url = urljoin(server_url, 'actual-rate')

    basic = HTTPBasicAuth(login, password)
    rates = requests.get(url, auth=basic)
    rates.raise_for_status()
    return json.loads(rates.content)['rate']


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
    server_url = env('SERVER_URL')
    user_id = 406682076
    approved_order = {'executor_tg_id': 406682076, 'executor_id': 1, 'client_tg_id': 406682076, 'order_id': 2, 'estimate': '12 часов', 'is_taken': True, 'end_order_id': 1}
    # check_executor_api(user_id, login, password, server_url)
    # get_orders_api(login, password, server_url)
    # push_order_api(login, password, server_url, approved_order)
    # get_inwork_orders_api(login, password, server_url, user_id)
    # get_rate_api(login, password, server_url)
    # end_order_api(login, password, server_url)
    end_order_api(login, password, server_url)
