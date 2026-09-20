from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, dashboard, inventory, metrics, logs, alerts, ai, security, reports, optimization

app=FastAPI(title="CloudOps-AI Kubernetes Monitoring API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

routers=[auth.router,dashboard.router,inventory.router,metrics.router,logs.router,
         alerts.router,ai.router,security.router,reports.router,optimization.router]
for r in routers: app.include_router(r,prefix="/api")

@app.get("/")
def root(): return {"project":"CloudOps-AI","status":"running","docs":"/docs"}

@app.get("/health")
def health(): return {"status":"healthy"}
