from fastapi import FastAPI
from src.api.tasks import router as task_router

app = FastAPI(title="Async Task Processing API")

app.include_router(task_router)   # ✅ NO PREFIX HERE

