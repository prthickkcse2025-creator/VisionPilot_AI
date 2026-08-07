# Streamlit Deployment Guide - VisionPilot AI (Hackathon Edition)

This guide provides instructions on how to run, preview, and deploy the Streamlit-based demonstration portal.

---

## 1. Local Development Run

To launch the Streamlit dashboard on your local machine:
1. **Navigate to the app directory**:
   ```bash
   cd E:\VisionPilot_AI
   ```
2. **Install Streamlit dependencies**:
   ```bash
   pip install -r streamlit_app/streamlit_requirements.txt
   ```
3. **Execute the launcher**:
   ```bash
   streamlit run streamlit_app/app.py
   ```
4. **Access the portal**:
   Open `http://localhost:8501` inside your web browser.

---

## 2. Cloud Deployment (Streamlit Community Cloud)

To deploy the dashboard for free on Streamlit Community Cloud:
1. **Push your code to GitHub**:
   Ensure all changes are committed and pushed to your repository `https://github.com/KPrthick/VisionPilot_AI`.
2. **Access Streamlit Cloud**:
   Go to [share.streamlit.io](https://share.streamlit.io) and log in using your GitHub account.
3. **Deploy App**:
   - Click **Create App** or **New App**.
   - Select your Repository: `KPrthick/VisionPilot_AI`.
   - Set Branch: `main`.
   - Set Main file path: `streamlit_app/app.py`.
4. **Launch**:
   Click **Deploy!**. Streamlit will automatically read `streamlit_requirements.txt`, install python libraries, and assign a public URL.
