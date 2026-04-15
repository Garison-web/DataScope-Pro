# Interactive Data Analysis Dashboard

A complete, production-ready Data Analysis Dashboard using Python and Streamlit with a clean, modern UI.

## Features

- **Upload CSV Dataset**: Effortlessly upload and preview large datasets.
- **Data Preprocessing**: Handles missing values and calculates missing derived metrics (like Revenue).
- **Interactive Filters**: Dynamic date pickers, dropdown selectors, and layout toggles.
- **KPI Metrics**: Dynamic summary cards displaying relevant data stats (Total Revenue, Average Order Value, etc.).
- **Plotly Visualizations**: High-quality, interactive visualizations such as Bar, Line, and Pie charts.

## Deployment on Streamlit Cloud

1. Create a GitHub repository for your project and push these files (`app.py`, `requirements.txt`, etc.).
2. Go to [Streamlit Cloud](https://share.streamlit.io/) and sign in with your GitHub account.
3. Click on "New App" and select your repository, branch, and specify `app.py` as the main file path.
4. Click "Deploy". Streamlit will use `requirements.txt` to install dependencies and instantly host your application!

## Running Locally

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```
