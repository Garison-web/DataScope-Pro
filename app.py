import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Setup page configuration
st.set_page_config(
    page_title="Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
<style>
/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #020617;
}

/* KPI Cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    padding: 15px;
    border-radius: 15px;
    color: white;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

/* Headers */
h1, h2, h3 {
    color: #e2e8f0;
}

/* Buttons */
button {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #020617;
}

/* KPI Cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    padding: 15px;
    border-radius: 15px;
    color: white;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

/* Headers */
h1, h2, h3 {
    color: #e2e8f0;
}

/* Buttons */
button {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

def main():
    st.sidebar.header("📁 Data Upload & Filters")
    
    # 1. Upload CSV functionality
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
    
    if uploaded_file is None:
        st.info("💡 Please upload a CSV dataset from the sidebar to view the dashboard.")
        try:
            df = pd.read_csv("dataset.csv")
            st.warning("⚠️ No file uploaded. Loading default `dataset.csv` for demonstration.")
        except FileNotFoundError:
            st.stop()
    else:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()
            
    # Preprocessing
    # Convert 'Date' column to datetime if it exists
    datetime_cols = [col for col in df.columns if 'date' in col.lower()]
    for col in datetime_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            pass
            
    # Calculate derived metrics
    if 'Revenue' not in df.columns:
        if 'Price' in df.columns and 'Quantity' in df.columns:
            df['Revenue'] = pd.to_numeric(df['Price'], errors='coerce') * pd.to_numeric(df['Quantity'], errors='coerce')

    # Handle missing values
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    cat_cols = df.select_dtypes(include=['object']).columns
    df[num_cols] = df[num_cols].fillna(0)
    df[cat_cols] = df[cat_cols].fillna('Unknown')

    # --- Interactive Filters ---
    st.sidebar.markdown("### 🔍 Filters")
    filtered_df = df.copy()
    
    # Category Filter
    categorical_options = df.select_dtypes(include=['object']).columns
    if 'Category' in categorical_options:
        filter_col = 'Category'
    elif len(categorical_options) > 0:
        filter_col = categorical_options[0]
    else:
        filter_col = None

    if filter_col:
        categories = ["All"] + list(filtered_df[filter_col].unique())
        selected_category = st.sidebar.selectbox(f"Select {filter_col}", categories)
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df[filter_col] == selected_category]
            
    # Date Filter
    if len(datetime_cols) > 0:
        date_col = datetime_cols[0]
        min_date = filtered_df[date_col].min()
        max_date = filtered_df[date_col].max()
        
        # Guard against NaT values in dates
        if not pd.isnull(min_date) and not pd.isnull(max_date):
            st.sidebar.markdown("### 📅 Date Range")
            # If dates are the same (e.g. single row), date_input might complain if min and max are identical.
            # Using try-except or ensuring safe differences.
            try:
                start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                filtered_df = filtered_df[(filtered_df[date_col] >= start_date) & (filtered_df[date_col] <= end_date)]
            except ValueError:
                # User might not select a complete range yet.
                pass

    # --- Dashboard View ---
    st.markdown("""
# 🚀 DataScope Pro
### Turn Your Data into Insights Instantly

Upload. Analyze. Visualize. Decide.
""")
    
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Insights", "📋 Data"])

    with tab1:
        st.title("📊 Data Analysis Dashboard")
        st.markdown("A complete, production-ready dashboard to analyze your datasets.")
        
        # KPI Cards
        st.subheader("🏆 Key Performance Indicators")
        col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Revenue' in filtered_df.columns:
            total_rev = filtered_df['Revenue'].sum()
            st.metric("Total Revenue", f"${total_rev:,.2f}")
        else:
            st.metric("Total Records", f"{len(filtered_df)}")
            
    with col2:
        if 'Quantity' in filtered_df.columns:
            total_qty = filtered_df['Quantity'].sum()
            st.metric("Total Items Sold", f"{total_qty:,.0f}")
        elif 'Order_ID' in filtered_df.columns:
            st.metric("Total Orders", f"{filtered_df['Order_ID'].nunique()}")
        else:
            st.metric("Total Columns", f"{len(filtered_df.columns)}")

    with col3:
        if 'Revenue' in filtered_df.columns and ('Quantity' in filtered_df.columns or 'Order_ID' in filtered_df.columns):
            orders = filtered_df['Order_ID'].nunique() if 'Order_ID' in filtered_df.columns else filtered_df['Quantity'].sum()
            avg_order = filtered_df['Revenue'].sum() / orders if orders > 0 else 0
            st.metric("Average Value", f"${avg_order:,.2f}")
        else:
            st.metric("Total Records", f"{len(filtered_df):,}")
            
        st.divider()
        
        # 2. Charts
        st.subheader("📈 Trend & Distribution Analysis")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Bar Chart
            if filter_col and 'Revenue' in filtered_df.columns:
                st.markdown("#### Revenue by Category")
                bar_data = filtered_df.groupby(filter_col)['Revenue'].sum().reset_index()
                fig_bar = px.bar(bar_data, x=filter_col, y='Revenue', color=filter_col, template='plotly_white')
                st.plotly_chart(fig_bar, use_container_width=True)
            elif filter_col:
                st.markdown(f"#### Count by {filter_col}")
                bar_data = filtered_df[filter_col].value_counts().reset_index()
                bar_data.columns = [filter_col, 'Count']
                fig_bar = px.bar(bar_data, x=filter_col, y='Count', color=filter_col, template='plotly_white')
                st.plotly_chart(fig_bar, use_container_width=True)

        with chart_col2:
            # Pie Chart
            if filter_col and 'Revenue' in filtered_df.columns:
                st.markdown("#### Overall Revenue Distribution")
                fig_pie = px.pie(filtered_df, names=filter_col, values='Revenue', hole=0.4, template='plotly_white')
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
                
            elif filter_col:
                st.markdown(f"#### {filter_col} Distribution")
                fig_pie = px.pie(filtered_df, names=filter_col, hole=0.4, template='plotly_white')
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.subheader("📈 Advanced Analytics")
        
        # Time series line chart
        if len(datetime_cols) > 0 and 'Revenue' in filtered_df.columns:
            date_col = datetime_cols[0]
            st.subheader("📉 Time-Series Revenue Trend")
            
            time_data = filtered_df.groupby(date_col)['Revenue'].sum().reset_index()
            fig_line = px.line(time_data, x=date_col, y='Revenue', markers=True, template='plotly_white')
            fig_line.update_traces(fill='tozeroy', line_color='#4CAF50')
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No date columns found for time-series analysis")

    with tab3:
        st.subheader("📋 Dataset Preview & Download")
        st.dataframe(filtered_df.head(50), use_container_width=True)
        
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Processed Dataset",
            data=csv_buffer.getvalue(),
            file_name="processed_data.csv",
            mime="text/csv",
        )
if __name__ == "__main__":
    main()
