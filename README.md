# VisionPilot AI - AI-Powered Inference Optimization Middleware

VisionPilot AI is a production-ready, full-stack web application designed as an **AI-powered Inference Optimization Middleware** for industrial commerce. 

Its central purpose is to **predict the optimal preprocessing strategy** for industrial images before AI inference (such as product detection, OCR, or packaging verification) to maximize downstream model performance under varying industrial imaging conditions.

Rather than acting as a simple image enhancement tool, VisionPilot AI houses an **Inference-Aware Policy Network** that controls all preprocessing decisions dynamically. Preprocessing modules (such as HDR exposure blending and image straightening) are implemented as swappable plugins.

## Core Architecture Flow

```text
Industrial Image
        │
        ▼
Image Quality Assessment
        │
        ▼
Feature Extraction (brightness, contrast, blur, noise, color cast, dynamic range, skew)
        │
        ▼
Inference-Aware Policy Network
        │
        ▼
Policy Executor (loads & executes selected enhancement plugins)
        │
        ▼
Enhancement Plugins (HDR Fusion, Image Straightening, White Balance, etc.)
        │
        ▼
Existing Vision Models (YOLO Product Detection, OCR Reader)
        │
        ▼
Product Intelligence (Packaging Status PASS/FAIL)
```

## Project Directory Tree

```text
E:\VisionPilot_AI
├── frontend/                     # React + Vite + TypeScript dashboard application
├── backend/                      # FastAPI asynchronous REST backend
│   └── models/                   # Core Inference Policy structure
│       ├── quality/              # Image Quality Assessment metrics
│       ├── feature_extraction/   # Multi-module feature extraction
│       ├── policy/               # Policy Network & executor logic
│       │   └── training/         # Dataset builders and trainers
│       ├── enhancement/          # Preprocessing wrapper logic
│       ├── detectors/            # Downstream detection model wrappers
│       ├── ocr/                  # Downstream OCR model wrappers
│       ├── evaluation/           # Benchmarking & metrics
│       └── interfaces/           # Abstract Enhancement/Detector/OCR plugin definitions
├── database/                     # PostgreSQL schema scripts and SQLite fallback
├── api/                          # REST API specifications
├── configs/                      # JSON system configuration files
├── uploads/                      # Temporary image ingestion directory
├── outputs/                      # Final processed and annotated images
├── logs/                         # File logging directory
├── docs/                         # System manuals and specifications
├── deployment/                   # Nginx reverse proxy configurations
├── docker/                       # Dockerfiles for service build
├── docker-compose.yml            # Container orchestration config
├── HDR_Fusion_Engine_VisionPilot.py  # Approved HDR Fusion Engine (READ-ONLY)
└── ImageStraightener_VisionPilot.py # Approved Image Straightener Engine (READ-ONLY)
```

## Quick Start (Docker)

To deploy the entire stack including PostgreSQL, Nginx, React, and FastAPI:

```bash
docker-compose up --build -d
```

Access the React Dashboard at `http://localhost/` and the FastAPI Swagger docs at `http://localhost/docs`.

## Deployment and Secrets Configuration

For production and cloud environments (such as Railway), configurations are loaded from environment variables. Set the following parameters (refer to `.env.example` in the project root):
- `PORT`: Server port (automatically assigned by Railway; defaults to `8000` locally).
- `DATABASE_URL`: Connection string for PostgreSQL database. Falls back to local SQLite database if not provided.
- `JWT_SECRET` / `SECRET_KEY`: Secrets for cryptographic signing of security tokens.
- `VITE_API_URL`: Address of the FastAPI backend for the React client.

---

## Saas Demonstration Credentials

Log in using the following seeded operator credentials:
- **Username**: `admin`
- **Password**: `admin123`
- *Permission Level*: Administrator (access to calibrations, metrics, and health audits).

---

## Detailed Manuals and Guides

For further instructions, refer to:
- [Local Installation Guide](file:///E:/VisionPilot_AI/docs/installation_guide.md)
- [Railway Deployment Guide](file:///E:/VisionPilot_AI/docs/railway_deployment_guide.md)
- [Streamlit Demo Guide](file:///E:/VisionPilot_AI/docs/streamlit_deployment_guide.md)
- [User & Admin Manual](file:///E:/VisionPilot_AI/docs/user_manual.md)
- [API Reference Sheets](file:///E:/VisionPilot_AI/docs/api_documentation.md)
- [Troubleshooting & Recovery](file:///E:/VisionPilot_AI/docs/troubleshooting_guide.md)

---

## Streamlit Hackathon Demo Page (Quick Start)

To run the lightweight Streamlit presentation layer for judges:
```bash
pip install -r streamlit_app/streamlit_requirements.txt
streamlit run streamlit_app/app.py
```
This deploys a standalone dashboard interface showcasing metrics comparisons, defect uploads, and model pipeline decisions in real-time.
