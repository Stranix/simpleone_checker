import time
import asyncio
import logging
import argparse

from config.base import db_helper

from src.utils import load_from_json
from simpleone.services import fetch_simpleone_tasks


logger = logging.getLogger('simpleone_fetch')

logging.basicConfig(
    level=logging.DEBUG,
    format='[{asctime}] {levelname: >8} : {name}:{funcName: <31} - {message}',
    style='{',
)


def create_arg_parser():
    description = 'Загрузка задач из SimpleOne'

    arg_parser = argparse.ArgumentParser(description=description)

    arg_parser.add_argument('--groups', default='our_groups.json', metavar='',
                            type=str,
                            help='''Путь до файла с указанием того заявки 
                            каких групп надо получать и из каких таблиц.
                            Значение по умолчанию  our_groups.json '''
                            )

    arg_parser.add_argument('--req_params', default='req_params.json',
                            metavar='', type=str,
                            help='''Путь до файла с параметрами запроса. 
                            Значение по умолчанию  req_params.json '''
                            )

    return arg_parser


async def main():
    logger.setLevel(logging.DEBUG)
    parser = create_arg_parser()
    args = parser.parse_args()
    logger.debug('argparse %s', args)

    groups_file = args.groups
    req_params_file = args.req_params

    groups = load_from_json(groups_file)
    req_params = load_from_json(req_params_file)

    while True:
        logger.info('Собираю заявки из simpleone')
        await fetch_simpleone_tasks(groups, req_params)
        logger.info('Пауза на 5 минут!')
        time.sleep(5 * 60)
        await db_helper.dispose()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Работа скрипта остановлена')
