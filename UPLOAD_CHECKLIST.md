# GitHub Upload & Deployment Checklist - VisionPilot AI

Use this checklist to verify repository completeness, security, and Railway deployment success.

---

## 1. Files Included (Completeness Checks)
- [x] **Root Directory**: `docker-compose.yml`, `.gitignore`, `.env.example`, `LICENSE`, `README.md`, `REPOSITORY_MANIFEST.md`.
- [x] **Production Engines**: `HDR_Fusion_Engine_VisionPilot.py` and `ImageStraightener_VisionPilot.py` are present and unmodified.
- [x] **Service folders**: `backend/`, `frontend/`, `configs/`, `database/`, `deployment/`, `docker/`, `docs/`.
- [x] **Preserved folders**: Empty directories `uploads/`, `outputs/`, and `logs/` contain `.gitkeep` files.

---

## 2. Excluded Files (Git Ignore Verification)
Verify that the following local cache or credentials files are NOT staged:
- [x] No `node_modules/` or custom packages.
- [x] No `__pycache__/` folders or `.pyc` compile symbols.
- [x] No python virtual environments (`venv/`, `env/`, `.venv/`).
- [x] No `.env` containing production passwords or API tokens.
- [x] No active runtime files under `uploads/*`, `outputs/*`, or `logs/*` (except `.gitkeep`).
- [x] No local sqlite DB files (`*.db`, `*.sqlite`).

---

## 3. GitHub Upload Workflow
Run these commands from your local workspace containing git CLI access:
1. Initialize repository:
   ```bash
   git init
   ```
2. Stage and commit:
   ```bash
   git add .
   git commit -m "feat: VisionPilot AI - Production Launch v1.0"
   ```
3. Link and push to your public/private repo:
   ```bash
   git remote add origin https://github.com/<your-username>/VisionPilot_AI.git
   git branch -M main
   git push -u origin main
   ```

---

## 4. Railway Deployment Checklist
1. **GitHub Auth**: Log in to Railway and link your GitHub account.
2. **Project Setup**: Click **New Project** $\rightarrow$ select your linked repository.
3. **Database Setup**: Click **New** $\rightarrow$ **Database** $\rightarrow$ **Add PostgreSQL**.
4. **Variables Config**: Navigate to the backend service $\rightarrow$ **Variables** tab $\rightarrow$ add:
   - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
   - `JWT_SECRET` = `SUPER_SECRET_VISION_PILOT_KEY_12345!`
   - `SECRET_KEY` = `SUPER_SECRET_VISION_PILOT_KEY_12345!`
5. **Frontend URL Mapping**: Under the frontend service variables tab, set `VITE_API_URL` to your deployed backend URL.

---

## 5. Live Verification Checks
Once deployed, perform the following validation walkthrough:
- [ ] Connect to `GET /health` and confirm all statuses return `"healthy"` or `"loaded"`.
- [ ] Log in using: User: `admin` / Password: `admin123`.
- [ ] Upload an image via the dashboard upload portal.
- [ ] Verify that the policy decision displays correctly, OCR results render, and detection confidence compiles.
