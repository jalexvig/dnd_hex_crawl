from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


class Character(Base):

    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)

    name = Column(String)
    level = Column(Integer, default=1)

    location_id = Column(Integer, ForeignKey('areas.id'))
    location = relationship('Area', back_populates='characters')

    player_name = Column(String)
