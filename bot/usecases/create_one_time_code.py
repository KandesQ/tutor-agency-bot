import os
import time
import jwt


def create_one_time_code() -> str:
    expiration = get_one_time_code_expiration_in_sec()
    exp = int(time.time()) + expiration
    JWT_SECRET = os.getenv("JWT_SECRET")

    return jwt.encode({"exp": exp, "type": "invite_tutor"}, JWT_SECRET, algorithm="HS256")


def get_one_time_code_expiration_in_sec() -> int:
    return 10 * 60