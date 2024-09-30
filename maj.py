import sys
import json
import time
import requests
from datetime import datetime
from colorama import init, Fore, Style
from urllib.parse import unquote
import cloudscraper
import os
import pyrogram
from pyrogram import Client
from fake_useragent import UserAgent
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName


init(autoreset=True)


PROXY_TYPE = "socks5"  # http/socks5
USE_PROXY = True  # True/False
API_ID = 22579982  # апи
API_HASH = '2825cfd9be7a2b620e1753fa646cd3d6'
REF = '382695384'

class Data:
    def __init__(self, token):
        self.token = token

class PixelTod:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.DEFAULT_COUNTDOWN = (8 * 3600) + (5 * 60)  # Интервал между повтором скрипта, 8 часов 5 минут дефолт
        self.INTERVAL_DELAY = 10  # Интервал между каждым аккаунтом, 3 секунды дефолт
        self.base_headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": "https://webapp.cspr.community",
            "Referer": "https://webapp.cspr.community/",
            "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": "Android",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": UserAgent(os='android').random
        }
        self.ref = REF
        self.proxy = None

    def data_parsing(self, data):
        return {key: value for key, value in (i.split('=') for i in unquote(data).split('&'))}

    def main(self):
        action = int(input(f'{Fore.LIGHTBLUE_EX}Выберите действие:\n{Fore.LIGHTWHITE_EX}1. Начать фарм\n{Fore.LIGHTWHITE_EX}2. Создать сессию\n>'))

        if not os.path.exists('sessions'):
            os.mkdir('sessions')

        if action == 2:
            self.create_sessions()

        if action == 1:
            sessions = self.pars_sessions()
            accounts = self.check_valid_sessions(sessions)

            if not accounts:
                raise ValueError(f"{Fore.LIGHTRED_EX}Нет валидных сессий")


            while True:
                for idx, account in enumerate(accounts):
                    self.log(f'{Fore.LIGHTYELLOW_EX}Аккаунт {idx+1}: {Fore.LIGHTWHITE_EX}{account}')

                    if USE_PROXY:
                        proxy_dict = {}
                        with open('proxy.txt', 'r') as file:
                            proxy_list = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                            for prox, name in proxy_list:
                                proxy_dict[name] = prox
                        proxy = proxy_dict[account]
                        proxy_client = {
                            "scheme": PROXY_TYPE,
                            "hostname": proxy.split(':')[0],
                            "port": int(proxy.split(':')[1]),
                            "username": proxy.split(':')[2],
                            "password": proxy.split(':')[3],
                        }
                        prox = proxy_client
                        self.proxy = f"{PROXY_TYPE}://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"
                    else:
                        prox = None

                    data = self.get_tg_web_data(account, prox)
                    new_data = Data(data)
                    self.process_account(new_data)
                    print('-' * 50)
                    self.countdown(self.INTERVAL_DELAY)
                self.countdown(self.DEFAULT_COUNTDOWN)



    def process_account(self, data):
        self.login(data)
        self.leaderboard(data)
        self.task(data)

    def pars_sessions(self):
        sessions = []
        for file in os.listdir('sessions/'):
            if file.endswith(".session"):
                sessions.append(file.replace(".session", ""))

        self.log(f"{Fore.LIGHTYELLOW_EX}Найдено сессий: {Fore.LIGHTWHITE_EX}{len(sessions)}!")
        return sessions
    def create_sessions(self):
        while True:
            session_name = input(F'{Fore.LIGHTBLUE_EX}Введите название сессии (для выхода нажмите Enter)\n')
            if not session_name:
                return

            if USE_PROXY:
                proxy_dict = {}
                with open('proxy.txt', 'r') as file:
                    proxy_list = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                    for prox, name in proxy_list:
                        proxy_dict[name] = prox

                if session_name in proxy_dict:
                    proxy = proxy_dict[session_name]
                    proxy_client = {
                        "scheme": PROXY_TYPE,
                        "hostname": proxy.split(':')[0],
                        "port": int(proxy.split(':')[1]),
                        "username": proxy.split(':')[2],
                        "password": proxy.split(':')[3],
                    }

                    with pyrogram.Client(
                        api_id=API_ID,
                        api_hash=API_HASH,
                        name=session_name,
                        workdir="sessions/",
                        proxy=proxy_client
                    ) as session:
                        user_data = session.get_me()
                    self.log(f'{Fore.LIGHTYELLOW_EX}Добавлена сессия +{user_data.phone_number} @{user_data.username} PROXY {proxy.split(":")[0]}')
                else:

                    with pyrogram.Client(
                        api_id=API_ID,
                        api_hash=API_HASH,
                        name=session_name,
                        workdir="sessions/"
                    ) as session:


                        user_data = session.get_me()

                    self.log(f'{Fore.LIGHTYELLOW_EX}Добавлена сессия +{user_data.phone_number} @{user_data.username} PROXY : NONE')
            else:

                with pyrogram.Client(
                        api_id=API_ID,
                        api_hash=API_HASH,
                        name=session_name,
                        workdir="sessions/"
                ) as session:

                    user_data = session.get_me()

                self.log(f'{Fore.LIGHTYELLOW_EX}Добавлена сессия +{user_data.phone_number} @{user_data.username} PROXY : NONE')

    def check_valid_sessions(self, sessions: list):
        self.log(f"{Fore.LIGHTYELLOW_EX}Проверяю сессии на валидность!")
        valid_sessions = []
        if USE_PROXY:
            proxy_dict = {}
            with open('proxy.txt', 'r') as file:
                proxy_list = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                for prox, name in proxy_list:
                    proxy_dict[name] = prox
            for session in sessions:
                try:
                    if session in proxy_dict:
                        proxy = proxy_dict[session]
                        proxy_client = {
                            "scheme": PROXY_TYPE,
                            "hostname": proxy.split(':')[0],
                            "port": int(proxy.split(':')[1]),
                            "username": proxy.split(':')[2],
                            "password": proxy.split(':')[3],
                        }
                        client = Client(name=session, api_id=API_ID, api_hash=API_HASH, workdir="sessions/",
                                        proxy=proxy_client)

                        if client.connect():
                            valid_sessions.append(session)
                        else:
                            self.log(f"{Fore.LIGHTRED_EX}{session}.session is invalid")

                        client.disconnect()
                    else:
                        client = Client(name=session, api_id=API_ID, api_hash=API_HASH, workdir="sessions/")

                        if client.connect():
                            valid_sessions.append(session)
                        else:
                            self.log(f"{Fore.LIGHTRED_EX}{session}.session is invalid")
                        client.disconnect()
                except:
                    self.log(f"{Fore.LIGHTRED_EX}{session}.session is invalid")
            self.log(f"{Fore.LIGHTYELLOW_EX}Валидных сессий: {Fore.LIGHTWHITE_EX}{len(valid_sessions)}; {Fore.LIGHTYELLOW_EX}Невалидных: {Fore.LIGHTWHITE_EX}{len(sessions) - len(valid_sessions)}")

        else:
            for session in sessions:
                try:
                    client = Client(name=session, api_id=API_ID, api_hash=API_HASH, workdir="sessions/")

                    if client.connect():
                        valid_sessions.append(session)
                    else:
                        self.log(f"{session}.session is invalid")
                    client.disconnect()
                except:
                    self.log(f"{Fore.LIGHTRED_EX}{session}.session is invalid")
            self.log(f"{Fore.LIGHTYELLOW_EX}Валидных сессий: {Fore.LIGHTWHITE_EX}{len(valid_sessions)}; {Fore.LIGHTYELLOW_EX}Невалидных: {Fore.LIGHTWHITE_EX}{len(sessions) - len(valid_sessions)}")
        return valid_sessions

    def get_tg_web_data(self, account, prox):
        auth_url = None
        if USE_PROXY:
            client = Client(name=account, api_id=API_ID, api_hash=API_HASH, workdir="sessions/", proxy=prox)
        else:
            client = Client(name=account, api_id=API_ID, api_hash=API_HASH, workdir="sessions/")
        client.connect()
        try:
            bot = client.resolve_peer('csprfans_bot')
            app = InputBotAppShortName(bot_id=bot, short_name="CSPRfans")
            web_view = client.invoke(RequestAppWebView(
                    peer=bot,
                    app=app,
                    platform='android',
                    write_allowed=True,
                    start_param=self.ref
                ))
            auth_url = web_view.url
            json.loads((unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])))[5:].split('&chat_instance')[0])
            try:
                return unquote(auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            except IndexError:
                self.log(f"{Fore.LIGHTRED_EX}Invalid auth_url format: {auth_url}")
                return None
        except Exception as err:
            self.log(f"{err}")

        client.disconnect()


    def countdown(self, t):
        while t:
            one, two = divmod(t, 3600)
            three, four = divmod(two, 60)
            print(f"{Fore.LIGHTWHITE_EX}Ожидание до {one:02}:{three:02}:{four:02} ", flush=True, end="\r")
            t -= 1
            time.sleep(1)
        print("                          ", flush=True, end="\r")

    def api_call(self, url, data=None, headers=None, method='GET'):
        while True:
            try:
                if hasattr(self, 'proxy'):
                    proxy_dict = {
                        "http": self.proxy,
                        "https": self.proxy,
                    }
                else:
                    proxy_dict = None
                if method == 'GET':
                    res = self.scraper.get(url, headers=headers, proxies=proxy_dict)
                elif method == 'POST':
                    res = self.scraper.post(url, headers=headers, data=data, proxies=proxy_dict)
                else:
                    raise ValueError(f'Не поддерживаемый метод: {method}')
                if res.status_code == 401:
                    self.log(f'{Fore.LIGHTRED_EX}{res.text}')
                return res
            except (
            requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout):
                self.log(f'{Fore.LIGHTRED_EX}Ошибка подключения соединения!')
                continue

    def login(self, data: Data):
        url = "https://api.cspr.community/api/users/me"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.token}"
        res = self.api_call(url, headers=headers)

        if res.status_code == 200:
            try:
                result = res.json()
                user_data = result.get('user', {})
                point = result.get('points', {})
                user_name = user_data.get('username', 'Unknown Name')
                self.log(f'{Fore.LIGHTYELLOW_EX}Аккаунт: {Fore.LIGHTWHITE_EX}{user_name} ')
                self.log(f'{Fore.LIGHTYELLOW_EX}Поинты: {Fore.LIGHTWHITE_EX}{point} ')
                return user_data
            except Exception as e:
                self.log(f"{Fore.LIGHTRED_EX}Ошибка ключа: {e}")
        else:
            self.log(f"{Fore.LIGHTRED_EX}Ошибка авторизации: {res.status_code}")

    def leaderboard(self, data: Data):
        url = "https://api.cspr.community/api/airdrop-info?leaderboard_offset=0&leaderboard_limit=3"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.token}"

        params = {
            "leaderboard_offset": 0,
            "leaderboard_limit": 3
        }
        res = self.api_call(url, headers=headers, data=params)
        if res.status_code == 200:
            try:
                result = res.json()
                user_rank = result.get("ranking", {}).get("user_rank", {})
                user_points = user_rank.get("points", 0)
                user_position = user_rank.get("position", "N/A")
                if user_points and user_position:
                    self.log(f"{Fore.LIGHTYELLOW_EX}Ранг: {Fore.LIGHTWHITE_EX}{user_position}")
            except Exception as e:
                self.log(f"{Fore.LIGHTRED_EX}Ошибка лидерборда: {e}")
        else:
            self.log(f"{Fore.LIGHTRED_EX}ошибка лидерборда: {res.status_code}")


    def task(self, data: Data):
        self.log(f"{Fore.LIGHTYELLOW_EX}Начал проверку заданий")
        url = "https://api.cspr.community/api/users/me/tasks"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.token}"
        res = self.api_call(url, headers=headers)

        if res.status_code == 200:
            try:
                result = res.json()
                tasks = result.get('tasks', {})

                for category, task_list in tasks.items():
                    for task in task_list:
                        task_name = task.get('task_name')
                        sleep = task.get('seconds_to_allow_claim', 1)
                        if (task.get('claimed_at') is None or task.get('category') == 'daily') and task.get('category') != 'recruit':
                            url1 = "https://api.cspr.community/api/users/me/tasks"
                            headers = self.base_headers.copy()
                            headers["Authorization"] = f"Bearer {data.token}"
                            payload1 = {
                                "task_name": task_name,
                                "action": 0,
                                "data": {
                                    "date": datetime.utcnow().isoformat() + "Z"
                                }
                            }

                            res1 = self.api_call(url1, headers=headers, data=json.dumps(payload1), method='POST')

                            if res1.status_code == 200:
                                time.sleep(sleep+1)
                                payload2 = {
                                    "task_name": task_name,
                                    "action": 1,
                                    "data": {
                                        "date": datetime.utcnow().isoformat() + "Z"
                                    }
                                }
                                headers = self.base_headers.copy()
                                headers["Authorization"] = f"Bearer {data.token}"
                                res2 = self.api_call(url1, headers=headers, data=json.dumps(payload2), method='POST')
                                y = res2.json()
                                if not 'error' in y:
                                    self.log(f"{Fore.LIGHTYELLOW_EX}Выполнил задание: {Fore.LIGHTWHITE_EX}{task_name}")


            except Exception as e:
                self.log(f"{Fore.LIGHTRED_EX}Ошибка парсинга заданий: {e}")

    def log(self, message):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{Fore.LIGHTBLACK_EX}[{now}]{Style.RESET_ALL} {message}")



if __name__ == "__main__":
    try:
        app = PixelTod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()