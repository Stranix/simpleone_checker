import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.default import DefaultBotProperties

from config import settings
from simpleone.schemes import SimpleOneTask
from src.utils import format_to_moscow_time_as_str

logger = logging.getLogger('simpleone_notify')


async def sla_new_task_notify(task: SimpleOneTask) -> str:
    """Отложенная задача по отслеживанию сла"""
    logger.debug('Создаю уведомление о sla задачи %r', task.number)
    sla = format_to_moscow_time_as_str(task.sla_term)
    notify = (
        f'У заявки <code>{task.number}</code> истекает срок SLA\n'
        f'Выполнить до: <code>{sla}</code>\n\n'
    )
    logger.debug('notify: %s', notify)
    return notify


async def new_task_notify(task: SimpleOneTask) -> str:
    """Уведомление о новой задаче с отметкой крит или не крит"""
    logger.debug('Создаю уведомление о новой задаче %r', task.number)
    notify = ''
    opened__at = format_to_moscow_time_as_str(task.opened_at)
    sla = format_to_moscow_time_as_str(task.sla_term)
    if task.attention_required:
        notify += '!!! КРИТ !!!\n\n'
    notify += (
        f'Зафиксировал новое обращение <code>{task.number}</code>\n'
        f'Рабочая группа: <code>{task.assignment_group}</code>\n'
        f'Время создания заявки: <code>{opened__at}</code>\n'
        f'Выполнить до: <code>{sla}</code>\n\n'
    )
    logger.debug('notify: %s', notify)
    return notify


async def task_out_of_waiting_notify(task: SimpleOneTask) -> str:
    """Уведомление по задаче вышедшей из ожидания"""
    logger.debug('Создание уведомления о выходе задачи из ожидания')
    sla = format_to_moscow_time_as_str(task.sla_term)
    notify = (
        f'Заявка <code>{task.number}</code> вышла из ожидания\n'
        f'Рабочая группа: <code>{task.assignment_group}</code>\n'
        f'Выполнить до: <code>{sla}</code>\n\n'
    )
    logger.debug('notify: %s', notify)
    return notify


async def task_sla_change_notify(task: SimpleOneTask) -> str:
    """Уведомление об изменении максимального sla задачи"""
    logger.debug('Создаю уведомление о изменении sla в задаче %r', task.number)
    sla = format_to_moscow_time_as_str(task.sla_term)
    notify = (
        f'У заявки <code>{task.number}</code> изменился SLA\n'
        f'Рабочая группа: <code>{task.assignment_group}</code>\n'
        f'Выполнить до: <code>{sla}</code>\n\n'
    )
    logger.debug('notify: %s', notify)
    return notify


async def task_reopen_notify(task: SimpleOneTask) -> str:
    """Уведомление о переоткрытии заявки"""
    logger.debug('Создаю уведомление о переоткрытии заявки %r', task.number)
    sla = format_to_moscow_time_as_str(task.sla_term)
    notify = (
        f'!!! заявку <code>{task.number}<code> переоткрыли\n'
        f'Рабочая группа: <code>{task.assignment_group}</code>\n'
        f'Выполнить до: <code>{sla}</code>\n\n'
    )
    logger.debug('notify: %s', notify)
    return notify


async def send_tg_notify(chat_id: int, notifications: list[str]):
    """Отправка уведомлений в телегу"""
    logger.info('Отправляю сообщения в телеграм')
    if not notifications:
        logger.debug('нет сообщений для отправки')
        return
    bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(
        token=settings.telegram.bot_token,
        default=bot_properties,
    )
    try:
        await bot.send_message(chat_id, '\n'.join(notifications))
    except TelegramBadRequest:
        logger.error('ошибка отправки сообщения', notifications)
    finally:
        await bot.session.close()
    logger.info('Сообщения отправлены')
