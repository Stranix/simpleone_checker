import pytz
import json
import logging

from datetime import datetime
from datetime import timezone
from datetime import timedelta

logger = logging.getLogger('simpleone_utils')


def format_to_moscow_time_as_str(utc_dt: datetime) -> str:
    if utc_dt is None:
        return ''
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    moscow_timezone = pytz.timezone('Europe/Moscow')
    moscow_time = utc_dt.astimezone(moscow_timezone)
    return moscow_time.strftime('%Y-%m-%d %H:%M:%S')


def load_from_json(file: str) -> dict | None:
    logger.info('Загружаю данные из файла %r', file)
    try:
        with open(file, 'r') as json_dump:
            return json.load(json_dump)
    except FileNotFoundError:
        logger.error('Не найден файл %s', file)


def create_parm_query_from_groups(groups: list, states: list) -> str:
    logger.info('Создаю строку для фильтрации заявок')
    assignment_groups = '^OR'.join(
        f'assignment_group={group_id}' for group_id in groups
    )
    state = '^OR'.join(f'state={state_id}' for state_id in states)
    parm_query = f'(active=1^({assignment_groups})^({state}))'
    logger.debug('parm_query -> %s', parm_query)
    logger.info('фильтр создан!')
    return parm_query


def sla_expires_within_hour(sla: str) -> bool:
    sla = datetime.strptime(sla, "%Y-%m-%d %H:%M:%S")
    sla = sla.replace(tzinfo=timezone.utc)

    moscow_tz = pytz.timezone("Europe/Moscow")
    current_time_moscow = datetime.now(moscow_tz)
    sla_moscow = sla.astimezone(moscow_tz)
    time_diff = sla_moscow - current_time_moscow

    if timedelta(hours=0) < time_diff <= timedelta(hours=1):
        return True
    return False
