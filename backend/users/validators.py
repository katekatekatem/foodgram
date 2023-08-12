import re

from django.conf import settings
from django.core.exceptions import ValidationError


def symbols_validator(value):
    MESSAGE_SYMBOLS = 'Нельзя использовать символы: {}'
    invalid_simbols = ''.join(set(re.sub(r'([\w.@+-]+)', '', str(value))))
    if invalid_simbols:
        raise ValidationError(MESSAGE_SYMBOLS.format(invalid_simbols))
    return value


def names_validator_reserved(value):
    MESSAGE = 'Невозможно использовать {} в качестве имени пользователя.'
    for reserved_username in settings.RESERVED_USERNAMES:
        if value == reserved_username:
            raise ValidationError(MESSAGE.format(value))
    return value
