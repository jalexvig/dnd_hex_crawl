from src import models


def info(area: models.Area):

    indent = '  '

    print('Description: ', area.description)
    if area.parent:
        print('Parent:')
        print(indent, area.parent.name)
    if area.children:
        print('Children:')
        for child in area.children:
            print(indent, child.name)
    if area.siblings:
        print('Siblings:')
        for sib in area.siblings:
            print(indent, sib.name)
