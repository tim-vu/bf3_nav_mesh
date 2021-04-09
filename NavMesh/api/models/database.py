import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URl = 'sqlite:///' + os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir, os.pardir, 'db.sqlite3'))

engine = create_engine(
    SQLALCHEMY_DATABASE_URl, connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


