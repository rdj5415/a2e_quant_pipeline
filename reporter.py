"""
Analytics and reporting module for the A2E trading system.
"""
import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json
from pathlib import Path

from ..config.config import PERFORMANCE_METRICS, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    filename=LOGGING_CONFIG["file"]
)
logger = logging.getLogger(__name__)

class PerformanceReporter:
    """Implements performance analysis and reporting functionality."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the performance reporter.
        
        Args:
            output_dir: Directory to save reports and visualizations
        """
        self.output_dir = output_dir or Path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def calculate_performance_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        Args:
            returns: Portfolio returns series
            benchmark_returns: Optional benchmark returns series
            
        Returns:
            Dictionary of performance metrics
        """
        metrics = {}
        
        # Calculate basic return metrics
        metrics['total_return'] = (1 + returns).prod() - 1
        metrics['annualized_return'] = (1 + metrics['total_return']) ** (252 / len(returns)) - 1
        metrics['volatility'] = returns.std() * np.sqrt(252)
        metrics['sharpe_ratio'] = metrics['annualized_return'] / metrics['volatility']
        
        # Calculate drawdown metrics
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = cum_returns / rolling_max - 1
        metrics['max_drawdown'] = drawdowns.min()
        
        # Calculate win rate and profit factor
        metrics['win_rate'] = (returns > 0).mean()
        positive_returns = returns[returns > 0].sum()
        negative_returns = abs(returns[returns < 0].sum())
        metrics['profit_factor'] = positive_returns / negative_returns if negative_returns != 0 else float('inf')
        
        # Calculate information ratio if benchmark is provided
        if benchmark_returns is not None:
            excess_returns = returns - benchmark_returns
            tracking_error = excess_returns.std() * np.sqrt(252)
            metrics['information_ratio'] = excess_returns.mean() * 252 / tracking_error
        
        return metrics
    
    def generate_equity_curve(
        self,
        equity_history: List[Dict],
        benchmark_history: Optional[List[Dict]] = None
    ) -> go.Figure:
        """
        Generate equity curve visualization.
        
        Args:
            equity_history: List of equity values over time
            benchmark_history: Optional benchmark equity history
            
        Returns:
            Plotly figure object
        """
        df = pd.DataFrame(equity_history)
        
        fig = go.Figure()
        
        # Add portfolio equity curve
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['equity'],
            name='Portfolio',
            line=dict(color='blue')
        ))
        
        # Add benchmark if provided
        if benchmark_history:
            benchmark_df = pd.DataFrame(benchmark_history)
            fig.add_trace(go.Scatter(
                x=benchmark_df['timestamp'],
                y=benchmark_df['equity'],
                name='Benchmark',
                line=dict(color='gray', dash='dash')
            ))
        
        fig.update_layout(
            title='Portfolio Equity Curve',
            xaxis_title='Date',
            yaxis_title='Equity',
            template='plotly_white'
        )
        
        return fig
    
    def generate_drawdown_chart(self, equity_history: List[Dict]) -> go.Figure:
        """
        Generate drawdown visualization.
        
        Args:
            equity_history: List of equity values over time
            
        Returns:
            Plotly figure object
        """
        df = pd.DataFrame(equity_history)
        equity_series = df['equity']
        
        # Calculate drawdown
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=drawdown,
            name='Drawdown',
            fill='tozeroy',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title='Portfolio Drawdown',
            xaxis_title='Date',
            yaxis_title='Drawdown',
            template='plotly_white'
        )
        
        return fig
    
    def generate_monthly_returns_heatmap(
        self,
        returns: pd.Series
    ) -> go.Figure:
        """
        Generate monthly returns heatmap.
        
        Args:
            returns: Returns series
            
        Returns:
            Plotly figure object
        """
        # Convert returns to monthly
        monthly_returns = returns.resample('M').agg(lambda x: (1 + x).prod() - 1)
        
        # Create pivot table for heatmap
        monthly_returns.index = pd.to_datetime(monthly_returns.index)
        pivot_table = monthly_returns.groupby([
            monthly_returns.index.year,
            monthly_returns.index.month
        ]).first().unstack()
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=pivot_table.columns,
            y=pivot_table.index,
            colorscale='RdYlGn',
            text=np.round(pivot_table.values * 100, 2),
            texttemplate='%{text}%',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title='Monthly Returns Heatmap',
            xaxis_title='Month',
            yaxis_title='Year',
            template='plotly_white'
        )
        
        return fig
    
    def generate_performance_report(
        self,
        equity_history: List[Dict],
        returns: pd.Series,
        benchmark_history: Optional[List[Dict]] = None,
        benchmark_returns: Optional[pd.Series] = None
    ) -> Dict:
        """
        Generate comprehensive performance report.
        
        Args:
            equity_history: List of equity values over time
            returns: Returns series
            benchmark_history: Optional benchmark equity history
            benchmark_returns: Optional benchmark returns series
            
        Returns:
            Dictionary containing report data and visualizations
        """
        # Calculate performance metrics
        metrics = self.calculate_performance_metrics(returns, benchmark_returns)
        
        # Generate visualizations
        equity_curve = self.generate_equity_curve(equity_history, benchmark_history)
        drawdown_chart = self.generate_drawdown_chart(equity_history)
        monthly_returns = self.generate_monthly_returns_heatmap(returns)
        
        # Save visualizations
        equity_curve.write_html(self.output_dir / "equity_curve.html")
        drawdown_chart.write_html(self.output_dir / "drawdown_chart.html")
        monthly_returns.write_html(self.output_dir / "monthly_returns.html")
        
        # Save metrics to JSON
        with open(self.output_dir / "performance_metrics.json", 'w') as f:
            json.dump(metrics, f, indent=4)
        
        return {
            'metrics': metrics,
            'visualizations': {
                'equity_curve': equity_curve,
                'drawdown_chart': drawdown_chart,
                'monthly_returns': monthly_returns
            }
        }

def main():
    """Main function to demonstrate the performance reporter."""
    # Example usage
    from ..data.ingest import DataIngestion
    from ..backtest.engine import BacktestEngine
    
    # Fetch data
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    ingestion = DataIngestion(symbols, start_date, end_date)
    market_data = ingestion.fetch_market_data()
    
    # Initialize backtesting engine
    engine = BacktestEngine()
    
    # Generate some equity history
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    equity_history = []
    for date in dates:
        equity_history.append({
            'timestamp': date,
            'equity': 1_000_000 * (1 + np.random.normal(0, 0.01))
        })
    
    # Generate returns series
    returns = pd.Series(
        np.random.normal(0.0001, 0.01, len(dates)),
        index=dates
    )
    
    # Initialize reporter and generate report
    reporter = PerformanceReporter()
    report = reporter.generate_performance_report(
        equity_history,
        returns
    )
    
    logger.info(f"Performance metrics: {report['metrics']}")

if __name__ == "__main__":
    main() 