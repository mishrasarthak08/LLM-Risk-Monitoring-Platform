import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from dashboard.streamlit_app.queries import get_active_features, get_drift_events, get_calibration_status

st.set_page_config(page_title="LLM Risk Monitoring", page_icon="🏦", layout="wide")

st.title("🏦 LLM Model-Risk Monitoring Platform")
st.markdown("---")

st.header("Active Features")
features = get_active_features()
selected_feature = st.selectbox("Select Feature to view summary:", features)

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚠️ Active Drift Alerts")
    drift_df = get_drift_events(selected_feature)
    open_alerts = drift_df[drift_df["status"] != "acknowledged"]
    if open_alerts.empty:
        st.success("No active drift alerts.")
    else:
        st.warning(f"{len(open_alerts)} alerts require attention.")
        st.dataframe(open_alerts, use_container_width=True)

with col2:
    st.subheader("⚖️ Judge Calibration Status")
    cal_data = get_calibration_status(selected_feature)
    
    if cal_data["status"] == "calibrated":
        st.success(f"Judge is fully calibrated (Last updated: {cal_data['last_updated']})")
    else:
        st.error("Judge is stale or failed calibration! Regression gating is disabled.")
        
    st.dataframe(
        cal_data["dimensions"][["dimension", "kappa_score", "threshold", "passed"]],
        use_container_width=True
    )

st.markdown("---")
st.markdown("Navigate using the sidebar to explore Runs, Regressions, Drift, and Calibration Details.")
