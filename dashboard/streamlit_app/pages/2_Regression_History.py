import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
import pandas as pd
import altair as alt
from dashboard.streamlit_app.queries import get_active_features, mock_regression_history

st.set_page_config(page_title="Regression History", layout="wide")
st.title("📈 Regression History & Failure Analysis")

features = get_active_features()
selected_feature = st.selectbox("Feature:", features)

st.markdown("### Historical Pass Rate")
reg_df = mock_regression_history(selected_feature)

# Chart
chart = alt.Chart(reg_df).mark_line(point=True).encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('pass_rate:Q', scale=alt.Scale(domain=[0.5, 1.0]), title='Pass Rate'),
    color=alt.Color('gate_decision:N', scale=alt.Scale(domain=['allow', 'block'], range=['green', 'red']))
).properties(height=300)

st.altair_chart(chart, use_container_width=True)

st.markdown("### Regression Runs")
st.dataframe(
    reg_df[["run_id", "date", "status", "pass_rate", "gate_decision"]], 
    use_container_width=True
)

st.markdown("---")
st.header("Failure Analysis Workbench")
run_to_inspect = st.selectbox("Select Failed Run to Triage:", reg_df[reg_df["gate_decision"] == "block"]["run_id"])

if run_to_inspect:
    st.warning(f"Triaging run `{run_to_inspect}`")
    
    st.markdown("#### Case: `v1_edge_seasonal_income` (Newly Failing)")
    
    col_base, col_cand = st.columns(2)
    
    with col_base:
        st.markdown("**Baseline Output (Passed)**")
        st.info("The seasonal income of $40,000 was correctly annualized.")
        st.markdown("*Judge Rationale: Accurately reflected Q4 seasonality.*")
        
    with col_cand:
        st.markdown("**Candidate Output (Failed)**")
        st.error("The applicant has an income of $40,000.")
        st.markdown("*Judge Rationale: Failed to annualize the Q4 seasonal income figure, resulting in a severe under-representation of revenue.*")
        
    st.markdown("#### Triage Action")
    st.selectbox("Tag Error Pattern:", ["hallucinated_figure", "missed_required_section", "bad_math", "formatting_regression"])
    st.button("Promote to Known Failure (Golden Set)")
