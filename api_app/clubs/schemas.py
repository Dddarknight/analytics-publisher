from typing import Union

from pydantic import BaseModel


class BaseClub(BaseModel):
    name: str
    country: Union[str, None] = None
    owner: Union[str, None] = None
    year_of_foundation: Union[int, None] = None


class ClubCreate(BaseClub):
    pass


class Club(BaseClub):
    id: int

    class Config:
        orm_mode = True
