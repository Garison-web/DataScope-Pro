# DataScope Pro - Streamlit Data Analysis Dashboard

## Overview
A Streamlit-based data analysis dashboard that lets users upload CSV files and view KPIs, charts, and insights.

## Tech Stack
- Python 3.12
- Streamlit, Pandas, Plotly

## Project Structure
- `app.py` - Main Streamlit application
- `dataset.csv` - Default sample dataset
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit server config (port 5000, host 0.0.0.0, CORS/XSRF disabled for Replit proxy)

## Running
Workflow "Start application" runs: `streamlit run app.py --server.port 5000 --server.address 0.0.0.0`

## Deployment
Configured for autoscale deployment using streamlit.
