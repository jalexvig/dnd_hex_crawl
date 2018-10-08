import sqlalchemy.orm
from typing import List, Sequence, Callable, Union

from src import models


def prompt_bool(prompt: str,
                default: bool) -> bool:
    """
    Ask user yes or no question.

    Raises:
        MalformedBoolException: An error occured processing user inputs.
    """

    default_str = 'Y/n' if default else 'N/y'

    inp = input(prompt + ' [{}] '.format(default_str))

    if not inp or inp[0].lower() == default_str[0].lower():
        return default
    elif inp[0].lower() == default_str[-1].lower():
        return not default

    print('Cannot understand input: {}'.format(inp))

    raise MalformedBoolException


def prompt_choices(seq: Sequence,
                   func: Callable[[int, str], str],
                   default: int=0,
                   suffix_choices: str= '',
                   suffix_len: int=None,
                   multiple: bool=False) -> Union[int, List[int]]:
    """
    Asks user to choose from enumeration of options.

    Args:
        seq: Arbitrary Python objects to choose from.
        func: Transform object from seq into a str for selection.
        default: Index of default choice.
        suffix_choices: String to append to end of menu.
        suffix_len: Number of extra entries in suffix.
        multiple: Boolean indicating whether multiple options may be chosen (via space separated values).

    Returns:
        Choice(s).

    Raises:
        MalformedInputException
    """

    prompt = 'Select: [{}]\n'.format(default)
    prompt += '\n'.join(func(i, x) for i, x in enumerate(seq))

    if suffix_choices:
        prompt += suffix_choices

    prompt += '\n'

    res = input(prompt)

    max_ = len(seq) - 1

    if suffix_choices:
        if suffix_len is None:
            max_ += len(suffix_choices.strip().split())
        else:
            max_ += suffix_len

    if multiple:
        result = [validate_selection(x, default, max_) for x in res.split()]
    else:
        result = validate_selection(res, default, max_)

    return result


def validate_selection(s: str,
                       default: int,
                       max_: int) -> int:
    """
    Parse string selection.

    Raises:
        MalformedInputException
    """

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


def find_area(session: sqlalchemy.orm.Session,
              area_str: str) -> models.Area:
    """
    Find area from string name.

    Raises:
        AreaNotFoundException
    """

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


CharacterGroups = List[List[models.Character]]
