from functools import partial

from sqlalchemy import Column, Integer, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

NotNullColumn = partial(Column, nullable=False)


class Chunk(Base):
    __tablename__ = 'Chunks'

    def __init__(self, x: int, z: int, width: int, height: int, depth: int, data: bytes):
        self.x = x
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
        self.data = data

    id = Column(Integer, primary_key=True, index=True)
    x = NotNullColumn(Integer)
    z = NotNullColumn(Integer)
    data = NotNullColumn(LargeBinary)

    level_id = NotNullColumn(Integer, ForeignKey('Levels.id'))
    level = relationship('Level', back_populates='chunks', lazy='joined')

