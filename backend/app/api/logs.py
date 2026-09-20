from fastapi import APIRouter
from app.services.kubernetes_service import k8s
router=APIRouter(prefix="/logs",tags=["Logs"])
@router.get("")
def logs(namespace:str="default",pod:str|None=None):
    if pod: return {"logs":k8s.pod_logs(namespace,pod)}
    return {"logs":"Select a pod to retrieve its latest container logs."}
