from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select, and_

from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy.sql.functions import func

from models import Payment
from models.enums import PaymentStatus


async def get_last_month_income(tutor_account_id: int, session: AsyncSession) -> Decimal:
    first_day_of_this_month = date.today().replace(day=1)
    first_day_of_prev_month = first_day_of_this_month - relativedelta(months=1)

    st = (
        select(func.sum(Payment.price))
            .where(and_(
            Payment.tutor_account_id == tutor_account_id,
            Payment.payment_status == PaymentStatus.PAID,
            Payment.payment_date >= first_day_of_prev_month,
            Payment.payment_date < first_day_of_this_month
        ))
    )

    res = (await session.execute(st)).scalar()
    if not res:
        return Decimal(0)

    return Decimal(res)