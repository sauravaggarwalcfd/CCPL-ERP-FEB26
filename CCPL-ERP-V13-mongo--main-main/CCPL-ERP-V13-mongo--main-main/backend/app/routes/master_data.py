from fastapi import APIRouter

router = APIRouter()

# Placeholder routes - to be implemented
@router.get("/")
async def list_master_data():
    return {"message": "Master Data endpoint"}
