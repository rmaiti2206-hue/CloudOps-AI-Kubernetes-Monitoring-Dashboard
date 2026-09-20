from fastapi import APIRouter
router=APIRouter(prefix="/security",tags=["Security"])
@router.get("/events")
def events():
    return [{"time":"20:58","severity":"INFO","event":"Successful login"},
            {"time":"20:59","severity":"WARNING","event":"Failed login attempt"},
            {"time":"21:02","severity":"HIGH","event":"Unauthorized API request blocked"}]
