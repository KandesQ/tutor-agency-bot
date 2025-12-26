from sqlalchemy import BigInteger, String, Date
from sqlalchemy.orm import mapped_column

from .Base import Base


class Tutor(Base):
    __tablename__ = "tutors"

    chat_id = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    surname = mapped_column(String(100), nullable=False)
    name = mapped_column(String(100), nullable=False)
    fathers_name = mapped_column(String(100), nullable=True)
    birthday_date = mapped_column(Date, nullable=False)

