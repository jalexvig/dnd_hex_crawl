import random
from typing import List

import sqlalchemy

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import Character
from src.models.base import Base
from src.models.encounter import Encounter


class Area(Base):

    __tablename__ = 'areas'

    id = Column(Integer, primary_key=True)

    name = Column(String)
    description = Column(String)

    type = Column(String)

    parent_id = Column(Integer, ForeignKey('areas.id'))
    parent = relationship('Area', back_populates='children', remote_side=[id])
    children = relationship('Area', back_populates='parent')

    monster_assocs = relationship('MonsterAreaAssociation', back_populates='area')

    characters = relationship('Character', back_populates='location')

    encounters = relationship('Encounter', back_populates='area')

    # TODO(jalex): Make this a variable number of inheritance levels
    inherit_encounters = Column(Boolean, default=False)
    inherit_discount = Column(Float, default=1/2)

    def full_name(self):

        area = self
        names = []

        while area:
            names.append(area.name)
            area = area.parent

        return ' > '.join(reversed(names))

    @property
    def siblings(self):

        if not self.parent:
            return []

        siblings = [x for x in self.parent.children if x is not self]

        return siblings

    def process_encounter(self,
                          session: sqlalchemy.orm.Session,
                          characters: List[Character]):
        """
        Find encounter and print it.
        """

        try:
            encounter = self._choose_encounter()
        except NoEncountersFoundException:
            print('No encounters found for this area.')
        else:
            encounter.handle(session, characters)

    def _choose_encounter(self) -> Encounter:
        """
        Select an encounter for this area.

        Returns: Encounter.

        Raises:
            NoEncountersFoundException
        """

        area = self
        while area and not area.encounters:
            area = area.parent

        if not area:
            raise NoEncountersFoundException

        encounter_list = [area.encounters]
        weight_list = [[e.relative_freq for e in area.encounters]]
        discount = 1

        if area.inherit_encounters:
            while area.parent:
                area = area.parent
                discount *= area.inherit_discount
                if area.encounters:
                    encounter_list.append(area.encounters)
                    weight_list.append([e.relative_freq * discount for e in encounter_list[-1]])

        encounters = [e for sl in encounter_list for e in sl]
        weights = [w for sl in weight_list for w in sl]
        encounter = random.choices(encounters, weights)[0]

        return encounter

    def __lt__(self, other):

        return self.id < other.id


class NoEncountersFoundException(Exception):
    pass
