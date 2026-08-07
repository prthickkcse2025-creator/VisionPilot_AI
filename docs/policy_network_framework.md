# Inference-Aware Policy Network & Feature Extraction Framework

This document outlines the architecture, data structures, modes, and guides for the VisionPilot AI Policy Network.

---

## 1. Downstream Performance-Aware Label Generation

Rather than using manual heuristic rules or human labels, VisionPilot AI generates labels for the Policy Network training set directly from **measured downstream AI performance**.

### Target Label Logic
During dataset builder compilation:
1. An image is ingested and its 7 feature metrics are extracted.
2. The image is preprocessed using **every available strategy**:
   - `Skip` (Class 0)
   - `White Balance` (Class 1)
   - `HDR Fusion` (Class 2)
   - `Image Straightening` (Class 3)
   - `White Balance + HDR Fusion` (Class 4)
3. Each output is run through the downstream vision models (YOLO box finder, OCR reader, packaging verification).
4. The system calculates a `combined_score` from the downstream metrics:
   $$\text{Combined Score} = \frac{\text{OCR Score} + \text{Detection Confidence} + \text{Packaging Score}}{3}$$
5. The strategy that maximizes the `combined_score` is selected as the ground truth training target `label`.

---

## 2. Separate Development and Evaluation Modes

To maintain scientific integrity during testing and deployment, the framework operates in two distinct modes:

### A. Development Mode (`evaluation_mode = False`)
- **Purpose**: UI testing and system debugging.
- **Behavior**: Uses the trained Policy Network if weights exist. If weights are missing, it falls back to heuristic rule-based logic to return mock predictions so that the dashboard UI elements can render correctly without throwing errors.

### B. Evaluation Mode (`evaluation_mode = True`)
- **Purpose**: System benchmarking and scientific evaluation.
- **Behavior**: Relies strictly on the trained MLP PyTorch network. Heuristic fallback and mock outputs are **strictly disabled**.
- **Missing Weights Handling**: If the trained checkpoint (`policy_best.pth`) is missing, the system aborts and returns an error response:
  `"Policy model not trained. Evaluation unavailable."`
  This ensures that heuristic outputs never contaminate benchmark datasets or experimental reports.

---

## 3. Feature Extraction Reference
Features are extracted in real-time under `backend/models/feature_extraction/`:
- **Brightness (`brightness.py`)**: Computes mean grayscale values normalized to `[0.0, 1.0]`.
- **Contrast (`contrast.py`)**: Estimates grayscale standard deviation normalized to `[0.0, 1.0]`.
- **Blur (`blur.py`)**: Variance of Laplacian mapped to `[0.0, 1.0]` (1.0 = extremely blurry).
- **Noise (`noise.py`)**: Estimates standard deviation of difference between source and Gaussian blur.
- **Color Cast (`color_cast.py`)**: Measures Lab chrominance coordinates deviation from neutral.
- **Dynamic Range (`dynamic_range.py`)**: Spread between 99th and 1st percentile of grayscale values.
- **Perspective Distortion (`perspective.py`)**: Estimates skew angle using Hough line transform.
