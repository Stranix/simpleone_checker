import json
import logging

import aiohttp

from urllib.parse import urljoin

from aiohttp.web_exceptions import HTTPUnauthorized

from config import settings

logger = logging.getLogger('simpleone_client')


class Client:
    __token: str

    def __init__(self, token: str = ''):
        self.api = settings.simpleone.url
        self.user = settings.simpleone.user
        self.__password = settings.simpleone.password
        self.user_agent = settings.simpleone.user_agent
        self.__token = token

    async def send_get_request(self, url: str, params: dict | None = None):
        headers = {
            'User-Agent': self.user_agent,
            'Authorization': f'Bearer {self.__token}',
            'Content-Type': 'application/json',
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url,
                    headers=headers,
                    params=params,
                    ssl=False,
            ) as response:
                header_content_type = response.headers.get('Content-Type')
                logger.debug('response: %s', response.status)
                logger.debug('content-type: %s', header_content_type)
                if header_content_type.split(';')[0] == 'text/html':
                    logger.error('Что то пошло не так. Не верный тип ответа')
                    return
                if response.status == 401:
                    raise HTTPUnauthorized
                return await response.json()

    async def get_token(self):
        if self.__token:
            logger.info('Использую токен полученный ранее')
            return
        await self._token_from_api()
        with open('auth.json', 'w') as fp:
            json.dump({'api_token': self.__token}, fp, indent=4)

    async def _token_from_api(self):
        logger.info('Получаю новый токен')
        url = urljoin(self.api, 'auth/login')
        data = {
            'username': self.user,
            'password': self.__password,
            'language': 'ru',
        }
        logger.debug('url: %s', url)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url,
                    data=data,
                    ssl=False,
            ) as response:
                header_content_type = response.headers.get('Content-Type')
                logger.debug('response: %s', response.status)
                logger.debug('content-type: %s', header_content_type)
                response.headers.get('Content-Type')
                token = await response.json()
                logger.debug('token: %s', token)
                logger.debug('token: %s', token['data']['auth_key'])
                self.__token = token['data']['auth_key']
        logger.info('Токен получен')

    async def get_task_by_id(
            self,
            table_name: str,
            task_id: str,
            params: dict = None,
    ) -> dict:
        uri = urljoin(self.api, f'table/{table_name}/{task_id}')
        logger.debug('url: %s', uri)
        try:
            task_info = await self.send_get_request(uri, params)
        except HTTPUnauthorized:
            logger.info('Токен не подходит. Обновляю')
            self.__token = ''
            await self.get_token()
            task_info = await self.send_get_request(uri, params)
        return task_info['data'][0]

    async def get_tasks_by_filter(self, table_name: str, params: dict):
        url = urljoin(self.api, f'table/{table_name}')
        logger.debug('url: %s', url)
        params['sysparm_page'] = 1
        limit = params['sysparm_limit']
        tasks = []
        while True:
            logger.debug('Текущая страница %s', params['sysparm_page'])
            try:
                tasks_on_page = await self.send_get_request(url, params)
                tasks_on_page = tasks_on_page.get('data', [])
                if not tasks_on_page or len(tasks_on_page) < limit:
                    break
                tasks.extend(tasks_on_page)
                params['sysparm_page'] += 1
            except HTTPUnauthorized:
                logger.info('Токен не подходит. Обновляю')
                self.__token = ''
                await self.get_token()
                await self.get_tasks_by_filter(table_name, params)
        return tasks


def get_token_from_file():
    try:
        with open('auth.json') as auth_dump:
            auth = json.load(auth_dump)
            return auth.get('api_token', '')
    except FileNotFoundError:
        return ''


client = Client(token=get_token_from_file())
