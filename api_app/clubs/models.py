from sqlalchemy import Column, Integer, String

from api_app.database import Base


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    country = Column(String)
    owner = Column(String)
    year_of_foundation = Column(Integer)
