from sqlalchemy import BigInteger, String, Integer, Enum, ForeignKey, Numeric, DateTime
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
    lesson_date = mapped_column(DateTime(timezone=False), nullable=False)
    price = mapped_column(Numeric(10, 2), nullable=False)
    payment_status = mapped_column(Enum(PaymentStatus), nullable=False)

    # Ученик может не оплатить уже внесенное в базу занятие, поэтому nullable=True
    payment_date = mapped_column(DateTime(timezone=False), nullable=True)
    tutor_account_id = mapped_column(ForeignKey("tutors.account_id"), nullable=False)
