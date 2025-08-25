
from sqlalchemy import Boolean, Column, Integer, String, DateTime 
from database import Base  

class Events(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(50), unique=True)
    genre_name = Column(String(50))
    event_datetime = Column(DateTime(timezone=True))
    description = Column(String(255), nullable=True)
