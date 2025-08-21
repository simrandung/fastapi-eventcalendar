
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated 
import models
from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session

app = FastAPI()
Base.metadata.create_all(bind=engine)

class EventBase(BaseModel):
    event_name : str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

 

@app.post("/events/", status_code=status.HTTP_201_CREATED)

async def create_event(event: EventBase, db: Annotated[Session, Depends(get_db)]): 
    db_event = models.Events(**event.dict())
    db.add(db_event)
    db.commit()
    return db_event

@app.get("/events/{id}", status_code=status.HTTP_200_OK)
async def read_events(id:int, db: Annotated[Session,Depends(get_db)]):
    event = db.query(models.Events).filter(models.Events.id== id).first()
    if event is None:
        raise HTTPException(status_code=404,detail='Event not found')
    return event