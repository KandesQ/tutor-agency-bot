from typing import List

from sqlalchemy import BigInteger, String, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base
from .payment import Payment


class Tutor(Base):
    __tablename__ = "tutors"

    chat_id = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    surname = mapped_column(String(100), nullable=False)
    name = mapped_column(String(100), nullable=False)
    fathers_name = mapped_column(String(100), nullable=True)
    birthday_date = mapped_column(Date, nullable=False)

    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="tutor")
