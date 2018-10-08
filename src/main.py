import sqlalchemy.orm

import src.actions.utils
from src import actions
from src.utils import find_area, AreaNotFoundException, CharacterGroups
from src.initialize import init


def main():

    character_groups, session = init()

    loop(session, character_groups)


def loop(session: sqlalchemy.orm.Session,
         character_groups: CharacterGroups):
    """
    Start REPL.
    """

    idx_group = 0

    while 1:

        characters = character_groups[idx_group]

        action = input('Action for {}: '.format(', '.join(c.name for c in characters))).lower()

        if not action:
            continue
        elif action[0] == 'm':
            try:
                actions.move(session, character_groups, idx_group)
            except AreaNotFoundException:
                print('Area not found. Try again.')
                continue
        elif action[0] == 'i':
            _, *area_name_list = action.split(maxsplit=1)
            if area_name_list:
                try:
                    area = find_area(session, area_name_list[0])
                except AreaNotFoundException:
                    print('Area not found. Try again.')
                    continue
            else:
                area = characters[0].location
            actions.info(area)
        elif action[0] == 'g':
            try:
                actions.group(character_groups, idx_group)
            except src.actions.MalformedAction as e:
                print('Malformed action.')
                continue
        elif action[0] == 's':
            # skip this group
            pass
        elif action[0] == 'q':
            # quit
            break
        else:
            print('Action not understood. Try again.')
            continue

        idx_group += 1
        idx_group %= len(character_groups)

    session.commit()


if __name__ == '__main__':

    main()
