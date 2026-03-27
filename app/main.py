from fastapi import FastAPI
from app.routes.chat import router as chat_router
from app.routes.leads import router as leads_router
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(chat_router, prefix="/chat")
app.include_router(leads_router, prefix="/leads")

@app.get("/")
def root():
    return {"message": "AI Front Desk is running"}