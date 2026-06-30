# A3 智能学习系统 - 主入口
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from database import init_db
from routers import auth, agent_api, resource, report

app = FastAPI(title="LearnMind - A3智能学习系统", version="1.0.0")

# 注册路由
app.include_router(auth.router)
app.include_router(agent_api.router)
app.include_router(resource.router)
app.include_router(report.router)

# 静态文件
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.on_event("startup")
async def startup():
    await init_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
