import logging

from typing import Any

from pydantic import ValidationError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from config.base import db_helper

from src.services import db
from src.services import notify
from src.models import Simpleone
from simpleone import schemes
from simpleone.Client import client
from src.utils import create_parm_query_from_groups


logger = logging.getLogger('simpleone_services')


async def get_new_task_from_groups(
        groups: dict,
        req_params: dict,
) -> list[schemes.SimpleOneTask]:
    """Получаем новые задачи из заданных групп по статусам"""
    tasks = []
    for group in groups:
        req_params['sysparm_query'] = create_parm_query_from_groups(
            group['our_groups'],
            [
                state.value
                for state in schemes.TaskState
                if state != schemes.TaskState.COMPLETED
            ],
        )
        tasks.extend(
            await client.get_tasks_by_filter(group['table'], req_params)
        )
    logger.info('Получено обращений: %s', len(tasks))
    return await validate_tasks(tasks)


async def validate_tasks(tasks: list) -> list[schemes.SimpleOneTask]:
    validated_tasks = []
    logger.info('Валидирую задачи')
    for task in tasks:
        try:
            validated_tasks.append(schemes.SimpleOneTask(**task))
        except ValidationError as error:
            logger.error(error)
    return validated_tasks


async def tasks_sorting(
        tasks: list[schemes.SimpleOneTask],
        db_session: AsyncSession,
) -> schemes.SortedTasks:
    """Сортируем заявки:
    Новые - для записи в базу.
    Измененные - измененные заявки для обновления информации в базе.
    Без изменений - заявки без изменений."""
    logger.info('Запуск сортировки задач')
    sorted_tasks = schemes.SortedTasks()
    for task_in_api in tasks:
        task_in_db = await db.check_task_in_db(task_in_api.number, db_session)
        if task_in_db is None:
            sorted_tasks.new.append(task_in_api)
            continue
        changed_fields = await check_task_changes(
            task_in_db=task_in_db,
            task_in_api=task_in_api,
        )
        if not changed_fields:
            logger.info('Задача %r не изменена', task_in_api.number)
            sorted_tasks.not_changed.append(task_in_db)
            continue
        logger.warning('Задача %r изменилась', task_in_api.number)
        changed_task = schemes.ChangedTask(task_in_api, changed_fields)
        sorted_tasks.changed.append(changed_task)
    logger.info('Сортировка успешно завершена!')
    return sorted_tasks


async def fetch_simpleone_tasks(groups: dict, req_params: dict):
    logger.info('Собираю информацию по задачам')
    notifications = []
    tasks = await get_new_task_from_groups(groups, req_params)
    async with db_helper.get_session() as db_session:
        sorted_tasks = await tasks_sorting(tasks, db_session)
        for new_task in sorted_tasks.new:
            if not new_task.attention_required:
                continue
            notifications.append(await notify.new_task_notify(new_task))
        await db.save_tasks_in_db(sorted_tasks.new, db_session)

        await db.update_tasks_in_base(sorted_tasks.changed, db_session)

        tasks_for_closing = await get_missing_tasks(tasks, db_session)
        await db.delete_tasks_in_db(tasks_for_closing, db_session)

        logger.debug('message_for_send: %s', '\n'.join(notifications))
        await notify.send_tg_notify(
            settings.telegram.dispatchers_chat_id,
            notifications,
        )
    return sorted_tasks


async def check_task_changes(
        *,
        task_in_db: schemes.SimpleOneTask,
        task_in_api: schemes.SimpleOneTask
) -> dict[str, Any]:
    """Проверяем изменения в задаче"""
    changed_fields = {}
    for field, value in task_in_db.dict().items():
        if field == 'sla_alert_sending':
            continue
        api_value = task_in_api.dict().get(field)
        if api_value != value:
            changed_fields[field] = {'db_value': value, 'api_value': api_value}
    return changed_fields


async def get_missing_tasks(
        api_tasks: list[schemes.SimpleOneTask],
        db_session: AsyncSession,
) -> list[schemes.SimpleOneTask]:
    api_task_numbers = {task.number for task in api_tasks}
    stmt = (
        select(Simpleone)
        .where(Simpleone.state != schemes.TaskStateAlias.COMPLETED.value)
    )
    db_tasks = await db_session.scalars(stmt)
    db_tasks = db_tasks.all()
    missing_tasks = [
        task for task in db_tasks if task.number not in api_task_numbers
    ]
    logger.debug('missing_tasks: %s', len(missing_tasks))
    return missing_tasks


async def create_tasks_notify(tasks: list[schemes.ChangedTask]):
    """Определяем изменения по задаче и создаем уведомления"""
    notifications = []
    for task in tasks:
        logger.debug('Измененная задача %s', task.task)
        logger.debug('Измененная поля %s', task.changed_fields)
        changed_fields = task.changed_fields
        if 'state' in changed_fields:
            state_in_db = changed_fields['state']['db_value']
            state_in_api = changed_fields['state']['api_value']
            logger.debug('state_in_db: %s', state_in_db)
            logger.debug('state_in_api: %s', state_in_api)
            if state_in_db == 'Черновик' and state_in_api == '0':
                notification = await notify.task_reopen_notify(task.task)
                notifications.append(notification)

        if 'max_processing_duration' in changed_fields:
            notification = await notify.task_sla_change_notify(task.task)
            notifications.append(notification)

        if 'reason_for_waiting' in changed_fields:
            if changed_fields['reason_for_waiting']['api_value'] is None:
                notification = await notify.task_out_of_waiting_notify(
                    task.task,
                )
                notifications.append(notification)

    return notifications
