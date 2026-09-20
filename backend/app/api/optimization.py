from fastapi import APIRouter
from app.services.kubernetes_service import k8s
from app.services.ai_service import optimize
router=APIRouter(prefix="/optimization",tags=["Optimization"])
@router.get("/recommendations")
def recommendations(): return optimize(k8s.nodes(),k8s.pods())
