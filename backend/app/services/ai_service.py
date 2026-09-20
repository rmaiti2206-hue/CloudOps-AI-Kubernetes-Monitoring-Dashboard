def analyze(nodes,pods,alerts):
    insights=[]
    bad=[p for p in pods if p.get("status") in ("CrashLoopBackOff","Failed","Error") or p.get("restarts",0)>=5]
    if bad:
        p=bad[0]
        insights.append({"severity":"High","title":"Workload instability detected",
          "analysis":f"{p['name']} is unhealthy or restarting frequently.",
          "recommendation":"Inspect pod logs, events, liveness/readiness probes and memory/CPU limits."})
    overloaded=[n for n in nodes if str(n.get("cpu","")).rstrip("%").isdigit() and int(str(n["cpu"]).rstrip("%"))>=80]
    if overloaded:
        insights.append({"severity":"High","title":"Node resource pressure",
          "analysis":f"{overloaded[0]['name']} shows high CPU utilization.",
          "recommendation":"Review workload placement and consider scaling or adjusting resource requests."})
    if not insights:
        insights.append({"severity":"Low","title":"No critical pattern detected",
          "analysis":"Current inventory does not show a major failure pattern.",
          "recommendation":"Continue monitoring historical CPU, memory, restarts and Kubernetes events."})
    return insights

def optimize(nodes,pods):
    result=[]
    for n in nodes:
        c=str(n.get("cpu","")).rstrip("%")
        if c.isdigit() and int(c)>=80:
            result.append({"resource":n["name"],"type":"Scale/Balance","reason":"High CPU utilization",
                           "action":"Distribute workloads or increase capacity."})
        elif c.isdigit() and int(c)<=20:
            result.append({"resource":n["name"],"type":"Right-size","reason":"Low CPU utilization",
                           "action":"Review requests and workload placement before reducing capacity."})
    return result
