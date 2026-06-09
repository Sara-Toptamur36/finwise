# -*- coding: utf-8 -*-
"""
Banka AI — FastAPI Backend
"""
import os, sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# backend/ ve veri_seti/ dizinlerini path'e ekle
_HERE   = os.path.dirname(os.path.abspath(__file__))   # .../backend
_PARENT = os.path.join(_HERE, "..")                    # .../veri_seti
for _p in (_HERE, _PARENT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from routers import auth, analysis, demo, scenario, reports

app = FastAPI(
    title="Banka AI API",
    description="4 asamali ML tabanli kisisel finans analiz sistemi",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(demo.router,     prefix="/api/demo",     tags=["Demo"])
app.include_router(scenario.router, prefix="/api/scenario", tags=["Scenario"])
app.include_router(reports.router,  prefix="/api/reports",  tags=["Reports"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
