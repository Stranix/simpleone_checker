from typing import Optional

from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from config.base import Base


class Simpleone(Base):
    active: Mapped[bool]
    number: Mapped[str] = mapped_column(unique=True)
    assignment_group: Mapped[str]
    attention_required: Mapped[bool]
    caller_department: Mapped[Optional[str]]
    company: Mapped[str]
    subject: Mapped[str]
    description: Mapped[Optional[str]]
    opened_at: Mapped[datetime]
    service: Mapped[str]
    additional_rem_configuration: Mapped[str]
    sla_due: Mapped[Optional[str]]
    state: Mapped[str]
    sys_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    contact_information: Mapped[str]
    max_processing_duration: Mapped[Optional[str]]
    out_of_sla: Mapped[bool]
    reason_for_waiting: Mapped[Optional[str]]
    reopen_counter: Mapped[int]
    sla_term: Mapped[Optional[datetime]]
    wait_untill: Mapped[Optional[datetime]]
    sla_alert_sending: Mapped[bool] = mapped_column(default=False)
