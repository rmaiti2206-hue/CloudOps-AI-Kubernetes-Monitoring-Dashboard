from fastapi import APIRouter,Query
from app.services.kubernetes_service import k8s
router=APIRouter(prefix="/inventory",tags=["Kubernetes Inventory"])
@router.get("/nodes")
def nodes(): return k8s.nodes()
@router.get("/pods")
def pods(): return k8s.pods()
@router.get("/deployments")
def deployments(): return k8s.deployments()
@router.get("/services")
def services(): return k8s.services()
@router.get("/namespaces")
def namespaces(): return k8s.namespaces()
@router.get("/events")
def events(): return k8s.events()
@router.get("/logs")
def logs(namespace:str=Query("default"),pod:str=Query(...),container:str|None=None):
    return {"namespace":namespace,"pod":pod,"logs":k8s.pod_logs(namespace,pod,container)}
