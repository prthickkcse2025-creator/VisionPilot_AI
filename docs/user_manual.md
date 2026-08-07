# VisionPilot AI - User Manual, Administrator & Demo Guide

This guide details dashboard usage, administrative interfaces, and demo mode operations.

---

## 1. User Manual

VisionPilot AI is designed for real-time warehouse package inspections.

### A. Live Inspection Dashboard
- **Camera Stream**: Renders live webcam capture or mock video streams. Click **Start Inspection** to stream.
- **Dynamic Policy Cards**: Display the selected preprocessor in real-time. If the image is clean, it skips preprocessing (`NO_ACTION`).
- **Inspection Metrics**: Displays downstream YOLO detection confidences, OCR text character accuracy, and overall package verification validation status.
- **Latency Monitoring**: Displays latency breakdowns: feature extraction (2.2ms) + policy decision (0.3ms) + plugin execution.

### B. Image Upload Portal
- **Drag & Drop**: Ingest target inspection images (`.png`, `.jpg`, `.jpeg`).
- **Interactive Controls**:
  - **Zoom & Pan**: Adjust image coordinates.
  - **Side-by-side View**: Compare the original and preprocessed image.
  - **Split-screen Slider**: Move the boundary line to compare enhancements.

---

## 2. Administrator Guide

### A. System Configuration
- **Checkpoints Manager**: View active PyTorch model weights (`policy_best.pth`).
- **Plugin Health Checks**: Monitor the compile status of the production engines (`MAWB-Net HDR Fusion v13.2` and `Image Straightener`).
- **Database Management**: Monitor raw history records stored in PostgreSQL.

### B. User Access Policies
- **Role-Based Rules**:
  - **Admin**: Grants access to settings modification, system health logs, model swapping, and audits.
  - **User**: Restricted to Live Inspection, Image Upload, and History pages.

---

## 3. Demo Guide

For technical presentations and hackathons:
- **Demonstration Mode**: Activating Demo Mode loads 5 pre-rendered real-image industrial scenarios:
  1. **img_clean**: Nominal product box (strategy selection: `skip`).
  2. **img_dark**: Under-exposed barcode label (strategy selection: `hdr`).
  3. **img_skew**: Skewed packaging carton (strategy selection: `straighten`).
  4. **img_cast**: Temperature discolored solvent label (strategy selection: `white_balance`).
  5. **img_dark_cast**: Under-exposed discolored tag (strategy selection: `wb_hdr`).
- **Walkthrough Mode**: Step-by-step guides that walk users through simulated lighting and rotation corrections without requiring a live industrial camera.
