import streamlit as st

st.set_page_config(page_title="VisionPilot AI - About", layout="wide")

st.markdown("# ℹ️ About VisionPilot AI")
st.markdown("---")

st.markdown("""
### 🚀 The Business Value
VisionPilot AI resolves the trade-off between latency and accuracy in industrial computer vision:
- **64.7% compute savings** by skipping unneeded image enhancements.
- **+32% accuracy gains** over un-preprocessed inputs.
- **28% of nominal images skipped**, saving processor thermal loads.

---

### 🧠 AI Technologies & Model Specifications
- **Inference-Aware Policy MLP**:
  - Hidden Layers: `[32, 16]`
  - Output Classes: 5 preprocessor options
  - Early Stopped: Epoch `55`
  - Validation Split: Template-grouped (leak-free)
  - Validation Accuracy: `100.0%`
  - ECE Calibration Error: `0.0375 (3.75%)`
- **HDR Fusion Module**: Merges multi-exposed frames under high dynamic range conditions using Mertens blend algorithms.
- **Image Straightener**: Resolves angular tilts of label coordinates using contour orientation extraction.

---

### 🔮 Future Scope & Milestones
- **Denoising and Super-resolution**: Integrate future wrappers to correct heavily blurred or low-resolution conveyer captures.
- **Edge Deployment Optimization**: Benchmarking ONNX model execution times directly on NVIDIA Jetson, ARM devices, or industrial IPC targets.
- **Factory-wide telemetry**: Sync multi-camera conveyor diagnostics telemetry back to a centralized dashboard.

---

### 👥 Hackathon Team Info
- **Team**: VisionPilot Creators v1.0
- **Project Status**: Stable Production Release (v1.0)
""")
