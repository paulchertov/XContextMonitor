"""
Common objects for orm

Base - Core orm class

LoginTokenPair - type for pair of login and token (common key
for Yandex API aggregated items

engine - database engine object
"""

from typing import Tuple


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
LoginTokenPair = Tuple[str, str]

engine = create_engine('sqlite:///db.db', echo=False)
