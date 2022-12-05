from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from api_app import dependencies
from api_app.clubs import crud, schemas
from api_app.events import make_event


router = APIRouter()


@router.get("/clubs/", response_model=List[schemas.Club])
async def read_clubs(db: Session = Depends(dependencies.get_db),
                     skip: int = 0,
                     limit: int = 100):
    return crud.get_clubs(db=db, skip=skip, limit=limit)


@router.get("/clubs/{club_id}",
            response_model=schemas.Club)
async def read_club(*,
                    club_id: int,
                    request: Request,
                    db: Session = Depends(dependencies.get_db)):
    db_club = crud.get_club(db=db, id=club_id)
    if db_club is None:
        raise HTTPException(status_code=404, detail="Club not found")
    event_data = {'club_id': db_club.id,
                  'club': db_club.name,
                  'type': 'view',
                  'date_time': datetime.utcnow(),
                  'ip': request.client.host}
    await make_event(event_data)
    return db_club


@router.post('/clubs/', response_model=schemas.Club)
async def create_club(*,
                      club: schemas.ClubCreate,
                      db: Session = Depends(dependencies.get_db)):
    return crud.create_club(db=db, club=club)
