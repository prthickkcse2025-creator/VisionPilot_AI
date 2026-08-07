# Policy Network Training & Validation Report

This document contains the training summary, validation results, model card, and ONNX configurations for the Policy Network.

---

## 1. Training Configuration Summary

The training run loaded parameters directly from `configs/policy_config.yaml`:
- **Learning Rate**: `0.005`
- **Batch Size**: `16`
- **Total Target Epochs**: `100`
- **Optimizer**: Adam (weight decay = `0.0001`)
- **Loss Function**: CrossEntropyLoss
- **Early Stopping Patience**: `10`
- **Random Seed**: `42` (Fixed for 100% reproducibility)
- **Dataset Size**: 100 samples (80% Train, 20% Validation split)
- **Number of Classes**: 5 targets

---

## 2. Model Card

### Model Details:
- **Model Name**: VisionPilot Inference-Aware Policy MLP
- **Model Type**: Multi-Layer Perceptron (MLP)
- **Input Dimensions**: 7 float features (brightness, contrast, blur, noise, color_cast, dynamic_range, perspective_skew)
- **Architecture**:
  - Linear (7 -> 32) + ReLU
  - Linear (32 -> 16) + ReLU
  - Linear (16 -> 5) + Softmax (classification)
- **Target Output Classes**:
  - `0`: `Skip`
  - `1`: `White Balance`
  - `2`: `HDR Fusion`
  - `3`: `Image Straightening`
  - `4`: `White Balance + HDR Fusion`

### Intended Use:
To predict the optimal image enhancement preprocessor that maximizes downstream AI model accuracy under varied light and tilt conditions.

---

## 3. Training & Validation Results

The model trained to convergence at **Epoch 100** (best checkpoint at Epoch 97):

### Summary Metrics:
- **Training Accuracy**: 100.00%
- **Validation Accuracy**: 100.00%
- **Precision (Macro-Average)**: 1.0000
- **Recall (Macro-Average)**: 1.0000
- **F1 Score (Macro-Average)**: 1.0000
- **ONNX Export Validation**: Success (model checked and loaded successfully)

### Confusion Matrix (20 validation samples):
```
            Predicted
            0  1  2  3  4
True  0     7  0  0  0  0
      1     0  3  0  0  0
      2     0  0  2  0  0
      3     0  0  0  6  0
      4     0  0  0  0  2
```

### Per-Class Metrics:
- **Class 0 (skip)**: Precision: 1.00, Recall: 1.00, F1: 1.00
- **Class 1 (white_balance)**: Precision: 1.00, Recall: 1.00, F1: 1.00
- **Class 2 (hdr)**: Precision: 1.00, Recall: 1.00, F1: 1.00
- **Class 3 (straighten)**: Precision: 1.00, Recall: 1.00, F1: 1.00
- **Class 4 (wb_hdr)**: Precision: 1.00, Recall: 1.00, F1: 1.00

---

## 4. Hardware and Environment Specifications
- **Hardware Used**: Intel Core / NVIDIA GPU (CUDA CPU execution mode)
- **Software Versions**: PyTorch v2.x, ONNX v1.22
- **Training Logs Location**: [`training_stats.json`](file:///E:/VisionPilot_AI/backend/models/policy/training/training_stats.json)
- **Prediction Logs Location**: [`prediction_logs.json`](file:///E:/VisionPilot_AI/backend/models/policy/training/prediction_logs.json)
- **Export Paths**:
  - PyTorch Checkpoint: [`policy_best.pth`](file:///E:/VisionPilot_AI/backend/models/policy/checkpoints/policy_best.pth)
  - ONNX Model: [`policy_best.onnx`](file:///E:/VisionPilot_AI/backend/models/policy/checkpoints/policy_best.onnx)
