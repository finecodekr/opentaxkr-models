from datetime import date, datetime

import dateutil.parser


class Model:
    def __setattr__(self, key, value):
        super().__setattr__(key, convert_type(value, self.__annotations__[key]))


def convert_type(value, to_type):
    if value is None:
        return value

    if isinstance(value, to_type):
        return value

    if (type(value), to_type) in TYPE_CONVERSION_MAP:
        return TYPE_CONVERSION_MAP[type(value), to_type](value)

    return to_type(value)


TYPE_CONVERSION_MAP = {
    (str, date): lambda value: dateutil.parser.parse(value).date(),
    (str, datetime): lambda value: dateutil.parser.parse(value),
    (str, bool): lambda value: value.lower() in ['true', 'y', 'yes', '1'],
}