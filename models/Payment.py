from sqlalchemy import BigInteger, String, Integer, Enum, ForeignKey, Numeric
from sqlalchemy.orm import mapped_column

from .Base import Base
from .enums import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    id = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_surname = mapped_column(String(100), nullable=False)
    student_name = mapped_column(String(100), nullable=False)
    student_fathers_name = mapped_column(String(100), nullable=True)
    subject = mapped_column(String(100), nullable=False)
    lesson_number = mapped_column(Integer, nullable=False)
    price = mapped_column(Numeric(10, 2), nullable=False)
    payment_status = mapped_column(Enum(PaymentStatus), nullable=False)
    tutor_chat_id = mapped_column(ForeignKey("tutors.chat_id"), nullable=False)
