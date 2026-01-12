import re


def valid_fullname(fullname: str) -> bool:
    # 2 и более слов, только буквы (латиница + кириллица), разделенные пробелом
    pattern = r'^[А-Яа-яЁё]+( [А-Яа-яЁё]+)+$'

    return bool(re.match(pattern, fullname))

def valid_birth_date(birth_date: str) -> bool:
    # День.Месяц.Год
    pattern = r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d\d$"

    return bool(re.match(pattern, birth_date))