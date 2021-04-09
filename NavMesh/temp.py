import pickle

from api.models import Level
from api.models.database import SessionLocal
from io import BytesIO

import api.models

session = SessionLocal()

level = session.query(Level).get(2)

for chunk in level.chunks:

    buffer = BytesIO(chunk.data)

    filled_positions = pickle.load(buffer)

    new_positions = set()

    for x, y, z, v in filled_positions:

        if y >= 125:
            continue

        new_positions.add((x, y, z, v))

    new_buffer = BytesIO()

    pickle.dump(new_positions, buffer)

    chunk.data = new_buffer.getvalue()
    session.commit()