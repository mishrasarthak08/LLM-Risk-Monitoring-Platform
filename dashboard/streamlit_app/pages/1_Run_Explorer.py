import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
import pandas as pd
from dashboard.streamlit_app.queries import get_active_features, mock_run_traces

st.set_page_config(page_title="Run Explorer", layout="wide")
st.title("🔍 Run Explorer")

features = get_active_features()
selected_feature = st.selectbox("Feature:", features)

st.markdown("### Recent Traces")
traces_df = mock_run_traces(selected_feature)

# Filter by error
show_errors_only = st.checkbox("Show only traces with errors")
if show_errors_only:
    traces_df = traces_df[traces_df["has_error"] == True]

st.dataframe(traces_df, use_container_width=True)

st.markdown("---")
st.subheader("Inspect Specific Trace")
trace_to_inspect = st.selectbox("Select Trace ID:", traces_df["trace_id"].tolist())

if trace_to_inspect:
    trace_data = traces_df[traces_df["trace_id"] == trace_to_inspect].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Latency", f"{trace_data['latency_ms']:.0f} ms")
    col2.metric("Cost", f"${trace_data['cost_usd']:.4f}")
    col3.metric("Status", "Error" if trace_data['has_error'] else "Success")
    
    st.markdown("#### Prompt Payload (Rendered)")
    st.code("{\"source_data\": \"...\", \"instruction\": \"Draft a credit memo...\"}", language="json")
    
    st.markdown("#### Model Response")
    st.text_area("Output", "This is the generated credit memo text...", height=150)
    
    st.markdown("#### Judge Rationale (If Scored)")
    st.info("**Factual Accuracy (1/1)**: All numbers match the source data exactly.")
