import random
from typing import List

import sqlalchemy
from collections import Counter

import numpy as np
import pandas as pd
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models.character import Character

from src.models import Base, Monster
from src.stats import difficulty_dict, monster_cr_xp

NUM_MONSTERS_ = MAX_NUM_MONSTERS = 20


class Encounter(Base):

    __tablename__ = 'encounters'

    id = Column(Integer, primary_key=True)

    area_id = Column(Integer, ForeignKey('areas.id'))
    area = relationship('Area', back_populates='encounters')

    relative_freq = Column(Integer, default=1)

    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'encounters',
        'polymorphic_on': type,
    }

    def handle(self,
               session: sqlalchemy.orm.Session,
               characters: List[Character]):
        """
        Process this encounter and print relevant information to display.
        Args:
            session:
            characters:

        Returns:

        """

        raise NotImplementedError


class EncounterRoleplay(Encounter):

    __tablename__ = 'encounters_roleplay'

    id = Column(Integer, ForeignKey('encounters.id'), primary_key=True)

    description = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'encounters_roleplay',
    }

    def handle(self, *args):

        print('Roleplay:\n\n', self.description)


class EncounterCombat(Encounter):

    __tablename__ = 'encounters_combat'

    id = Column(Integer, ForeignKey('encounters.id'), primary_key=True)

    terrain = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'encounters_combat',
    }

    def handle(self,
               session,
               characters):

        if self.terrain:
            monsters = session.query(Monster).filter(getattr(Monster, self.terrain)).all()
        else:
            monsters = [assoc.monster for assoc in self.area.monster_assocs]

        if not monsters:
            raise NoMonstersFoundException

        cr_counts = Counter(m.cr for m in monsters)

        s_monster = pd.Series(monster_cr_xp)
        s_monster = s_monster[s_monster.index.isin(cr_counts)]

        df_monster_xp = pd.concat([s_monster] * MAX_NUM_MONSTERS, axis=1)
        df_monster_xp.columns += 1
        num_monsters = df_monster_xp.columns

        df_monster_xp *= df_monster_xp.columns
        encounter_multiplier = np.log(1 + num_monsters) / np.log(2)
        df_monster_xp *= encounter_multiplier
        s_monster_xps = df_monster_xp.stack()

        party_xp = sum(difficulty_dict[c.level] for c in characters)

        df_monster_prob = pdf_norm(df_monster_xp, party_xp, party_xp)

        s_num_prob = pd.Series(1 / num_monsters, index=num_monsters)

        factor_monster_type = np.log(np.e + df_monster_prob.index.map(cr_counts))

        df_probs = (df_monster_prob * s_num_prob).mul(factor_monster_type, axis=0)

        s_probs = df_probs.stack()

        (cr, num), monster_xp = random.choices(list(zip(s_probs.index, s_monster_xps)), weights=s_probs)[0]

        monster = random.choice([m for m in monsters if m.cr == cr])

        print('Combat: {} {} (cr: {}) (monsters: {}, party: {})'.format(
            num, monster.name, monster.cr, round(monster_xp), party_xp))

        if monster.description:
            print(monster.description)


def pdf_norm(data: pd.DataFrame,
             u: float,
             s: float):
    """
    Calculate the probability density for values.

    Args:
        data: 2-d data (e.g. DataFrame)
        u: Mean.
        s: Standard deviation.

    Returns:

    """

    z = (data - u) / s

    probs = np.exp(-z ** 2 / 2) / np.sqrt(2 * np.pi)

    return probs


class NoMonstersFoundException(Exception):
    pass
