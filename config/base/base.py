from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declared_attr

from config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(self) -> str:
        return f'{camel_case_to_snake_case(self.__name__)}s'

    id: Mapped[int] = mapped_column(primary_key=True)


def camel_case_to_snake_case(input_str: str) -> str:
    chars = []
    for c_idx, char in enumerate(input_str):
        if c_idx and char.isupper():
            nxt_idx = c_idx + 1
            flag = nxt_idx >= len(input_str) or input_str[nxt_idx].isupper()
            prev_char = input_str[c_idx - 1]
            if prev_char.isupper() and flag:
                pass
            else:
                chars.append('_')
        chars.append(char.lower())
    return ''.join(chars)
