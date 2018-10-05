from src.utils import prompt_choices
from src.actions.utils import MalformedAction


def group(character_groups, group_idx):

    try:
        _group(character_groups, group_idx)
    except:
        raise MalformedAction


def _group(character_groups, idx_group):

    action = input('Action: ').lower()

    if action[0] == 's':
        character_groups = _split(character_groups, idx_group)
        return character_groups

    elif action[0] == 'm':
        character_groups, _ = _merge(character_groups, idx_group)
        return character_groups

    elif action[0] == 'r':
        character_groups = _remove(character_groups, idx_group)
        return character_groups


def _remove(character_groups, idx_group):

    idx = prompt_choices(character_groups,
                         lambda i, characters: '  {} - {}'.format(i, ', '.join(c.name for c in characters)),
                         default=idx_group)

    character_groups.pop(idx)

    return character_groups


def _split(character_groups, idx_group):

    idx_group = prompt_choices(character_groups,
                               lambda i, characters: '  {} - {}'.format(i, ', '.join(c.name for c in characters)),
                               default=idx_group)
    characters = character_groups[idx_group][:]
    new_groups = []
    i = 1
    while characters:
        print('Group {}'.format(i))
        idxs = prompt_choices(characters,
                              lambda i, char: '  {} - {} ({})'.format(i, char.name, char.player_name),
                              multiple=True)

        if not idxs:
            continue

        new_groups.append([characters[i] for i in idxs])

        for idx_pop in idxs:
            characters.pop(idx_pop)

        i += 1

    character_groups += new_groups
    character_groups.pop(idx_group)

    return character_groups


def _merge(character_groups, group_idx):

    idxs = prompt_choices(character_groups,
                          lambda i, characters: '  {} - {}'.format(i, ', '.join(c.name for c in characters)),
                          default=group_idx,
                          multiple=True)

    area = character_groups[idxs[0]].area
    new_char_group = character_groups[idxs[0]]

    for i in idxs[1:]:

        for c in character_groups[i]:
            c.area = area
            new_char_group.append(c)

    for i in idxs[1:]:
        character_groups.pop(i)

    return character_groups, idxs[0]
