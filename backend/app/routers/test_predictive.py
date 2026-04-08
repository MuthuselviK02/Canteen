from fastapi import APIRouter

router = APIRouter(prefix="/api/test-predictive", tags=["Test Predictive"])

@router.get("/hello")
async def hello():
    return {"message": "Hello from test predictive router!"}
