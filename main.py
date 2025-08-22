
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated 
from datetime import datetime,timezone
import models
from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import logging # <<<<< This import is correct

# Configure logging (usually done once at the module level)
logging.basicConfig(level=logging.INFO) # Correctly configured basic logging
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",  # <--- THIS IS THE CRUCIAL ENTRY
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Or specify ["GET", "POST", "DELETE"] if you prefer
    allow_headers=["*"], # Or specify common headers like ["Content-Type", "Authorization"]
)
Base.metadata.create_all(bind=engine)

class EventBase(BaseModel):
    event_name: str # Corresponds to 'title' in frontend
    genre_name: str # Corresponds to 'genre' in frontend
    event_datetime: datetime # Corresponds to 'releaseDateTime' in frontend
    description: str | None = None # Corresponds to 'description', making it optional

class EventResponse(EventBase):
    id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

 
# @app.get("/events")
# async def read_all_events(db: Annotated[Session, Depends(get_db)]):
#     event = db.query(models.Events).all()
#     if event is None:
#         raise HTTPException(status_code=404,detail='Events not found')
#     return event

@app.get("/events/{id}", status_code=status.HTTP_200_OK, response_model=EventResponse)
async def read_event(id: int, db: Annotated[Session,Depends(get_db)]): 
    event = db.query(models.Events).filter(models.Events.id == id).first()
    if event is None:
        raise HTTPException(status_code=404, detail='Event not found')
    return event

@app.post("/events", status_code=status.HTTP_201_CREATED, response_model=EventResponse)
async def create_event(event: EventBase, db: Annotated[Session, Depends(get_db)]): 
    # Create the SQLAlchemy model instance

    if(event.event_datetime.tzinfo is None):
        utc_event_datetime = event.event_datetime.replace(tzinfo=timezone.utc)
    else:
        utc_event_datetime = event.event_datetime.astimezone(timezone.utc)
    db_event = models.Events(
        event_name=event.event_name, 
        genre_name=event.genre_name, 
        event_datetime=utc_event_datetime.replace(tzinfo=None),
        description=event.description # Pass description
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    logger.info(f"Pydantic parsed datetime: {event.event_datetime}")
    logger.info(f"Pydantic parsed datetime (tzinfo): {event.event_datetime.tzinfo}")
    logger.info(f"Pydantic parsed datetime: {event.event_datetime}")
    logger.info(f"Pydantic parsed datetime (tzinfo): {event.event_datetime.tzinfo}")

# ...
    return db_event

@app.get("/events", status_code=status.HTTP_200_OK, response_model=list[EventResponse])
async def read_events(db: Annotated[Session, Depends(get_db)]):
    events = db.query(models.Events).all()
    return events

@app.delete("/events/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(id: int, db: Annotated[Session, Depends(get_db)]):
    event = db.query(models.Events).filter(models.Events.id == id).first()
    if event is None:
        raise HTTPException(status_code=404, detail='Event not found')

    db.delete(event)
    db.commit()
    return 


