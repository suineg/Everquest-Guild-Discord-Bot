import datetime

from dateutil import tz


def to_kwargs(*arg_list):
    """Converts arg list ['key=value', ...] to dict {'KEY': 'VALUE', ...}"""

    if not arg_list:
        return None

    translations = {'>=': '=gte',
                    '<=': '=lte',
                    '>': '=gt',
                    '<': '=lt',
                    ':': '='}
    kwargs = {}
    for arg_string in arg_list:
        for op, translation in translations.items():
            if op in arg_string:
                arg_string.replace(op, translation)

        arg_list = arg_string.split('=')
        kwargs[arg_list[0].upper()] = arg_list[1].upper().split(',')
    return kwargs


def add_est_timestamp(string):
    """Converts a string to add a (timestamp) at the end of it"""

    if not string:
        return None

    now = datetime.datetime.now(tz=tz.gettz('America/New_York'))
    return f'{string} ({now.strftime("%I:%M %p")})'
