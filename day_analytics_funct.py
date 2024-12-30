import pandas as pd
import numpy as np
from scipy import stats

def calculate_portfolio_value(df, initial_portfolio):
    """Calculate portfolio value and returns using existing PnL values."""
    df = df.copy()
    df['adjusted_pnl'] = df['pnl']
    df['portfolio_value'] = initial_portfolio + df['pnl'].cumsum()
    df['daily_return'] = df['pnl'] / (df['portfolio_value'] - df['pnl'])
    df.loc[df['portfolio_value'] == df['pnl'], 'daily_return'] = 0
    return df

def calculate_metrics(df, initial_portfolio):
    """Calculate comprehensive strategy metrics."""
    net_profit = df['adjusted_pnl'].sum()
    final_portfolio_value = initial_portfolio + net_profit
    
    roll_max = df['portfolio_value'].cummax()
    daily_drawdown = df['portfolio_value'] - roll_max
    max_drawdown = (daily_drawdown / roll_max).min() * 100
    
    total_trades = len(df)
    winning_trades = df['adjusted_pnl'] > 0
    win_rate = (winning_trades.sum() / total_trades) * 100
    
    avg_win = df[winning_trades]['adjusted_pnl'].mean() if winning_trades.any() else 0
    avg_loss = abs(df[~winning_trades]['adjusted_pnl'].mean()) if (~winning_trades).any() else 0
    
    mean_daily_return = df['daily_return'].mean()
    daily_std = df['daily_return'].std() or 1
    downside_returns = df['daily_return'][df['daily_return'] < 0]
    downside_std = downside_returns.std() or 1
    
    annualized_return = mean_daily_return * 252
    sharpe_ratio = (mean_daily_return * np.sqrt(252)) / daily_std
    sortino_ratio = (mean_daily_return * np.sqrt(252)) / downside_std
    calmar_ratio = abs(annualized_return / (max_drawdown/100)) if max_drawdown != 0 else 0
    
    gross_profit = df[winning_trades]['adjusted_pnl'].sum() or 0
    gross_loss = abs(df[~winning_trades]['adjusted_pnl'].sum()) or 1
    profit_factor = gross_profit / gross_loss
    
    return {
        "initial_portfolio": initial_portfolio,
        "final_portfolio": final_portfolio_value,
        "net_profit": net_profit,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "calmar_ratio": calmar_ratio,
        "sortino": sortino_ratio,
        "sharpe": sharpe_ratio,
        "total_trades": total_trades
    }

def calculate_daily_metrics(df):
    """Calculate performance metrics by weekday."""
    df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
    
    daily_metrics = df.groupby('weekday').agg(
        net_profit=('adjusted_pnl', 'sum'),
        trades=('adjusted_pnl', 'count'),
        win_rate=('adjusted_pnl', lambda x: (len(x[x > 0]) / len(x)) * 100 if len(x) > 0 else 0),
        avg_profit=('adjusted_pnl', 'mean'),
        profit_factor=('adjusted_pnl', lambda x: abs(x[x > 0].sum() / x[x < 0].sum()) if (x < 0).any() else float('inf')),
        max_drawdown=('portfolio_value', lambda x: ((x - x.cummax()) / x.cummax()).min() * 100),
        volatility=('daily_return', 'std')
    ).reset_index()
    
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    daily_metrics['weekday'] = pd.Categorical(daily_metrics['weekday'], categories=weekday_order, ordered=True)
    return daily_metrics.sort_values('weekday')

def calculate_monthly_metrics(df):
    """Calculate metrics by month."""
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
    
    return df.groupby('month').agg(
        net_profit=('adjusted_pnl', 'sum'),
        trades=('adjusted_pnl', 'count'),
        win_rate=('adjusted_pnl', lambda x: (len(x[x > 0]) / len(x)) * 100),
        avg_profit=('adjusted_pnl', 'mean'),
        profit_factor=('adjusted_pnl', lambda x: abs(x[x > 0].sum() / x[x < 0].sum()) if (x < 0).any() else float('inf')),
        max_drawdown=('portfolio_value', lambda x: ((x - x.cummax()) / x.cummax()).min() * 100),
        volatility=('daily_return', 'std')
    ).reset_index()

def calculate_daily_metrics_by_month(df, initial_portfolio):
    """Calculate daily metrics for each month."""
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
    df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
    
    metrics = df.groupby(['month', 'weekday']).agg(
        net_profit=('adjusted_pnl', 'sum'),
        trades=('adjusted_pnl', 'count'),
        win_rate=('adjusted_pnl', lambda x: (len(x[x > 0]) / len(x)) * 100),
        avg_profit=('adjusted_pnl', 'mean'),
        profit_factor=('adjusted_pnl', lambda x: abs(x[x > 0].sum() / x[x < 0].sum()) if (x < 0).any() else float('inf')),
        volatility=('daily_return', 'std')
    )
    
    # Calculate percentage return
    metrics['return_pct'] = (metrics['net_profit'] / initial_portfolio) * 100
    
    metrics = metrics.reset_index()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    metrics['weekday'] = pd.Categorical(metrics['weekday'], categories=weekday_order, ordered=True)
    return metrics.sort_values(['month', 'weekday'])