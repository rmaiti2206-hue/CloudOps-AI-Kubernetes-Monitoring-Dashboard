# CloudOps-AI Kubernetes Monitoring Dashboard — Full MCA Major Project

Student: Rajdeep Maiti
Student ID: 25MCC20007

This project is designed as an actual Kubernetes operations dashboard, not only a static UI.

## Core capabilities
- JWT login and registration
- Role-based access control: admin, devops, viewer
- Real Kubernetes API integration
- Real node, pod, deployment, service and namespace inventory
- Pod logs and Kubernetes events
- Prometheus queries for CPU, memory and network metrics
- Alert engine
- AI-style diagnostic and resource-optimization engine
- Security event monitoring
- Cost/resource optimization recommendations
- Report API
- React dashboard with charts and tables
- PostgreSQL-ready persistence layer
- Docker Compose
- Kubernetes deployment manifests
- Prometheus + Grafana
- GitHub Actions CI
- Terraform starter for AWS/EKS

## Run without a cluster
The default `DEMO_MODE=true` lets you demonstrate the complete UI and API.

## Run with a real Kubernetes cluster
1. Start Minikube, Docker Desktop Kubernetes, kind, or connect to EKS.
2. Confirm:
   `kubectl get nodes`
3. Set `DEMO_MODE=false`.
4. If backend runs on your PC, it uses the current kubeconfig.
5. Start backend and frontend.
6. Configure Prometheus URL in `.env`.

For a backend running inside Kubernetes, use in-cluster Kubernetes configuration.

## Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Frontend
```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend: http://localhost:5173
Backend docs: http://localhost:8000/docs
Prometheus: http://localhost:9090
Grafana: http://localhost:3000

## Docker Compose
```powershell
docker compose up --build
```

## Security
Never put AWS keys, kubeconfig files, passwords, JWT secrets or private keys in Git.
