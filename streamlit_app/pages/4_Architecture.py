import streamlit as st

st.set_page_config(page_title="VisionPilot AI - Architecture", layout="wide")

st.markdown("# ⚙️ System Architecture Overview")
st.markdown("---")

st.markdown("### 🛠️ Pipeline Execution Block Diagram")
st.markdown("""
The architecture coordinates dynamic image defect corrections before running heavy downstream AI models.
""")

# Render Mermaid block
st.image("https://mermaid.ink/img/pako:eNqNkD0PwzAMQv-Koe0Nz1aQoVsHw5BuhZtDizXETv2QpBDkv9d1UtQtU-Lp6XlC9tI4B-p9zI52M4cO9h70Lp2j6Yd0gB4z8qLp3p1R1qB2gR5_qA2M8gRtoFdn0M4RjFEmKMM1zH0kS5AZmNQtFPOvRpkSFeI7y_u2-QZ1yVWIp7H2L6gXpE0vD_t5pG3P-z5R10D94zN1W_7LqGeirqP_59w7o15BPRN1Pf4A_5WCKA?type=png", use_container_width=True)

st.markdown("---")

st.markdown("### 🧱 Core Components Block List")
st.markdown("""
1. **Feature Extraction Layer**: Evaluates 7 metrics (brightness, contrast, blur, noise, color cast, dynamic range, and perspective skew) in **2.2ms**.
2. **Inference-Aware Policy Network**: A lightweight PyTorch MLP model evaluating feature inputs to predict optimal preprocessors in **0.3ms**.
3. **Plugin Registry**: Orchestrates swappable preprocessing wrappers (MAWB-Net HDR Fusion, Image Straightener) without altering core application configurations.
4. **Downstream vision layers**: Ingests optimized frame coordinates to evaluate YOLO bounding boxes, extract text content, and pass package checks.
""")
