from fastapi import FastAPI
from internal import models, database
from api import routes

app = FastAPI(title="NPS Integration & AI Risk System")

# Crea le tabelle
models.Base.metadata.create_all(bind=database.engine)

# Include le rotte che abbiamo definito in api/routes.py
app.include_router(routes.router)


@app.get("/")
def home():
    return {"status": "Sistema NPS & AI attivo"}
