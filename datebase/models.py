from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from zoneinfo import ZoneInfo


def now_msk():
    return datetime.now(tz=ZoneInfo("Europe/Moscow"))


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_msk)
    count = mapped_column(BigInteger, default=0)

    def __repr__(self):
        return f"<User {self.user_id}>"
