import time
import asyncio
import logging

from datetime import datetime
from datetime import timedelta

from sqlalchemy import select

from config import settings
from config.base import db_helper
from src.models import Simpleone
from src.services.notify import send_tg_notify
from src.services.notify import sla_new_task_notify
from simpleone.schemes import SimpleOneTask
from simpleone.schemes import TaskStateAlias


logging.basicConfig(
    level=logging.DEBUG,
    format='[{asctime}] {levelname: >8} : {name}:{funcName: <31} - {message}',
    style='{',
    filename='logs/sla_checker_service.log',
    filemode='a',
)

logger = logging.getLogger('simpleone_sla_checker')


async def main():
    logger.info('Старт sla checker')
    while True:
        async with db_helper.get_session() as db_session:
            current_time_utc = datetime.utcnow()
            one_hour_from_now = current_time_utc + timedelta(hours=1)
            stmt = (
                select(Simpleone)
                .where(Simpleone.sla_term > current_time_utc)
                .where(Simpleone.sla_term < one_hour_from_now)
                .where(Simpleone.state != TaskStateAlias.WAITING.value)
                .where(Simpleone.sla_alert_sending.is_(False))
            )
            result = await db_session.scalars(stmt)
            tasks = result.all()
            notify = []
            for task in tasks:
                # noinspection Pydantic
                notify.append(
                    await sla_new_task_notify(
                        SimpleOneTask.from_orm(task)
                    )
                )
                task.sla_alert_sending = True
                await db_session.flush()
            await db_session.commit()
        logger.debug('Сообщения для отправки: %s', notify)
        await send_tg_notify(settings.telegram.notify_chat_id, notify)
        time.sleep(300)
        await db_helper.dispose()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Работа скрипта остановлена')
