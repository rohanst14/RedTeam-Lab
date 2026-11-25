import os
from pathlib import Path
from typing import Literal
from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,ConfigDict
from .engine import run
from .providers import FixtureProvider
from .store import Store

class RunRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    mode: Literal["protected","unprotected"]="protected"

def create_app(path=None):
    app=FastAPI(title="RedTeam-Lab",version="0.1.0")
    store=Store(path or os.getenv("REDTEAM_DB","data/runs.sqlite3"))
    @app.get("/api/health")
    def health(): return {"status":"ok"}
    @app.post("/api/runs",status_code=201)
    def create_run(request:RunRequest):
        report=run(FixtureProvider(request.mode))
        store.save(report)
        return report
    @app.get("/api/runs")
    def list_runs(): return store.list()
    @app.get("/api/runs/{run_id}")
    def get_run(run_id:str):
        result=store.get(run_id)
        if result is None: raise HTTPException(status_code=404,detail="Run not found")
        return result
    app.mount("/",StaticFiles(directory=Path(__file__).parent/"static",html=True),name="dashboard")
    return app

app=create_app()
