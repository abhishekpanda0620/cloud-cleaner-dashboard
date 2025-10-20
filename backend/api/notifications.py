from fastapi import APIRouter

router = APIRouter()

@router.get("/unused")
def get_unused_notifications():
    return {"msg": "Notifications cleanup endpoint placeholder"}
