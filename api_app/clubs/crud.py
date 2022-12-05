from sqlalchemy.orm import Session

from api_app.clubs.models import Club
from api_app.clubs.schemas import ClubCreate


def get_club(db: Session, id: int):
    return db.query(
        Club).filter(Club.id == id).first()


def get_clubs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(
        Club).offset(skip).limit(limit).all()


def create_club(db: Session,
                club: ClubCreate):
    db_club = Club(name=club.name,
                   country=club.country,
                   owner=club.owner,
                   year_of_foundation=club.year_of_foundation)
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club
