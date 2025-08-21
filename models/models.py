
from sqlalchemy import Boolean, Column, Integer, String
from database import Base  

class Events(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(50), unique=True)
