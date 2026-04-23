import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

st.set_page_config(
    page_title="DataScope Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern SaaS Dashboard CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global */
html, body, [class*="css"]  {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at top left, rgba(56, 189, 248, 0.08), transparent 50%),
        radial-gradient(ellipse at bottom right, rgba(139, 92, 246, 0.08), transparent 50%),
        linear-gradient(135deg, #0f172a 0%, #020617 100%);
    color: #e2e8f0;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0a0f1f 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.1);
}

[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
}

/* Brand block */
.brand-block {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 4px 20px 4px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    margin-bottom: 18px;
}
.brand-logo {
    width: 38px;
    height: 38px;
    border-radius: 11px;
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 6px 20px rgba(56, 189, 248, 0.35);
}
.brand-name {
    font-weight: 700;
    font-size: 18px;
    color: #f8fafc;
    line-height: 1.1;
}
.brand-sub {
    font-size: 11px;
    color: #64748b;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

.nav-label {
    font-size: 11px;
    letter-spacing: 1px;
    color: #64748b !important;
    text-transform: uppercase;
    margin: 12px 4px 6px 4px;
}

/* Sidebar radio styled as nav */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 4px;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    display: flex; align-items: center;
    padding: 9px 12px;
    border-radius: 10px;
    background: transparent;
    transition: all 0.2s ease;
    cursor: pointer;
    border: 1px solid transparent;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(56, 189, 248, 0.08);
    border-color: rgba(56, 189, 248, 0.15);
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(6,182,212,0.18), rgba(59,130,246,0.18));
    border-color: rgba(56, 189, 248, 0.35);
}

