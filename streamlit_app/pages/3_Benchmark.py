import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="VisionPilot AI - Benchmarking", layout="wide")

st.markdown("# 📈 Scientific Benchmarking & Evaluation")
st.markdown("---")

st.markdown("### 📊 Performance Comparison Table")
metrics_table = pd.DataFrame({
    "Metric": ["OCR Accuracy", "Detection Confidence", "Packaging Score", "Average Latency (ms)", "Overall Weighted Score"],
    "Raw (Method A)": ["60.65%", "64.68%", "59.59%", "1.20 ms", "0.6210"],
    "CLAHE (Method B)": ["62.25%", "65.96%", "59.59%", "3.70 ms", "0.6334"],
    "Fixed Pipeline (Method C)": ["93.17%", "91.17%", "90.00%", "92.20 ms", "0.9189"],
    "VisionPilot AI (Method D)": ["94.76%", "93.84%", "93.20%", "32.52 ms", "0.9416"]
})
st.table(metrics_table)

st.markdown("---")

# Altair Charts
col_ch1, col_ch2 = st.columns(2)

with col_ch1:
    st.markdown("### ⚡ Latency Breakdown comparison (ms)")
    latency_data = pd.DataFrame({
        "Configuration": ["Raw", "CLAHE", "Fixed Pipeline", "VisionPilot AI"],
        "Latency (ms)": [1.2, 3.7, 92.2, 32.52]
    })
    chart_lat = alt.Chart(latency_data).mark_bar(size=40).encode(
        x=alt.X('Configuration', sort=None),
        y='Latency (ms)',
        color='Configuration'
    ).properties(height=300)
    st.altair_chart(chart_lat, use_container_width=True)

with col_ch2:
    st.markdown("### 🎯 Overall Weighted downstream Accuracy Score")
    accuracy_data = pd.DataFrame({
        "Configuration": ["Raw", "CLAHE", "Fixed Pipeline", "VisionPilot AI"],
        "Weighted Score": [0.6210, 0.6334, 0.9189, 0.9416]
    })
    chart_acc = alt.Chart(accuracy_data).mark_bar(size=40).encode(
        x=alt.X('Configuration', sort=None),
        y=alt.Y('Weighted Score', scale=alt.Scale(domain=[0.5, 1.0])),
        color='Configuration'
    ).properties(height=300)
    st.altair_chart(chart_acc, use_container_width=True)
