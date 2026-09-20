from fastapi import APIRouter
from app.services.kubernetes_service import k8s
router=APIRouter(prefix="/dashboard",tags=["Dashboard"])
@router.get("/overview")
def overview():
    n,p,d,ns=k8s.nodes(),k8s.pods(),k8s.deployments(),k8s.namespaces()
    bad=sum(1 for x in p if x.get("status") not in ("Running","Succeeded"))
    return {"cluster":"CloudOps-AI","health":"Warning" if bad else "Healthy",
            "nodes":len(n),"pods":len(p),"deployments":len(d),"namespaces":len(ns),
            "failed_pods":bad,"open_alerts":bad+2}
