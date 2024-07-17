import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from api.handlers import router as image_router


app = FastAPI(title="ResCompPicAPI")

main_api_router = APIRouter()

main_api_router.include_router(image_router, prefix='/image', tags=['image'])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
