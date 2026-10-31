import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Lab Operations & Quality Intelligence",
    page_icon="🧪",
    layout="wide"
)

@st.cache_data
def load_data():
    conn = sqlite3.connect('data/lab_data.db')
    query = "SELECT * FROM lab_operations"
    df = pd.read_sql(query, conn)
    conn.close()
    
    df['collection_timestamp'] = pd.to_datetime(df['collection_timestamp'])
    df['completion_timestamp'] = pd.to_datetime(df['completion_timestamp'])
    return df

df = load_data()

st.sidebar.header("🎛️ Control Panel")
selected_dept = st.sidebar.selectbox("Filter Department", options=["All"] + list(df['department'].unique()))

if selected_dept != "All":
    filtered_df = df[df['department'] == selected_dept]
else:
    filtered_df = df

st.title("🧪 Hospital Laboratory Operations & Quality Intelligence")
st.markdown("Real-time mission control for tracking sample turnaround efficiency, equipment bottlenecks, and clinical safety.")

col1, col2, col3, col4 = st.columns(4)

total_tests = len(filtered_df)
avg_tat = int(filtered_df['turnaround_time_mins'].mean())
critical_count = int(filtered_df['critical_flag'].sum())
rejection_rate = (filtered_df['is_rejected'].sum() / total_tests) * 100 if total_tests > 0 else 0

col1.metric("Total Tests Processed", f"{total_tests:,}")
col2.metric("Avg Turnaround Time (TAT)", f"{avg_tat} mins")
col3.metric("Critical Alerts Active", f"{critical_count}", delta_color="inverse")
col4.metric("Sample Rejection Rate", f"{rejection_rate:.1f}%")

st.markdown("---")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("⚡ Average TAT by Machine ID")
    machine_tat = filtered_df.groupby('machine_id')['turnaround_time_mins'].mean().reset_index()
    fig_machine = px.bar(
        machine_tat, x='machine_id', y='turnaround_time_mins',
        text_auto='.1f', labels={'machine_id': 'Machine', 'turnaround_time_mins': 'Avg TAT (Mins)'},
        color='turnaround_time_mins', color_continuous_scale='Reds'
    )
    fig_machine.update_layout(showlegend=False)
    st.plotly_chart(fig_machine, use_container_width=True, key="machine_tat_chart")

with row1_col2:
    st.subheader("🏥 Departmental Workload Distribution")
    dept_counts = filtered_df['department'].value_counts().reset_index()
    dept_counts.columns = ['department', 'count']
    fig_dept = px.pie(
        dept_counts, names='department', values='count', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_dept, use_container_width=True, key="dept_workload_chart")

st.markdown("---")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("⚠️ Pre-Analytical Sample Rejections")
    rejected_df = filtered_df[filtered_df['is_rejected'] == 1]
    condition_counts = rejected_df['sample_condition'].value_counts().reset_index()
    condition_counts.columns = ['condition', 'count']
    
    fig_reject = px.bar(
        condition_counts, x='condition', y='count',
        labels={'condition': 'Error Type', 'count': 'Number of Rejections'},
        color='count', color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig_reject, use_container_width=True, key="sample_rejections_chart")

with row2_col2:
    st.subheader("🚨 Live Critical Result Queue")
    critical_df = filtered_df[filtered_df['critical_flag'] == 1][['test_id', 'patient_id', 'department', 'machine_id', 'collection_timestamp']]
    st.dataframe(critical_df.head(10), use_container_width=True)