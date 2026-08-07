# Repository Manifest - VisionPilot AI

This manifest details the directory layout and file structures included in the VisionPilot AI GitHub repository.

---

## 1. Project Directory Structure

```text
VisionPilot_AI/
├── frontend/             # React + Vite + TypeScript dashboard application
├── backend/              # FastAPI asynchronous REST backend
│   └── models/           # Inference Policy structures and downstream wrappers
├── configs/              # JSON/YAML configuration file mounts
├── database/             # PostgreSQL database schemas & SQL scripts
├── deployment/           # Nginx server configuration files
├── docker/               # Dockerfiles for service images compilation
├── docs/                 # Complete architectural, installation, and evaluation guides
├── uploads/              # Ingested image caching directory
├── outputs/              # Enhanced/Annotated image output cache
└── logs/                 # Rotation file logging directory
```

---

## 2. Full File Inventory

### Root Configuration Files
- [`docker-compose.yml`](file:///E:/VisionPilot_AI/docker-compose.yml): Container orchestration recipe.
- [`.gitignore`](file:///E:/VisionPilot_AI/.gitignore): Files and folders excluded from Git version control.
- [`.env.example`](file:///E:/VisionPilot_AI/.env.example): Reference configuration template for environment secrets.
- [`LICENSE`](file:///E:/VisionPilot_AI/LICENSE): Open-source MIT release license.
- [`README.md`](file:///E:/VisionPilot_AI/README.md): Main documentation, features, installation, and deployment references.
- [`HDR_Fusion_Engine_VisionPilot.py`](file:///E:/VisionPilot_AI/HDR_Fusion_Engine_VisionPilot.py): Approved original HDR Fusion production engine copy (READ-ONLY).
- [`ImageStraightener_VisionPilot.py`](file:///E:/VisionPilot_AI/ImageStraightener_VisionPilot.py): Approved original Image Straightener production engine copy (READ-ONLY).

### System Manuals ([`docs/`](file:///E:/VisionPilot_AI/docs/))
- [`installation_guide.md`](file:///E:/VisionPilot_AI/docs/installation_guide.md): Local development environment instructions.
- [`railway_deployment_guide.md`](file:///E:/VisionPilot_AI/docs/railway_deployment_guide.md): Railway cloud deploy launch guides.
- [`user_manual.md`](file:///E:/VisionPilot_AI/docs/user_manual.md): Integrated User, Admin, and Demo dashboard walkthrough.
- [`api_documentation.md`](file:///E:/VisionPilot_AI/docs/api_documentation.md): API REST path mappings with curl templates.
- [`troubleshooting_guide.md`](file:///E:/VisionPilot_AI/docs/troubleshooting_guide.md): Setup debugging and recovery tips.
- [`architecture_overview.md`](file:///E:/VisionPilot_AI/docs/architecture_overview.md): System design, blocks, and sequence mappings.
- [`scientific_benchmark_report.md`](file:///E:/VisionPilot_AI/docs/scientific_benchmark_report.md): Comparative evaluation results and validity threats.
- [`railway_readiness_report.md`](file:///E:/VisionPilot_AI/docs/railway_readiness_report.md): Verification report confirming Railway readiness.

---

## 3. Directory Purposes

- **`backend/`**: Serves REST APIs, processes incoming images, extracts features, queries the Policy MLP network, and coordinates enhancement execution.
- **`frontend/`**: Dynamic dashboard for operator logins, drag-drop comparison, latency metrics, and configuration audits.
- **`configs/`**: Defines thresholds, scoring parameters, model inputs, and downstream weights.
- **`database/`**: Initializes historical inspection tables, user credentials, and telemetry schemas.
- **`deployment/`**: Manages Nginx routing, routing assets, and proxy headers.
- **`docker/`**: Provides isolated environments for reproducible execution.
- **`uploads/` / `outputs/`**: Volume mounts for raw inputs and preprocessed visuals.
