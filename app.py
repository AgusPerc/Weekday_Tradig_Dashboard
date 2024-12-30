import streamlit as st
import pandas as pd
from day_analytics_tab import render_metrics_tab

@st.cache_data
def load_preloaded_data():
    return pd.read_csv('bt_2024.csv')

def validate_columns(df):
    required_columns = [
        'short_entry', 'cover_price', 'shares', 
        'slippage_commission', 'date', 'pnl'
    ]
    df_columns = [col.lower() for col in df.columns]
    missing = [col for col in required_columns if col.lower() not in df_columns]
    return len(missing) == 0, missing

def validate_data(df):
    issues = []
    
    null_cols = df.columns[df.isnull().any()].tolist()
    if null_cols:
        issues.append(f"Found null values in columns: {', '.join(null_cols)}")
    
    numeric_cols = ['short_entry', 'cover_price', 'shares', 'slippage_commission', 'pnl']
    for col in numeric_cols:
        if not pd.to_numeric(df[col], errors='coerce').dtype.kind in 'fc':
            issues.append(f"Non-numeric values found in {col}")
            
    try:
        pd.to_datetime(df['date'])
    except:
        issues.append("Invalid date format in 'date' column")
        
    return issues

def process_data(df, initial_portfolio):
    is_valid, missing_cols = validate_columns(df)
    if not is_valid:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
        return False
    
    issues = validate_data(df)
    if issues:
        for issue in issues:
            st.warning(issue)
        return False
    
    return True

def main():
    st.set_page_config(layout="wide")
    st.title("Trading Strategy Analysis Dashboard")
    
    tab1, tab2 = st.tabs(["Day Analysis", "Coming Soon"])
    
    with tab1:
        use_preloaded = st.radio(
            "Choose data source",
            ["Use preloaded backtest", "Upload custom backtest"],
            horizontal=True
        )
        
        initial_portfolio = st.number_input(
            "Initial Portfolio Value", 
            min_value=1000.0, 
            value=75000.0,
            help="Starting portfolio value for calculations"
        )
        
        try:
            if use_preloaded == "Use preloaded backtest":
                df = load_preloaded_data()
                if process_data(df, initial_portfolio):
                    render_metrics_tab(df, initial_portfolio)
            else:
                uploaded_file = st.file_uploader("Upload backtest results", type=['csv', 'xlsx'])
                if uploaded_file:
                    with st.spinner("Processing your file..."):
                        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                        if process_data(df, initial_portfolio):
                            render_metrics_tab(df, initial_portfolio)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    with tab2:
        st.info("More analysis features coming soon!")

if __name__ == "__main__":
    main()