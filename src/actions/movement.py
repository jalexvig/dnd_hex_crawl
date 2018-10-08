from typing import List

import sqlalchemy

from src import models
from src.models import Character
from src.utils import prompt_bool, find_area, MalformedBoolException, CharacterGroups
from src.actions.groups import _merge_groups


def _join_groups(character_groups: CharacterGroups,
                 idx_group: int,
                 area: models.Area) -> int:
    """
    Join two collacted groups.

    Returns: Index of new combined group.
    """

    idxs_same = []

    for i, group in enumerate(character_groups):

        if i == idx_group:
            continue

        if group[0].location == area.id:

            idxs_same.append(i)

    if idxs_same:

        try:
            prompt_merge_bool = prompt_bool('Other groups in this area. Merge?', False)
        except MalformedBoolException:
            # don't handle this - can merge via cli if necessary
            pass
        else:
            if prompt_merge_bool:
                character_groups, idx_group = _merge_groups(character_groups, idx_group)

        return idx_group

    return idx_group


def move(session: sqlalchemy.orm.Session,
         character_groups: CharacterGroups,
         idx_group: int):
    """
    Move a group to a new area.
    """

    area_str = input('Which area? ')

    area = find_area(session, area_str)

    idx_group_new = _join_groups(character_groups, idx_group, area)

    characters = character_groups[idx_group_new]

    process_triggers(session, characters, area)

    if area.type == 'hex':
        area.process_encounter(session, characters)


def process_triggers(session: sqlalchemy.orm.Session,
                     characters: List[Character],
                     area: models.Area):
    """
    Find triggers for an area, print them, and potentially resolve them.
    """

    triggers = session.query(models.Trigger).filter(
        (~models.Trigger.resolved) &
        (models.Trigger.area_id == area.id) &
        (models.Trigger.party_lvl_min <= min(c.level for c in characters)) &
        (models.Trigger.party_size >= len(characters))
    ).all()

    events = [t.event for t in triggers]

    for event in events:
        print('Event: {}'.format(event.name))
        print(event.description)

        while 1:
            try:
                resolved_bool = prompt_bool('Resolved ?', True)
            except MalformedBoolException:
                continue
            break

        if resolved_bool:
            for t in event.triggers:
                t.resolved = True

    # TODO(jalex): Does this commit the triggers attached to the events?
    session.add_all(events)
    session.commit()
