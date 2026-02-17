from fastapi import APIRouter

router = APIRouter()

# Placeholder routes - to be implemented
@router.get("/")
async def list_inventory():
    return {"message": "Inventory endpoint"}
