# Installation & Test Guide - VisionPilot AI

This document provides instructions on how to install, configure, execute, and verify the VisionPilot AI Inference Optimization Middleware locally or inside containerized production environments.

## System Prerequisites
- **Python**: version 3.11 or later
- **Docker & Docker Compose**: installed and configured
- **Operating System**: Windows (tested on Windows 10/11)

---

## Method 1: Local Development & Verification

### 1. Database Initialization
By default, the backend operates in **SQLite Fallback Mode** to ease development without requiring PostgreSQL to be running on the host system. 
To initialize the SQLite database tables:
```bash
# Add python path
$env:PYTHONPATH="E:\VisionPilot_AI"
python E:\VisionPilot_AI\database\init_db.py
```
This creates the tables in `E:\VisionPilot_AI\database\visionpilot.db`.

### 2. Backend Setup
Create a virtual environment, activate it, and install python dependencies:
```bash
cd E:\VisionPilot_AI\backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install PyTorch and backend requirements
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 3. Running Unit Tests
Validate the complete pipeline structure, feature extraction modules, policy network logic, plugin interface compliance, and REST APIs:
```bash
cd E:\VisionPilot_AI
python -m unittest discover -s backend/tests
```
Expected output: `OK` showing 16 tests passed.

### 4. Launching the Backend Server
Launch the FastAPI web server:
```bash
uvicorn main:app --reload --port 8000
```
Verify the server by going to `http://localhost:8000/health`.

### 5. Frontend Setup
```bash
cd E:\VisionPilot_AI\frontend
npm install
npm run dev
```
Open `http://localhost:3000` to view the SaaS dashboard portal.

---

## Method 2: Containerized Production Deployment

Using Docker Compose compiles the TypeScript frontend, sets up the Nginx proxy, provisions PostgreSQL tables, and runs the FastAPI backend pipeline automatically.

```bash
cd E:\VisionPilot_AI
docker-compose up --build -d
```

### Access Ports:
- **Web Frontend (Nginx)**: `http://localhost:80`
- **FastAPI REST API**: `http://localhost:8000`
- **PostgreSQL Database**: Port `5432` on `localhost`
- **Swagger Documentation**: `http://localhost:8000/docs`
