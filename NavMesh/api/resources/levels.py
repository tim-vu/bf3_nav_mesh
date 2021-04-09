import pickle
from http import HTTPStatus
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, conint, validator
from sqlalchemy.orm import Session
from starlette.responses import Response

from api.dependencies import get_db
from api.models.chunk import Chunk
from api.models.level import Level

router = APIRouter(prefix='/levels', dependencies=[Depends(get_db)])


class ChunkInfoModel(BaseModel):
    id: int
    x: int
    z: int
    width: int
    height: int
    depth: int


class LevelModel(BaseModel):
    id: int
    name: str
    bf3_level: str
    chunks: List[ChunkInfoModel]

    class Config:
        orm_mode = True


@router.get('', response_model=List[LevelModel])
def get_levels(db: Session = Depends(get_db)):
    return db.query(Level).all()


class CreateChunkModel(BaseModel):
    x: int
    z: int
    width: conint(gt=0)
    height: conint(gt=0)
    depth: conint(gt=0)
    data: str

    @validator('data')
    def data_must_have_correct_dimensions(cls, value, values):

        if 'width' not in values or 'height' not in values or 'depth' not in values:
            return value

        if len(value) != values['width'] * values['height'] * values['depth']:
            raise ValueError('data does not have the right dimensions')

        return value


def bitstring_to_sparsematrix(bitstring, width, height, depth):

    matrix = set()

    i = 0
    for x in range(width):
        for y in range(height):
            for z in range(depth):

                if bitstring[i] == '0':
                    continue

                matrix.add((x, y, z, int(bitstring[i])))

                i += 1

    buffer = BytesIO()

    pickle.dump(matrix, buffer)

    return buffer.getvalue()


@router.post('/{level_id}/chunks', status_code=204)
def add_chunk(level_id: int, chunk: CreateChunkModel, db: Session = Depends(get_db)):

    level = db.query(Level).filter(Level.id == level_id).first()

    if not level:
        raise HTTPException(status_code=404, detail='Level not found')

    if chunk.width != level.chunk_width or chunk.height != level.chunk_voxel_height or chunk.depth != level.chunk_depth:
        raise HTTPException(status_code=422, detail='data does not have the right dimensions')

    existing_chunk: Chunk = db.query(Chunk).filter(Chunk.x == chunk.x, Chunk.z == chunk.z, Chunk.level_id == level_id).first()

    data = bitstring_to_sparsematrix(chunk.data, level.chunk_width, level.chunk_voxel_height, level.chunk_depth)

    if existing_chunk:

        existing_chunk.data = data
        db.commit()
        return Response(status_code=HTTPStatus.NO_CONTENT.real)

    new_chunk = Chunk(chunk.x, chunk.z, chunk.width, chunk.height, chunk.depth, data, chunk.type)

    level.chunks.append(new_chunk)

    db.commit()

    return Response(status_code=HTTPStatus.NO_CONTENT.real)