/* Top Navbar */
.top-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 22px;
    background: rgba(15, 23, 42, 0.55);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 16px;
    margin-bottom: 22px;
}
.nav-left { display: flex; align-items: center; gap: 14px; }
.nav-title { font-size: 20px; font-weight: 700; color: #f8fafc; }
.nav-sub { font-size: 13px; color: #94a3b8; }
.nav-right { display: flex; align-items: center; gap: 14px; }
.nav-search {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 13px;
    color: #94a3b8;
    min-width: 260px;
    display: flex; align-items: center; gap: 8px;
}
.nav-icon-btn {
    width: 38px; height: 38px;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.profile-chip {
    display: flex; align-items: center; gap: 10px;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    padding: 5px 12px 5px 5px;
    border-radius: 999px;
}
.avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg, #06b6d4, #8b5cf6);
    color: white; font-weight: 700; font-size: 13px;
    display: flex; align-items: center; justify-content: center;
}
.profile-name { font-size: 13px; color: #e2e8f0; font-weight: 500; }

/* Glass Card */
.glass-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 18px;
    padding: 22px;
    transition: all 0.25s ease;
}
.glass-card:hover {
    border-color: rgba(56, 189, 248, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(6, 182, 212, 0.12);
}

/* KPI Cards (override Streamlit metrics) */
div[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(148, 163, 184, 0.12);
    padding: 20px 22px;
    border-radius: 18px;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #06b6d4, #3b82f6, #8b5cf6);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(56, 189, 248, 0.35);
    box-shadow: 0 14px 38px rgba(6, 182, 212, 0.15);
}
div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    color: #34d399 !important;
}

/* Headers */
h1, h2, h3, h4 { color: #f1f5f9 !important; font-weight: 700 !important; }
.section-title {
    font-size: 18px; font-weight: 600; color: #f1f5f9;
    display: flex; align-items: center; gap: 10px;
    margin: 6px 0 14px 0;
}
.section-title .dot {
    width: 6px; height: 22px; border-radius: 3px;
    background: linear-gradient(180deg, #06b6d4, #3b82f6);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(15, 23, 42, 0.4);
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.1);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #94a3b8;
    padding: 8px 18px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #06b6d4, #3b82f6) !important;
    color: white !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 9px 20px;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(6, 182, 212, 0.45);
    filter: brightness(1.08);
}

/* Inputs in sidebar */
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] input {
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid rgba(148, 163, 184, 0.18) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* File uploader */
[data-testid="stFileUploader"] section {
    background: rgba(15, 23, 42, 0.5);
    border: 1.5px dashed rgba(56, 189, 248, 0.35);
    border-radius: 12px;
    padding: 14px;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(56, 189, 248, 0.7);
    background: rgba(56, 189, 248, 0.05);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.12);
}

/* Plotly chart cards */
[data-testid="stPlotlyChart"] {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 16px;
    padding: 12px;
    transition: all 0.25s ease;
}
[data-testid="stPlotlyChart"]:hover {
    border-color: rgba(56, 189, 248, 0.25);
}

/* Alerts */
[data-testid="stAlert"] {
    background: rgba(30, 41, 59, 0.55);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 12px;
    backdrop-filter: blur(12px);
}

/* Divider */
hr { border-color: rgba(148, 163, 184, 0.1) !important; }

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }

/* Settings page rows */
.setting-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}
.setting-label { font-weight: 500; color: #e2e8f0; }
.setting-desc { font-size: 12px; color: #94a3b8; margin-top: 2px; }
.badge {
    display: inline-block;
    padding: 4px 10px;
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
}
.badge.cyan {
    background: rgba(6, 182, 212, 0.15);
    color: #22d3ee;
    border-color: rgba(6, 182, 212, 0.3);
}
</style>
""", unsafe_allow_html=True)


PLOTLY_TEMPLATE = "plotly_dark"
CHART_COLORS = ["#06b6d4", "#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#ef4444", "#14b8a6"]


def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(148,163,184,0.1)", zerolinecolor="rgba(148,163,184,0.1)"),
        yaxis=dict(gridcolor="rgba(148,163,184,0.1)", zerolinecolor="rgba(148,163,184,0.1)"),
    )
    return fig


def render_navbar(page_title, page_sub):
    st.markdown(f"""
    <div class="top-navbar">
        <div class="nav-left">
            <div>
                <div class="nav-title">{page_title}</div>
                <div class="nav-sub">{page_sub}</div>
            </div>
        </div>
        <div class="nav-right">
            <div class="nav-search">🔍 <span>Search metrics, reports…</span></div>
            <div class="nav-icon-btn">🔔</div>
            <div class="nav-icon-btn">⚙️</div>
            <div class="profile-chip">
                <div class="avatar">DS</div>
                <div class="profile-name">Data Analyst</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_title(text, icon=""):
    st.markdown(f'<div class="section-title"><div class="dot"></div>{icon} {text}</div>', unsafe_allow_html=True)


def load_and_prepare(uploaded_file):
    if uploaded_file is None:
        try:
            df = pd.read_csv("dataset.csv")
            st.info("ℹ️ Showing the demo dataset. Upload your own CSV in the sidebar to analyze it.")
        except FileNotFoundError:
            st.warning("Please upload a CSV dataset from the sidebar to begin.")
            st.stop()
    else:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()

    datetime_cols = [c for c in df.columns if 'date' in c.lower()]
    for col in datetime_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            pass

    if 'Revenue' not in df.columns:
        if 'Price' in df.columns and 'Quantity' in df.columns:
            df['Revenue'] = pd.to_numeric(df['Price'], errors='coerce') * pd.to_numeric(df['Quantity'], errors='coerce')

    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    cat_cols = df.select_dtypes(include=['object', 'string']).columns
    df[num_cols] = df[num_cols].fillna(0)
    df[cat_cols] = df[cat_cols].fillna('Unknown')

    return df, datetime_cols


def apply_filters(df, datetime_cols):
    filtered_df = df.copy()
    categorical_options = df.select_dtypes(include=['object', 'string']).columns

    if 'Category' in categorical_options:
        filter_col = 'Category'
    elif len(categorical_options) > 0:
        filter_col = categorical_options[0]
    else:
        filter_col = None

    st.sidebar.markdown('<div class="nav-label">Filters</div>', unsafe_allow_html=True)
    if filter_col:
        categories = ["All"] + list(filtered_df[filter_col].unique())
        selected_category = st.sidebar.selectbox(f"{filter_col}", categories)
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df[filter_col] == selected_category]

    if len(datetime_cols) > 0:
        date_col = datetime_cols[0]
        min_date = filtered_df[date_col].min()
        max_date = filtered_df[date_col].max()
        if not pd.isnull(min_date) and not pd.isnull(max_date):
            try:
                start_date, end_date = st.sidebar.date_input(
                    "Date Range", [min_date, max_date],
                    min_value=min_date, max_value=max_date
                )
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                filtered_df = filtered_df[(filtered_df[date_col] >= start_date) & (filtered_df[date_col] <= end_date)]
            except ValueError:
                pass

    return filtered_df, filter_col


def render_kpis(filtered_df):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if 'Revenue' in filtered_df.columns:
            st.metric("Total Revenue", f"${filtered_df['Revenue'].sum():,.2f}", "+12.4%")
        else:
            st.metric("Total Records", f"{len(filtered_df):,}")
    with col2:
        if 'Quantity' in filtered_df.columns:
            st.metric("Items Sold", f"{filtered_df['Quantity'].sum():,.0f}", "+8.2%")
        elif 'Order_ID' in filtered_df.columns:
            st.metric("Total Orders", f"{filtered_df['Order_ID'].nunique():,}")
        else:
            st.metric("Total Columns", f"{len(filtered_df.columns)}")
    with col3:
        if 'Revenue' in filtered_df.columns and ('Quantity' in filtered_df.columns or 'Order_ID' in filtered_df.columns):
            orders = filtered_df['Order_ID'].nunique() if 'Order_ID' in filtered_df.columns else filtered_df['Quantity'].sum()
            avg_order = filtered_df['Revenue'].sum() / orders if orders > 0 else 0
            st.metric("Avg Order Value", f"${avg_order:,.2f}", "+3.1%")
        else:
            st.metric("Total Records", f"{len(filtered_df):,}")
    with col4:
        st.metric("Active Rows", f"{len(filtered_df):,}", f"{len(filtered_df.columns)} cols")


def page_dashboard(filtered_df, filter_col, datetime_cols):
    render_navbar("Dashboard Overview", "Real-time insights from your dataset")

    section_title("Key Performance Indicators", "🏆")
    render_kpis(filtered_df)

    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Trend & Distribution", "📈")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if filter_col and 'Revenue' in filtered_df.columns:
            bar_data = filtered_df.groupby(filter_col)['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
            fig_bar = px.bar(bar_data, x=filter_col, y='Revenue', title=f"Revenue by {filter_col}",
                             color='Revenue', color_continuous_scale=['#3b82f6', '#06b6d4', '#22d3ee'])
            st.plotly_chart(style_fig(fig_bar), width='stretch')
        elif filter_col:
            bar_data = filtered_df[filter_col].value_counts().reset_index()
            bar_data.columns = [filter_col, 'Count']
            fig_bar = px.bar(bar_data, x=filter_col, y='Count', title=f"Count by {filter_col}",
                             color='Count', color_continuous_scale=['#3b82f6', '#06b6d4', '#22d3ee'])
            st.plotly_chart(style_fig(fig_bar), width='stretch')

    with chart_col2:
        if filter_col and 'Revenue' in filtered_df.columns:
            fig_pie = px.pie(filtered_df, names=filter_col, values='Revenue', hole=0.55,
                             title=f"Revenue Share by {filter_col}", color_discrete_sequence=CHART_COLORS)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(style_fig(fig_pie), width='stretch')
        elif filter_col:
            fig_pie = px.pie(filtered_df, names=filter_col, hole=0.55,
                             title=f"{filter_col} Distribution", color_discrete_sequence=CHART_COLORS)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(style_fig(fig_pie), width='stretch')

    if len(datetime_cols) > 0 and 'Revenue' in filtered_df.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        section_title("Revenue Trend Over Time", "📉")
        date_col = datetime_cols[0]
        time_data = filtered_df.groupby(date_col)['Revenue'].sum().reset_index()
        fig_line = px.area(time_data, x=date_col, y='Revenue',
                           color_discrete_sequence=['#06b6d4'])
        fig_line.update_traces(line=dict(color='#06b6d4', width=2.5),
                               fillcolor='rgba(6, 182, 212, 0.15)')
        st.plotly_chart(style_fig(fig_line), width='stretch')


def page_analytics(filtered_df, filter_col, datetime_cols):
    render_navbar("Analytics", "Deep-dive analysis & advanced visualizations")

    section_title("Numerical Summary", "🧮")
    num_df = filtered_df.select_dtypes(include=['float64', 'int64'])
    if len(num_df.columns) > 0:
        st.dataframe(num_df.describe().T.style.format("{:.2f}"), width='stretch')
    else:
        st.info("No numeric columns available for analysis.")

    if len(num_df.columns) >= 2:
        st.markdown("<br>", unsafe_allow_html=True)
        section_title("Correlation Heatmap", "🌡️")
        corr = num_df.corr()
        fig_heat = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.columns,
            colorscale=[[0, '#1e293b'], [0.5, '#3b82f6'], [1, '#06b6d4']],
            text=corr.round(2).values, texttemplate="%{text}",
            textfont={"size": 11, "color": "white"}
        ))
        st.plotly_chart(style_fig(fig_heat), width='stretch')

    if len(datetime_cols) > 0 and 'Revenue' in filtered_df.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        section_title("Time-Series Revenue Trend", "📈")
        date_col = datetime_cols[0]
        time_data = filtered_df.groupby(date_col)['Revenue'].sum().reset_index()
        fig_line = px.line(time_data, x=date_col, y='Revenue', markers=True,
                           color_discrete_sequence=['#22d3ee'])
        fig_line.update_traces(line=dict(width=2.5))
        st.plotly_chart(style_fig(fig_line), width='stretch')


