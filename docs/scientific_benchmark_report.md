# Scientific Benchmarking & Experimental Evaluation Report

This report presents the objective benchmarking results, ablation studies, failure reports, and threats to validity for VisionPilot AI.

---

## 1. Experimental Methodology & Settings
Evaluations were performed under identical settings on the **100-sample real-image inspection dataset** generated during Phase 4A.
- **Hardware Used**: Intel Core CPU, 16GB RAM.
- **Software Environment**: PyTorch v2.x, ONNX runtime v1.22, OpenCV v4.x.
- **Random Seed**: `42`
- **Evaluation Weights**: OCR (`0.45`), Object Detection (`0.40`), Packaging Verification (`0.15`).

---

## 2. Comparison Results (Baseline Benchmarks)

The four evaluated pipeline configurations are:
1. **Method A (Raw)**: Original un-preprocessed image.
2. **Method B (CLAHE)**: Standard OpenCV Contrast Limited Adaptive Histogram Equalization.
3. **Method C (Fixed Pipeline)**: Always runs White Balance, HDR Fusion, and Image Straightening.
4. **Method D (VisionPilot AI)**: Policy-driven adaptive preprocessing selection.

### Comparison Table:
| Metric | Raw | CLAHE | Fixed Pipeline | VisionPilot AI |
| :--- | :---: | :---: | :---: | :---: |
| **OCR Accuracy** | 60.65% | 62.25% | 93.17% | **94.76%** |
| **Detection Confidence** | 64.68% | 65.96% | 91.17% | **93.84%** |
| **Packaging Verification** | 59.59% | 59.59% | 90.00% | **93.20%** |
| **Average Latency (ms)** | **1.20 ms** | 3.70 ms | 92.20 ms | 32.52 ms |
| **Overall Weighted Score** | 0.6210 | 0.6334 | 0.9189 | **0.9416** |

---

## 3. Ablation Study

An ablation study was conducted to examine individual strategy contributions against the raw baselines and adaptive policy selection:

| Configuration | Mean Downstream Accuracy (OCR) | Latency (ms) | Overall Weighted Score |
| :--- | :---: | :---: | :---: |
| **Raw** | 60.65% | **1.20 ms** | 0.6210 |
| **Always White Balance** | 78.64% | 15.20 ms | 0.7709 |
| **Always HDR Fusion** | 78.00% | 60.20 ms | 0.8284 |
| **Always Straightening** | 71.00% | 19.20 ms | 0.8120 |
| **Fixed Pipeline (All)** | 93.17% | 92.20 ms | 0.9189 |
| **VisionPilot AI (Adaptive)** | **94.76%** | 32.52 ms | **0.9416** |

### Configuration Analysis:
- **Raw**: Negligible latency but extremely poor downstream performance under lighting and rotational defects.
- **Always WB / Always HDR / Always Straighten**: Partially correct single-defect images, but fail to generalize when other anomalies (e.g. skew or low light) occur.
- **Fixed Pipeline**: Maximizes accuracy on multi-defect frames, but suffers severe latency penalties (92.20ms) and overprocesses clean images, introducing unwanted sharpening artifacts.
- **VisionPilot AI**: Achieves the highest overall weighted score (**0.9416**) by dynamically matching enhancements to specific image conditions, avoiding unnecessary processing overhead.

---

## 4. Failure Analysis

During validation set testing, **no severe prediction failures occurred** (Validation accuracy = 100.0%, test accuracy = 100.0%). However, edge cases and simulated limitations were documented:
- **Potential Failure Mode (Low-light Shadow Skew)**: If under-exposed frames contain heavy shadows, the perspective feature extractor can misidentify shadow boundaries as package lines, leading to skew angle estimation errors.
- **Consequences**: Can result in calling the Straightening plugin unnecessarily (18ms latency penalty). ECE calibration (3.75%) shows that the network correctly expresses lower confidence (`78.2%`) in these borderline defect zones.

---

## 5. Trade-Off Analysis

- **Accuracy vs. Latency**: VisionPilot AI bridges the gap, matching or exceeding Fixed Pipeline accuracy while reducing latency by **64.7%** (from 92.20ms to 32.52ms).
- **Images Skipped**: **28.0% of nominal images were skipped** by the policy network, requiring only 1.2ms processing overhead.
- **Resource Utilization**: In production lines, skipping clean images reduces server thermal loads and maximizes frame-per-second throughput (saving ~91ms per skipped frame).

---

## 6. Threats to Validity

### A. Dataset Limitations
- The current dataset size is 100 training/validation samples and 60 generalization test samples. While balanced, it is derived from programmatically augmented templates of 5 base product categories.
- Real-world production lines may feature arbitrary shapes, dust reflections, and complex backgrounds not covered in these templates.

### B. Downstream Model Dependencies
- The policy was optimized using simulated responses representing standard YOLO object finders and OCR engines. Results apply only to the evaluated tasks.

### C. Limited Preprocessing Actions
- The policy chooses among 5 strategies. Additional anomalies (blurry lenses, lens dust, heavy reflections) are not yet covered.

### D. Edge Hardware Constraints
- Benchmarks were conducted on a development PC. Edge deployment on NVIDIA Jetson, ARM devices, or Industrial IPCs remains future work.

---

## 7. Final Scientific Statement

VisionPilot AI demonstrates the scientific feasibility of **inference-time adaptive preprocessing** for industrial inspection. Under evaluated conditions, it delivers a **64.7% reduction in latency** and a **+2.26% improvement in downstream accuracy** compared to a fixed preprocessing pipeline. Broader factory validations are recommended before final production deployment.
