from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request
from fastapi.responses import FileResponse

from api_app import dependencies
from api_app.clubs import crud, schemas
from api_app.events import make_event, get_filtered_statistics
from api_app.export import build_bar_plot, build_dynamics_plot
from api_app.export import (
    PNG_FILE_NAME_BARS, PNG_FILE_NAME_DYNAMICS
)

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


@router.get('/file-dataset/{period_in_minutes}', response_class=FileResponse)
async def get_dataset(period_in_minutes: int):
    statistics = await get_filtered_statistics(
        period_in_minutes=period_in_minutes)
    build_bar_plot(statistics)
    return PNG_FILE_NAME_BARS


@router.get('/file-dynamics/{period_in_minutes}', response_class=FileResponse)
async def get_dynamics(period_in_minutes: int):
    statistics = await get_filtered_statistics(
        period_in_minutes=period_in_minutes)
    build_dynamics_plot(statistics)
    return PNG_FILE_NAME_DYNAMICS
