import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import {LineChart,Line,XAxis,YAxis,Tooltip,CartesianGrid,ResponsiveContainer} from "recharts";
import "./styles.css";
const API=import.meta.env.VITE_API_URL||"http://localhost:8000/api";
const get=p=>fetch(API+p).then(r=>r.json());

function Table({data,cols}){return <table><thead><tr>{cols.map(c=><th>{c}</th>)}</tr></thead><tbody>{data.map(x=><tr>{cols.map(c=><td>{String(x[c]??"-")}</td>)}</tr>)}</tbody></table>}
function App(){
 const [page,setPage]=useState("Dashboard"),[data,setData]=useState({overview:{},nodes:[],pods:[],alerts:[],ai:[],metrics:null});
 const nav=["Dashboard","Nodes","Pods","Deployments","Services","Namespaces","Metrics","Logs","Alerts","AI Insights","Security","Cost Optimization","Reports"];
 useEffect(()=>Promise.all([get("/dashboard/overview"),get("/inventory/nodes"),get("/inventory/pods"),get("/alerts"),get("/ai/insights"),get("/metrics/summary")])
 .then(([overview,nodes,pods,alerts,ai,metrics])=>setData({overview,nodes,pods,alerts,ai,metrics})),[]);
 const d=data.overview,m=data.metrics;
 const chart=m?.cpu?.map((cpu,i)=>({t:i+1,cpu,memory:m.memory[i]}))||[];
 const render=()=>{
  if(page==="Dashboard")return <><div className="cards">{[["Nodes",d.nodes],["Pods",d.pods],["Deployments",d.deployments],["CPU","54%"],["Memory","61%"],["Alerts",d.open_alerts]].map(x=><div className="card"><small>{x[0]}</small><b>{x[1]??"—"}</b></div>)}</div>
  <div className="grid"><div className="panel"><h3>CPU / Memory</h3><div className="chart"><ResponsiveContainer><LineChart data={chart}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="t"/><YAxis/><Tooltip/><Line dataKey="cpu"/><Line dataKey="memory"/></LineChart></ResponsiveContainer></div></div>
  <div className="panel"><h3>AI Health Insights</h3>{data.ai.map(i=><div className="insight"><b>{i.severity} — {i.title}</b><p>{i.analysis}</p><span>{i.recommendation}</span></div>)}</div></div></>;
  if(page==="Nodes")return <Table data={data.nodes} cols={["name","status","cpu","memory","pods"]}/>;
  if(page==="Pods")return <Table data={data.pods} cols={["name","namespace","status","restarts"]}/>;
  if(page==="Alerts")return <Table data={data.alerts} cols={["severity","title","resource","status"]}/>;
  if(page==="AI Insights")return <div className="panel">{data.ai.map(i=><div className="insight"><h3>{i.title}</h3><p>{i.analysis}</p><b>Recommendation: {i.recommendation}</b></div>)}</div>;
  if(page==="Metrics")return <div className="panel"><h3>Prometheus Metrics</h3><div className="chart big"><ResponsiveContainer><LineChart data={chart}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="t"/><YAxis/><Tooltip/><Line dataKey="cpu" name="CPU %"/><Line dataKey="memory" name="Memory %"/></LineChart></ResponsiveContainer></div></div>;
  return <div className="panel"><h3>{page}</h3><p>This module is connected to the FastAPI/Kubernetes monitoring architecture. Use the API documentation at <b>/docs</b> for its endpoint.</p></div>;
 };
 return <div className="layout"><aside><h1>☁ CloudOps-AI</h1><small>Kubernetes Operations Center</small>{nav.map(n=><button className={page===n?"active":""} onClick={()=>setPage(n)}>{n}</button>)}</aside><main><header><div><h2>{page}</h2><span>Real-time cluster visibility • AI-assisted operations</span></div><strong className="health">● {d.health||"Loading"}</strong></header>{render()}</main></div>
}
createRoot(document.getElementById("root")).render(<App/>);
