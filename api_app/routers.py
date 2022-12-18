from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request
from fastapi.responses import FileResponse, JSONResponse

from api_app import dependencies
from api_app.database import cache_db
from api_app.clubs import crud, schemas
from api_app.events import create_event
from api_app.export import (
    PNG_FILE_NAME_BARS, PNG_FILE_NAME_DYNAMICS, PNG_FILE_NAME_DISPLOT
)
from api_app.celery_tasks import (
    task_app,
    task_publish_bar_plot,
    task_publish_dynamics_plot,
    task_publish_displot
)


router = APIRouter()


FILES = {
    'dynamics': PNG_FILE_NAME_DYNAMICS,
    'bars': PNG_FILE_NAME_BARS,
    'displot': PNG_FILE_NAME_DISPLOT,
}


TASKS = {
    'dynamics': task_publish_dynamics_plot,
    'bars': task_publish_bar_plot,
    'displot': task_publish_displot,
}


@router.get("/clubs/", response_model=List[schemas.Club])
async def get_clubs(db: Session = Depends(dependencies.get_db),
                    skip: int = 0,
                    limit: int = 100):
    return crud.get_clubs(db=db, skip=skip, limit=limit)


@router.get("/clubs/{club_id}",
            response_model=schemas.Club)
async def get_club(*,
                   club_id: int,
                   request: Request,
                   db: Session = Depends(dependencies.get_db)):
    db_club = crud.get_club(db=db, id=club_id)
    if db_club is None:
        raise HTTPException(status_code=404, detail="Club not found")
    event = {'club_id': db_club.id,
             'club': db_club.name,
             'type': 'view',
             'date_time': datetime.utcnow(),
             'ip': request.client.host}
    await create_event(event)
    return db_club


@router.post('/clubs/', response_model=schemas.Club)
async def create_club(*,
                      club: schemas.ClubCreate,
                      db: Session = Depends(dependencies.get_db)):
    return crud.create_club(db=db, club=club)


@router.get('/tasks/{task_type}/{period_in_minutes}',
            response_class=JSONResponse)
async def get_dataset(task_type: str, period_in_minutes: int):
    task_function = TASKS.get(task_type)
    if not task_function:
        return {}
    task = task_function.apply_async(countdown=10)
    return {'status': task.status, 'id': task.id}


@router.get('/tasks/{id}', response_class=JSONResponse)
async def get_task_status(id):
    task = task_app.AsyncResult(id)
    status = task.status
    return {'status': status}


@router.get('/result/{id}', response_class=FileResponse)
async def get_result_file(id):
    task_type = cache_db.get('current_task_type').decode('utf-8')
    task = task_app.AsyncResult(id)
    status = task.status
    if status == 'SUCCESS':
        return FILES[task_type]
