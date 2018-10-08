from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import models

import itertools

from src.utils import prompt_bool, prompt_choices, MalformedInputException, MalformedBoolException


def init():

    session = init_db()

    while 1:
        try:
            character_groups = init_characters(session)
        except MalformedInputException:
            continue
        break

    return character_groups, session


def init_db():

    engine = create_engine('sqlite:////Users/alex/projects/dnd_hex_crawl/db', echo=False)

    models.Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine)()

    return session


def init_characters(session):

    characters = []

    while 1:
        name = input('Character name: ')
        if not name:
            break

        chars = session.query(models.Character).filter(models.Character.name == name).all()

        if not chars:
            try:
                new_char = prompt_bool('New character?', False)
            except MalformedBoolException:
                continue

            if not new_char:
                continue

            player_name = input('Player name: ')

            char = models.Character(name=name, player_name=player_name)
        else:
            try:
                idx = prompt_choices(chars, lambda i, char: '  {} - {} ({})'.format(i, char.name, char.player_name))
            except MalformedInputException:
                continue
            char = chars[idx]

        default_lvl = char.level or 1
        try:
            char.level = int(input('Level: [{}] '.format(default_lvl)) or default_lvl)
        except ValueError:
            print('Supply integer level.')
            continue

        characters.append(char)

    character_groups = init_locations(session, characters)

    session.add_all(x for sl in character_groups for x in sl)
    session.commit()

    return character_groups


def _select_area(session, areas_chosen):

    if not areas_chosen:
        return _select_new_area(session)

    idx = prompt_choices(areas_chosen,
                         lambda i, char: '  {} - {} ({})'.format(i, area.name, area.full_name()),
                         choices_suffix='\n  {} - {}\n'.format('New area', len(areas_chosen)))

    if idx == len(areas_chosen):
        area = _select_new_area(session)
    else:
        area = areas_chosen[idx]

    return area


def _select_new_area(session):

    name = input('What is the name of the area? ')

    areas = session.query(models.Area).filter(models.Area.name == name)

    if not areas:
        print('No areas found by that name. Please try again.')
        return _select_new_area(session)

    idx = prompt_choices(areas, lambda i, area: '  {} - {} ({})'.format(i, area.name, area.full_name()))
    area = areas[idx]

    return area


def init_locations(session, characters):

    try:
        same_start = prompt_bool('Same starting location?', True)
    except MalformedBoolException:
        return init_locations(session, characters)

    if same_start:
        area = _select_new_area(session)
        for char in characters:
            char.location = area
    else:
        areas_chosen = []
        for char in characters:
            area = _select_area(session, areas_chosen)
            char.location = area
            areas_chosen.append(area)

    characters = sorted(characters, key=lambda char: char.location)

    characters = [list(chars) for area, chars in itertools.groupby(characters, lambda char: char.location)]

    return characters
