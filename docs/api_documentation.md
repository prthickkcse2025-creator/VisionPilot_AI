# VisionPilot AI - API Documentation Reference

This manual contains details for all FastAPI REST endpoints.

---

## 1. Authentication Endpoints

### A. User Login
- **Endpoint**: `POST /api/login`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Request Form Fields**:
  - `username`: `admin`
  - `password`: `admin123`
- **Response JSON**:
  ```json
  {
    "access_token": "mock_token_admin",
    "token_type": "bearer",
    "role": "admin"
  }
  ```
- **cURL Command**:
  ```bash
  curl -X POST http://localhost:8000/api/login \
    -d "username=admin&password=admin123"
  ```

---

## 2. Policy & Feature Extraction Endpoints

### A. Extract Features
- **Endpoint**: `POST /extract_features`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body (JSON)**:
  - `image_id`: `101`
- **Response JSON**:
  ```json
  {
    "image_id": 101,
    "features": {
      "brightness": 0.52,
      "contrast": 0.48,
      "blur": 0.05,
      "noise": 0.02,
      "color_cast": 0.01,
      "dynamic_range": 0.70,
      "perspective_skew": 0.00
    }
  }
  ```

### B. Predict Policy Strategy
- **Endpoint**: `POST /predict_policy`
- **Headers**: `Authorization: Bearer <token>`
- **Response JSON**:
  ```json
  {
    "image_id": 101,
    "policy_decision": "HDR_FUSION",
    "selected_strategy": "HDR_FUSION_Ensemble_v1",
    "confidence_score": 0.94,
    "reasons": [
      "Low brightness or high dynamic range detected; exposure fusion required."
    ],
    "feature_summary": {
      "dynamic_range": 0.78,
      "brightness": 0.22
    }
  }
  ```

### C. Evaluate Policy Performance
- **Endpoint**: `POST /policy/evaluate`
- **Headers**: `Authorization: Bearer <token>`
- **Response JSON**:
  ```json
  {
    "status": "complete",
    "images_evaluated": 100,
    "comparison": {
      "raw": { "latency_ms": 0.0, "mean_accuracy": 0.621 },
      "fixed": { "latency_ms": 92.2, "mean_accuracy": 0.919 },
      "policy": { "latency_ms": 32.52, "mean_accuracy": 0.9416 }
    }
  }
  ```
- **cURL Command**:
  ```bash
  curl -X POST http://localhost:8000/policy/evaluate \
    -H "Authorization: Bearer mock_token_admin"
  ```

---

## 3. Enhancement Plugins Endpoints

### A. Manual Enhancement execution
- **Endpoint**: `POST /enhance`
- **Headers**: `Authorization: Bearer <token>`
- **Request Form Data**:
  - `file`: `<Image File Binary>`
  - `enhancement`: `HDR Fusion`
- **Response JSON**:
  ```json
  {
    "status": "success",
    "enhancement": "HDR Fusion",
    "processing_time": 0.058,
    "original_image": "/uploads/test.png",
    "processed_image": "/outputs/test_enhanced.png"
  }
  ```

### B. Registry Plugin Health
- **Endpoint**: `GET /plugins/health`
- **Headers**: `Authorization: Bearer <token>`
- **Response JSON**:
  ```json
  {
    "HDR Fusion": "healthy",
    "Image Straightener": "healthy"
  }
  ```
