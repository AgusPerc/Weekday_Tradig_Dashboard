import streamlit as st
import pandas as pd
from day_analytics_funct import (
    calculate_portfolio_value, calculate_metrics, calculate_daily_metrics,
    calculate_monthly_metrics, calculate_daily_metrics_by_month
)

def display_metrics(metrics):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Net Profit", f"${metrics['net_profit']:.2f}")
        st.metric("Win Rate", f"{metrics['win_rate']:.2f}%")
        st.metric("Total Trades", f"{metrics['total_trades']}")
    with col2:
        st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
        st.metric("Avg Win", f"${metrics['avg_win']:.2f}")
        st.metric("Avg Loss", f"-${metrics['avg_loss']:.2f}")
    with col3:
        st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
        st.metric("Sortino Ratio", f"{metrics['sortino']:.2f}")
        st.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
    with col4:
        st.metric("Calmar Ratio", f"{metrics['calmar_ratio']:.2f}")
        st.metric("Initial Portfolio", f"${metrics['initial_portfolio']:,.2f}")
        st.metric("Final Portfolio", f"${metrics['final_portfolio']:,.2f}")

def display_daily_metrics(daily_metrics):
    st.dataframe(
        daily_metrics.style.format({
            'net_profit': '${:,.2f}',
            'trades': '{:,.0f}',
            'win_rate': '{:.2f}%',
            'avg_profit': '${:,.2f}',
            'profit_factor': '{:.2f}',
            'max_drawdown': '{:.2f}%',
            'volatility': '{:.4f}'
        }).background_gradient(subset=['net_profit', 'win_rate', 'profit_factor'], cmap='RdYlGn'),
        use_container_width=True
    )

def display_monthly_metrics(monthly_metrics):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chart_data = monthly_metrics[['month', 'net_profit']]
        st.bar_chart(chart_data.set_index('month'))
    
    with col2:
        st.dataframe(
            monthly_metrics.style.format({
                'net_profit': '${:,.2f}',
                'trades': '{:,.0f}',
                'win_rate': '{:.2f}%',
                'avg_profit': '${:,.2f}',
                'profit_factor': '{:.2f}',
                'max_drawdown': '{:.2f}%',
                'volatility': '{:.4f}'
            }).background_gradient(subset=['net_profit', 'win_rate'], cmap='RdYlGn'),
            use_container_width=True
        )

def display_daily_monthly_metrics(daily_monthly_metrics):
    pivot_df = daily_monthly_metrics.pivot(
        index='month', 
        columns='weekday', 
        values=['return_pct', 'win_rate', 'trades']
    )
    
    # Pre-format 'return_pct' and 'win_rate' with rounding and a % symbol
    for col in ['return_pct', 'win_rate']:
        for day in pivot_df.columns.get_level_values(1).unique():
            pivot_df[(col, day)] = pivot_df[(col, day)].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
    
    # Format 'trades' as integers without decimals
    for day in pivot_df.columns.get_level_values(1).unique():
        pivot_df[('trades', day)] = pivot_df[('trades', day)].apply(lambda x: f"{int(x)}" if pd.notna(x) else "")

    def color_returns(val):
        # Handle pre-formatted strings (e.g., "2.50%")
        if pd.isna(val) or val == "":
            return ''
        try:
            float_val = float(val.strip('%'))
        except ValueError:
            return ''
        norm_val = (float_val + 20) / 40
        norm_val = min(max(norm_val, 0), 1)
        intensity = int(255 * norm_val)
        return f'background-color: rgb{(intensity, 0, 0) if float_val < 0 else (0, intensity, 0)}'

    # Apply colors to 'return_pct' without affecting formatting
    styled_df = (
        pivot_df.style
        .map(
            color_returns, 
            subset=[(col, day) for col in ['return_pct'] for day in pivot_df.columns.get_level_values(1).unique()]
        )
    )

    st.dataframe(styled_df, use_container_width=True)

def render_metrics_tab(df, initial_portfolio):
    st.header("Trading Performance Analysis")
    
    start_date = pd.to_datetime(df['date'].min()).strftime('%Y-%m-%d')
    end_date = pd.to_datetime(df['date'].max()).strftime('%Y-%m-%d')
    st.write(f"Analysis Period: {start_date} to {end_date}")
    
    # Calculate portfolio values first
    df = calculate_portfolio_value(df, initial_portfolio)
    
    # Overall metrics
    overall = calculate_metrics(df, initial_portfolio)
    st.subheader("Overall Strategy Metrics")
    display_metrics(overall)
    
    # Monthly metrics
    monthly_metrics = calculate_monthly_metrics(df)
    st.subheader("Monthly Performance")
    display_monthly_metrics(monthly_metrics)
    
    # Daily metrics by month
    daily_monthly = calculate_daily_metrics_by_month(df, initial_portfolio)
    st.subheader("Daily Performance by Month")
    display_daily_monthly_metrics(daily_monthly)
    
    # Overall daily metrics
    daily_metrics = calculate_daily_metrics(df)
    st.subheader("Overall Performance by Weekday")
    display_daily_metrics(daily_metrics)