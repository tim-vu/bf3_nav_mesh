import enum
from functools import partial

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from .database import Base

NotNullColumn = partial(Column, nullable=False)


class Level(Base):
    __tablename__ = 'Levels'

    id = Column(Integer, primary_key=True, index=True)
    name = NotNullColumn(String)
    bf3_level = NotNullColumn(String)

    voxel_width = NotNullColumn(Integer)
    voxel_height = NotNullColumn(Integer)
    voxel_depth = NotNullColumn(Integer)

    chunk_voxel_height = NotNullColumn(Integer)
    chunk_height_offset = NotNullColumn(Integer)

    chunks = relationship('Chunk', back_populates='level')
