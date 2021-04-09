import json

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from api.models.database import Base, engine
from api.resources import levels

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(levels.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
