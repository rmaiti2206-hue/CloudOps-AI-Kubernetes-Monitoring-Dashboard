from fastapi import APIRouter
from app.services.kubernetes_service import k8s
from app.services.ai_service import analyze
router=APIRouter(prefix="/ai",tags=["AI"])
@router.get("/insights")
def insights():
    n,p=k8s.nodes(),k8s.pods()
    return analyze(n,p,[])
