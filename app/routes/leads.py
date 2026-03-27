from fastapi import APIRouter
from app.leads import get_all_leads

router = APIRouter()

@router.get("/")
def list_leads():
    return {"leads": get_all_leads()}