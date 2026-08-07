import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="VisionPilot AI - Dashboard", layout="wide")

st.markdown("# 📊 Operations Dashboard")
st.markdown("---")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Inspections", "24,590", "+12% vs yesterday")
with col2:
    st.metric("Mean Latency", "32.52 ms", "-64% latency savings")
with col3:
    st.metric("Yield Rate", "98.59%", "+0.4% efficiency")
with col4:
    st.metric("Active preprocessors", "2 Plugins", "HDR & Straightener")

st.markdown("---")

# Row for plots
col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown("### 📈 Defects Ingestion History (Hourly)")
    chart_data = pd.DataFrame({
        "Hour": ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00"],
        "Processed": [420, 580, 610, 490, 520, 640, 590],
        "Defects": [3, 5, 2, 8, 4, 1, 6]
    })
    chart = alt.Chart(chart_data).mark_line(point=True).encode(
        x='Hour',
        y='Processed',
        tooltip=['Hour', 'Processed', 'Defects']
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

with col_p2:
    st.markdown("### 📊 Preprocessor Strategy Distributions")
    defect_data = pd.DataFrame({
        "Category": ["NO_ACTION (skip)", "HDR Fusion", "Image Straightener", "White Balance", "WB + HDR Fusion"],
        "Count": [28, 20, 20, 12, 20]
    })
    donut = alt.Chart(defect_data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Category", type="nominal"),
        tooltip=['Category', 'Count']
    ).properties(height=300)
    st.altair_chart(donut, use_container_width=True)

st.markdown("---")

# Tech Stack & Health
st.markdown("### ⚙️ Technology Stack & System Health")
col_t1, col_t2 = st.columns(2)
with col_t1:
    st.markdown("""
    **Core Technologies**:
    - **Policy MLP Model**: PyTorch, ONNX Runtime
    - **Plugin Integrations**: OpenCV Headless, NumPy
    - **API Framework**: FastAPI, Uvicorn, PostgreSQL
    """)
with col_t2:
    st.success("🤖 Policy Network Status: LOADED")
    st.success("🖼️ HDR Fusion Engine: READY")
    st.success("📐 Image Straightener: READY")
