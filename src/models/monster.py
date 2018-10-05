import enum

from sqlalchemy import Column, Boolean, Enum, Float, String
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.models import Base


class Monster(Base):

    __tablename__ = 'monsters'

    class Size(enum.Enum):

        tiny = 1
        small = 2
        medium = 3
        large = 4
        huge = 5
        gargantuan = 6

    id = Column(Integer, primary_key=True)

    name = Column(String)
    cr = Column(String)
    type = Column(String)
    size = Column(Enum(Size))

    alignment1 = Column(String)
    alignment2 = Column(String)

    description = Column(String)

    area_assocs = relationship('MonsterAreaAssociation', back_populates='monster')

    arctic = Column(Boolean)
    coastal = Column(Boolean)
    desert = Column(Boolean)
    forest = Column(Boolean)
    grassland = Column(Boolean)
    hill = Column(Boolean)
    mountain = Column(Boolean)
    swamp = Column(Boolean)
    underdark = Column(Boolean)
    underwater = Column(Boolean)
    urban = Column(Boolean)
    other_plane = Column(Boolean)

    def __str__(self):

        components = []

        for attr in ['name', 'cr', 'type', 'alignment1', 'alignment2', 'size']:
            if hasattr(self, attr):
                components.append((attr, getattr(self, attr)))

        terrains = []
        for attr in ['arctic', 'coastal', 'desert', 'forest', 'grassland', 'hill', 'mountain', 'swamp', 'underdark',
                     'underwater', 'urban', 'other_plane']:
            if getattr(self, attr):
                terrains.append(attr)

        components.append(('terrains', '-'.join(terrains)))

        return ', '.join(': '.join(map(str, tup)) for tup in components)


class MonsterAreaAssociation(Base):

    __tablename__ = 'monster_area'
    left_id = Column(Integer, ForeignKey('monsters.id'), primary_key=True)
    right_id = Column(Integer, ForeignKey('areas.id'), primary_key=True)

    area = relationship("Area", back_populates="monster_assocs")
    monster = relationship("Monster", back_populates="area_assocs")
