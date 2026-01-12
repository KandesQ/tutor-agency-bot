import datetime
from datetime import timezone

from models import Base
from sqlalchemy import BigInteger, Date, DateTime
from sqlalchemy.orm import mapped_column

class UserConsent(Base):
    __tablename__ = "personal_data_consents"

    telegram_id = mapped_column(BigInteger, primary_key=True)
    consented_at = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.datetime.now(tz=timezone.utc)
    )
    consent_version = mapped_column(Date, nullable=False)