def page_reports(filtered_df):
    render_navbar("Reports", "Browse, preview and export your processed data")

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Rows", f"{len(filtered_df):,}")
    with c2: st.metric("Total Columns", f"{len(filtered_df.columns)}")
    with c3:
        size_kb = filtered_df.memory_usage(deep=True).sum() / 1024
        st.metric("Memory", f"{size_kb:,.1f} KB")

    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Dataset Preview", "📋")
    st.dataframe(filtered_df.head(100), width='stretch', height=420)

    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Processed Dataset (CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"datascope_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )


def page_settings():
    render_navbar("Settings", "Manage your workspace preferences")

    section_title("Workspace", "⚙️")
    st.markdown("""
    <div class="glass-card">
        <div class="setting-row">
            <div>
                <div class="setting-label">Theme</div>
                <div class="setting-desc">Currently using the Midnight Slate theme</div>
            </div>
            <div class="badge cyan">Dark Mode</div>
        </div>
        <div class="setting-row">
            <div>
                <div class="setting-label">Auto-refresh data</div>
                <div class="setting-desc">Reload uploaded datasets when modified</div>
            </div>
            <div class="badge">Enabled</div>
        </div>
        <div class="setting-row">
            <div>
                <div class="setting-label">Chart engine</div>
                <div class="setting-desc">High-performance interactive visuals</div>
            </div>
            <div class="badge cyan">Plotly</div>
        </div>
        <div class="setting-row" style="border-bottom:none;">
            <div>
                <div class="setting-label">Account</div>
                <div class="setting-desc">Signed in as Data Analyst</div>
            </div>
            <div class="badge">Active</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_title("About", "ℹ️")
    st.markdown("""
    <div class="glass-card">
        <div style="font-size:15px;color:#cbd5e1;line-height:1.7;">
            <b style="color:#f8fafc;">DataScope Pro</b> is a modern, dark-themed analytics dashboard built with
            Streamlit and Plotly. Upload any CSV file and instantly get KPIs, distribution charts,
            time-series trends, correlation analyses and exportable reports.
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    # Sidebar brand
    st.sidebar.markdown("""
    <div class="brand-block">
        <div class="brand-logo">📊</div>
        <div>
            <div class="brand-name">DataScope Pro</div>
            <div class="brand-sub">Analytics Suite</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)
    page = st.sidebar.radio(
        "Navigation",
        ["📊  Dashboard", "📈  Analytics", "📋  Reports", "⚙️  Settings"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown('<div class="nav-label">Data Source</div>', unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    df, datetime_cols = load_and_prepare(uploaded_file)
    filtered_df, filter_col = apply_filters(df, datetime_cols)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown(
        f"""<div style="padding:12px;background:rgba(6,182,212,0.08);border:1px solid rgba(6,182,212,0.2);border-radius:10px;">
        <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">Dataset</div>
        <div style="font-size:14px;color:#f1f5f9;font-weight:600;margin-top:4px;">{len(filtered_df):,} rows · {len(filtered_df.columns)} columns</div>
        </div>""",
        unsafe_allow_html=True
    )

    if page.strip().startswith("📊"):
        page_dashboard(filtered_df, filter_col, datetime_cols)
    elif page.strip().startswith("📈"):
        page_analytics(filtered_df, filter_col, datetime_cols)
    elif page.strip().startswith("📋"):
        page_reports(filtered_df)
    else:
        page_settings()


if __name__ == "__main__":
    main()
