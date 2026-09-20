from fastapi import APIRouter
from app.services.prometheus_service import query
router=APIRouter(prefix="/metrics",tags=["Prometheus Metrics"])
@router.get("/summary")
async def summary():
    if not (await query("up")):
        return {"source":"demo","cpu":[42,48,51,54,49,57,54],"memory":[50,53,56,58,61,64,61],
                "network_rx":[12,18,15,21,24,19,23],"network_tx":[9,14,13,17,20,16,18]}
    return {"source":"prometheus","message":"Prometheus connection active. Use /docs for custom queries."}
@router.get("/query")
async def custom(q:str):
    return await query(q)
