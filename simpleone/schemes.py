from enum import Enum

from datetime import datetime

from dataclasses import field
from dataclasses import dataclass

from pydantic import BaseModel
from pydantic import ConfigDict


class SimpleOneTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    active: bool
    number: str
    assignment_group: str
    attention_required: bool
    caller_department: str | None
    company: str
    subject: str
    description: str | None
    opened_at: datetime
    service: str
    additional_rem_configuration: str
    sla_due: str | None
    state: str
    sys_id: int
    contact_information: str
    max_processing_duration: str | None
    out_of_sla: bool
    reason_for_waiting: str | None
    reopen_counter: int
    sla_term: datetime | None
    wait_untill: datetime | None
    sla_alert_sending: bool = False


class TaskState(Enum):
    WAITING = '3'
    APPOINTED = '0'
    IN_PROGRESS = '2'
    COMPLETED = '7'


class TaskStateAlias(Enum):
    WAITING = 'В процессе'
    APPOINTED = '0'
    IN_PROGRESS = 'Доступна'
    COMPLETED = 'Черновик'


@dataclass
class ChangedTask:
    task: SimpleOneTask
    changed_fields: dict


@dataclass
class SortedTasks:
    new: list[SimpleOneTask] = field(default_factory=list)
    changed: list[ChangedTask] = field(default_factory=list)
    not_changed: list[SimpleOneTask] = field(default_factory=list)
