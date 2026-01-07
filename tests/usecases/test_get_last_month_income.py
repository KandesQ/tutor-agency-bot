import datetime
from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta

from bot.usecases.get_last_month_income import get_last_month_income
from models import Payment, Tutor
from models.enums import PaymentStatus


@pytest.mark.asyncio
async def test_get_last_month_income(db_session):
    test_tutor = Tutor(
        account_id=20,
        surname="test",
        name="test",
        fathers_name="test",
        birthday_date=datetime.datetime.now(),

    )
    db_session.add(test_tutor)
    await db_session.flush()

    first_day_of_this_month = datetime.datetime.today().replace(day=1)
    first_day_of_prev_month = first_day_of_this_month - relativedelta(months=1)

    last_month_payments = [
        Payment(
            student_surname="test",
            student_name="test",
            student_fathers_name="test",
            subject="test",
            lesson_number=1,
            lesson_date=datetime.datetime.now(),
            price=500,
            payment_status=PaymentStatus.PAID,
            payment_date=first_day_of_prev_month,
            tutor_account_id=test_tutor.account_id,
        ),
        Payment(
            student_surname="test",
            student_name="test",
            student_fathers_name="test",
            subject="test",
            lesson_number=15,
            lesson_date=datetime.datetime.now(),
            price=1500,
            payment_status=PaymentStatus.PAID,
            payment_date=first_day_of_prev_month + datetime.timedelta(days=10),
            tutor_account_id=test_tutor.account_id,
        ),
        Payment(
            student_surname="test",
            student_name="test",
            student_fathers_name="test",
            subject="test",
            lesson_number=15,
            lesson_date=datetime.datetime.now(),
            price=1500,
            payment_status=PaymentStatus.NOT_PAID,
            payment_date=first_day_of_prev_month + datetime.timedelta(days=10),
            tutor_account_id=test_tutor.account_id,
        ),
        Payment(
            student_surname="test",
            student_name="test",
            student_fathers_name="test",
            subject="test",
            lesson_number=15,
            lesson_date=datetime.datetime.now(),
            price=1500,
            payment_status=PaymentStatus.PAID,
            payment_date=first_day_of_this_month,
            tutor_account_id=test_tutor.account_id,
        )
    ]

    db_session.add_all(last_month_payments)


    res = await get_last_month_income(test_tutor.account_id, db_session)

    assert res == Decimal(2000)


