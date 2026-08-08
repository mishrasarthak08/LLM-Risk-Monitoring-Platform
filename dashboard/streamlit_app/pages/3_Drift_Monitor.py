import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
from dashboard.streamlit_app.queries import get_active_features, get_drift_events

st.set_page_config(page_title="Drift Monitor", layout="wide")
st.title("🌊 Drift Monitor")

features = get_active_features()
selected_feature = st.selectbox("Feature:", features)

st.markdown("### Active Drift Alerts")
drift_df = get_drift_events(selected_feature)

st.dataframe(drift_df, use_container_width=True)

st.markdown("---")
st.subheader("Triage Alert")

alert_to_triage = st.selectbox("Select Alert to Triage:", drift_df[drift_df["status"] != "acknowledged"]["event_id"])

if alert_to_triage:
    st.info(f"Investigating {alert_to_triage}")
    
    st.markdown("**Metric**: `refusal_rate_z`")
    st.markdown("**Severity**: `CRITICAL`")
    st.markdown("**Details**: The refusal rate has spiked from the baseline 5.0% to 15.2% over the last 24 hours. (p-value: 0.001)")
    
    st.markdown("#### Outcome")
    outcome = st.radio("Resolution:", [
        "Investigating",
        "Confirmed quality issue -> escalate to incident + consider rollback",
        "Benign population shift -> approve reference rebuild",
        "False positive -> threshold needs tuning"
    ])
    
    st.text_area("Notes", "Traffic pattern shows an influx of malformed PDFs...")
    st.button("Save Triage State")
