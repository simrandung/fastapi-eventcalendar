
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated 
from datetime import datetime,timezone
import models
from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import logging 
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)
Base.metadata.create_all(bind=engine)

oauth_scheme = OAuth2PasswordBearer(tokenUrl = "token")


@app.post("/token")
async def token_generate(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    return {"access_token": form_data.username, "token_type": "bearer"}

@app.post("/users/auth")
async def authentication(token: str = Depends(oauth_scheme)):
    print(token)
    return {
        "user":"simran",
        "profile_pic": "face"
    }

class EventBase(BaseModel):
    event_name: str 
    genre_name: str 
    event_datetime: datetime 
    description: str | None = None 

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
async def read_event(id: int, db: Annotated[Session,Depends(get_db)], token: str = Depends(oauth_scheme)): 
    print(token)
    event = db.query(models.Events).filter(models.Events.id == id).first()
    if event is None:
        raise HTTPException(status_code=404, detail='Event not found')
    return event

@app.post("/events", status_code=status.HTTP_201_CREATED, response_model=EventResponse)
async def create_event(event: EventBase, db: Annotated[Session, Depends(get_db)]): 
    
    if(event.event_datetime.tzinfo is None):
        utc_event_datetime = event.event_datetime.replace(tzinfo=timezone.utc)
    else:
        utc_event_datetime = event.event_datetime.astimezone(timezone.utc)
    db_event = models.Events(
        event_name=event.event_name, 
        genre_name=event.genre_name, 
        event_datetime=utc_event_datetime.replace(tzinfo=None),
        description=event.description 
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    logger.info(f"Pydantic parsed datetime: {event.event_datetime}")
    logger.info(f"Pydantic parsed datetime (tzinfo): {event.event_datetime.tzinfo}")
    logger.info(f"Pydantic parsed datetime: {event.event_datetime}")
    logger.info(f"Pydantic parsed datetime (tzinfo): {event.event_datetime.tzinfo}")

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


