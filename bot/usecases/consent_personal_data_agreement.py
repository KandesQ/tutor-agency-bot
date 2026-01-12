from datetime import datetime, timezone, date
import logging
import os
from typing import Optional

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import insert
from models.UserConsent import UserConsent

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

async def consent_personal_data_agreement(user_account_id: int, db_session: AsyncSession) -> Optional[int]:
    consent_version = date.fromisoformat(os.getenv("CONSENT_VERSION"))


    st = insert(UserConsent).values(
        telegram_id=user_account_id,
        consent_version=consent_version,
        consented_at=datetime.now(timezone.utc),
    )

    try:
        await db_session.execute(st)

        await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        logger.error("Ошибка при сохранении пользовательского соглашения: %s", e)
        return -4

    return None