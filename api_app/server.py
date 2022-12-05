import uvicorn
from fastapi import FastAPI

from api_app.routers import router
from api_app.clubs import models
from api_server.database import database, engine


app = FastAPI()

app.include_router(router)


@app.on_event('startup')
async def startup():
    await database.connect()
    models.Base.metadata.create_all(bind=engine)


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
