from io import BytesIO

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from openpyxl import Workbook

from models import Payment


async def get_all_students_report(
        tutor_account_id: int,
        db_session: AsyncSession
) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Оплаты"


    statement = select(Payment).where(Payment.tutor_account_id == tutor_account_id)
    payments = (await db_session.scalars(statement)).all()


    headers = [
        "Фамилия", "Имя", "Отчество",
        "Предмет", "Урок", "Цена урока",
        "Дата проведения", "Статус оплаты", "Дата оплаты"
    ]
    ws.append(headers)
    for payment in payments:
        ws.append([
            payment.student_surname,
            payment.student_name,
            payment.student_fathers_name if payment.student_fathers_name else "-",
            payment.subject,
            payment.lesson_number,
            payment.price,
            payment.lesson_date.strftime("%d.%m.%Y") if payment.lesson_date else "-",
            payment.payment_status.value,
            payment.payment_date.strftime("%d.%m.%Y") if payment.payment_date else "-"
        ])

    tmp_file = BytesIO()
    wb.save(tmp_file)
    tmp_file.seek(0)

    return tmp_file.read()