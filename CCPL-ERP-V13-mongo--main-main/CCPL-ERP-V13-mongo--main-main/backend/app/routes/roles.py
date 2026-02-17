from fastapi import APIRouter

router = APIRouter()

# Placeholder routes - to be implemented
@router.get("/")
async def list_roles():
    return {"message": "Roles endpoint"}
