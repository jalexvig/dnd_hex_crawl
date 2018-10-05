from src import models


def prompt_bool(prompt, default: bool):

    default_str = 'Y/n' if default else 'N/y'

    inp = input(prompt + ' [{}] '.format(default_str))

    if not inp or inp[0].lower() == default_str[0].lower():
        return default
    elif inp[0].lower() == default_str[-1].lower():
        return not default

    print('Cannot understand input: {}'.format(inp))

    raise MalformedBoolException


def prompt_choices(iterable, func, default=0, choices_suffix='', multiple=False):

    prompt = 'Select: [{}]\n'.format(default)
    prompt += '\n'.join(func(i, x) for i, x in enumerate(iterable))

    if choices_suffix:
        prompt += choices_suffix

    prompt += '\n'

    res = input(prompt)

    max_ = len(iterable) - 1
    if multiple:
        result = [validate_selection(x, default, max_) for x in res.split()]
    else:
        result = validate_selection(res, default, max_)

    return result


def validate_selection(s: str, default: int, max_: int):

    if not s:
        return default

    try:
        x = int(s)
    except ValueError:
        print('Invalid input: {}'.format(s))
        raise MalformedInputException
    else:
        if x > max_:
            print('Selection must be one of choices (not {})'.format(x))
            raise MalformedInputException

        return x


def get_area(session, area_str):

    areas = session.query(models.Area).filter(models.Area.name == area_str).all()

    if not areas:
        raise AreaNotFoundException

    idx = prompt_choices(areas, lambda i, area: '  {} - {} ({})'.format(i, area.name, area.full_name()))

    area = areas[idx]

    return area


class MalformedBoolException(Exception):
    pass


class MalformedInputException(Exception):
    pass


class AreaNotFoundException(Exception):
    pass
