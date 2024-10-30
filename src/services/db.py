import logging

from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Simpleone
from simpleone.schemes import ChangedTask
from simpleone.schemes import SimpleOneTask

logger = logging.getLogger('simpleone_db')


async def save_task_in_db(
        task: SimpleOneTask,
        db_session: AsyncSession,
) -> Simpleone:
    logger.info('Сохраняю задача %r в базу', task.number)
    simpleone_task = Simpleone(**task.model_dump())
    db_session.add(simpleone_task)
    await db_session.commit()
    await db_session.refresh(simpleone_task)
    logger.info('Задача сохранена')
    # noinspection Pydantic
    return SimpleOneTask.from_orm(simpleone_task)


async def save_tasks_in_db(
        tasks: list[SimpleOneTask],
        db_session: AsyncSession,
):
    for task in tasks:
        logger.info('Сохраняю задача %r в базу', task.number)
        simpleone_task = Simpleone(**task.model_dump())
        db_session.add(simpleone_task)
    await db_session.commit()
    logger.info('Все задачи сохранены. Новых записей: %s', len(tasks))


async def check_task_in_db(
        task_number: str,
        db_session: AsyncSession,
) -> SimpleOneTask | None:
    logger.debug('Проверяю существует ли задача %r в базе', task_number)
    stmt = select(Simpleone).filter(Simpleone.number == task_number)
    simpleone_task = await db_session.scalars(stmt)
    simpleone_task = simpleone_task.first()
    if simpleone_task:
        logger.debug('Задача уже есть в базе')
        # noinspection Pydantic
        return SimpleOneTask.from_orm(simpleone_task)
    logger.warning('Задачи нет в базе')


async def update_task_in_base(task: SimpleOneTask, db_session: AsyncSession):
    logger.info('Сохраняю изменения по задаче в базе')
    task_number = task.number
    stmt = select(Simpleone).filter(Simpleone.number == task_number)
    task_on_db = await db_session.scalars(stmt)
    task_on_db = task_on_db.first()
    for field, value in task:
        setattr(task_on_db, field, value)

    await db_session.commit()
    await db_session.refresh(task_on_db)
    logger.info('Изменения сохранены!')
    return task_on_db


async def update_tasks_in_base(
        tasks: list[ChangedTask],
        db_session: AsyncSession,
):
    logger.info('Обновление информации в задачах')
    for changed_task in tasks:
        task_number = changed_task.task.number
        stmt = select(Simpleone).filter(Simpleone.number == task_number)
        task_on_db = await db_session.scalars(stmt)
        task_on_db = task_on_db.first()
        for field, value in changed_task.task:
            setattr(task_on_db, field, value)
    await db_session.commit()
    logger.info('Изменения сохранены! Измененных задач: %s', len(tasks))


async def delete_tasks_in_db(
        tasks: list[SimpleOneTask],
        db_session: AsyncSession,
):
    logger.info('Удаляю отсутствующие задачи из базы. %s', len(tasks))
    delete_stmt = (
        delete(Simpleone)
        .where(Simpleone.number.in_([task.number for task in tasks]))
    )
    await db_session.execute(delete_stmt)
    await db_session.commit()
    logger.info('Задачи удалены.')
