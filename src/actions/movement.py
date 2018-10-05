from src import models
from src.utils import prompt_bool, get_area, MalformedBoolException
from src.actions.groups import _merge


def join_groups(character_groups, idx_group: int, area: models.Area):

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
                character_groups, idx_group = _merge(character_groups, idx_group)

        return idx_group

    return idx_group


def move(session, character_groups, idx_group):

    area_str = input('Which area? ')

    area = get_area(session, area_str)

    idx_group_new = join_groups(character_groups, idx_group, area)

    characters = character_groups[idx_group_new]

    process_triggers(session, characters, area)

    if area.type == 'hex':
        area.process_encounter(session, characters)


def process_triggers(session, characters, area):

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
