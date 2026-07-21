import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
from dashboard.streamlit_app.queries import get_active_features, mock_calibration_status

st.set_page_config(page_title="Judge Calibration", layout="wide")
st.title("⚖️ Judge Calibration Status")

features = get_active_features()
selected_feature = st.selectbox("Feature:", features)

cal_data = mock_calibration_status(selected_feature)

if cal_data["status"] == "calibrated":
    st.success(f"**STATUS**: Calibrated. Safe for regression gating. (Last updated: {cal_data['last_updated']})")
else:
    st.error(f"**STATUS**: STALE/FAILED. Regression gating is blocked until recalibration.")

st.markdown("### Dimension Kappa Scores")
st.markdown("Cohen's Kappa agreement between the LLM Judge and 2+ human expert reviewers on a stratified sample.")

st.dataframe(cal_data["dimensions"], use_container_width=True)

st.markdown("---")
st.subheader("Trigger Recalibration")
st.markdown("Required quarterly, or whenever the underlying judge model updates.")
st.button("Start New Calibration Run")
