from fastapi import APIRouter
from app.services.kubernetes_service import k8s
router=APIRouter(prefix="/reports",tags=["Reports"])
@router.get("/summary")
def report():
    p=k8s.pods(); n=k8s.nodes()
    return {"cluster":"CloudOps-AI","nodes":len(n),"pods":len(p),
            "failed_pods":sum(x.get("status") not in ("Running","Succeeded") for x in p),
            "node_count":len(n),"generated_by":"CloudOps-AI"}
