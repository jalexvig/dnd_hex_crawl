from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


class Event(Base):

    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)

    name = Column(String)
    description = Column(String)

    triggers = relationship('Trigger', back_populates='event')


class Trigger(Base):

    __tablename__ = 'triggers'

    id = Column(Integer, primary_key=True)

    event_id = Column(Integer, ForeignKey('events.id'))
    event = relationship('Event', back_populates='triggers')

    resolved = Column(Boolean, default=False)

    area_id = Column(Integer, ForeignKey('areas.id'))

    party_lvl_min = Column(Integer)

    party_size = Column(Integer)

    # TODO(jalex): Add party composition/min number
