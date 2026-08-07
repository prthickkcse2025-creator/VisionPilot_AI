# VisionPilot AI - Troubleshooting & Recovery Guide

This guide assists in troubleshooting environment mismatches, missing models, and database connectivity.

---

## 1. Database Connectivity Issues
- **Problem**: Backend fails to start with `ConnectionRefusedError: [Errno 111] Connect call failed`.
- **Cause**: PostgreSQL service is down or docker initialization has not completed.
- **Solution**:
  - Run `docker compose ps` to inspect container health status.
  - If using the SQLite fallback, check `USE_SQLITE_FALLBACK=true` environment variable inside your `.env` or Compose variables.

---

## 2. ONNX Missing Dependency
- **Problem**: Training or audit script fails with `ModuleNotFoundError: No module named 'onnx'`.
- **Cause**: Python environment is missing libraries.
- **Solution**:
  - Install dependencies: `pip install onnx onnxruntime`.

---

## 3. Production Model Engine Not Compiling
- **Problem**: Dashboard reports `HDR Fusion` or `Image Straightener` status as `unhealthy` or `error`.
- **Cause**: Hydration speculation file locations are misaligned.
- **Solution**:
  - Verify original approved production engines exist at `E:\MAWB-Net\HDR_FUSION_PRODUCTION_V13_1\Source_Code\fusion.py` and `D:\ai-image-straightener\backend\core\straighten.py`.
  - Check wrapper paths inside `hdr_plugin.py` and `straightener_plugin.py` to ensure local working copies under `E:\VisionPilot_AI\models\production\` are hydrated.

---

## 4. Frontend Hot Reload Failures
- **Problem**: Vite development server crashes or throws type errors during build.
- **Cause**: Outdated `node_modules` or type mismatches.
- **Solution**:
  - Run `npm install` to update node packages.
  - Clear vite caches: `rm -rf node_modules/.vite`.
