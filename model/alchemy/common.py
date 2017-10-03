"""
Common objects for orm

base - Core orm class

engine - database engine object
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


engine = create_engine('sqlite:///:memory:', echo=False)