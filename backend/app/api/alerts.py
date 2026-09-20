from fastapi import APIRouter
from app.services.kubernetes_service import k8s
router=APIRouter(prefix="/alerts",tags=["Alerts"])
@router.get("")
def alerts():
    pods=k8s.pods()
    out=[]
    for p in pods:
        if p.get("status") not in ("Running","Succeeded"):
            out.append({"severity":"CRITICAL","title":"Unhealthy pod","resource":p["name"],"status":"Open"})
        if p.get("restarts",0)>=5:
            out.append({"severity":"WARNING","title":"Frequent pod restarts","resource":p["name"],"status":"Open"})
    return out
