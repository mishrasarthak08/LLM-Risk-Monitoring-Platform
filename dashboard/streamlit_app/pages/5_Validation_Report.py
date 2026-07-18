import streamlit as st
from datetime import datetime, timedelta
from dashboard.streamlit_app.queries import get_active_features

st.set_page_config(page_title="Validation Report Generator", layout="wide")
st.title("📄 Validation Report Generator")

st.markdown("""
This tool generates a self-contained, audit-ready report (PDF/Markdown) satisfying SR 11-7 / OCC 2011-12 requirements for ongoing model monitoring.
""")

features = get_active_features()
selected_feature = st.selectbox("Target Feature:", features)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", datetime.today())

st.markdown("### Included Evidence")
st.checkbox("Regression History (CI Gates)", value=True, disabled=True)
st.checkbox("Drift Events & Triage Logs", value=True, disabled=True)
st.checkbox("Judge Calibration Records", value=True, disabled=True)
st.checkbox("Golden Set Version Approvals", value=True, disabled=True)

if st.button("Generate Validation Report", type="primary"):
    with st.spinner("Compiling evidence log..."):
        # In reality, this calls report_builder.py across a date range
        import time
        time.sleep(2)
        
    st.success("Report Generated!")
    
    st.markdown("""
    ### Download
    [Download `validation_report_credit_memo_v1_20260617_20260717.pdf`](#)
    """)
