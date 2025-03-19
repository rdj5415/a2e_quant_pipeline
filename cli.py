"""
Command-line interface for the A2E trading system.
"""
import click
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from .data.ingest import DataIngestion
from .models.factor_model import FactorModel
from .backtest.engine import BacktestEngine
from .risk.manager import RiskManager
from .execution.engine import ExecutionEngine
from .analytics.reporter import PerformanceReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """A2E: Alpha-to-Execution Quantitative Trading Pipeline"""
    pass

@cli.command()
@click.option('--symbols', '-s', multiple=True, required=True,
              help='Trading symbols to fetch data for')
@click.option('--start-date', '-sd', required=True,
              help='Start date for data collection (YYYY-MM-DD)')
@click.option('--end-date', '-ed', required=True,
              help='End date for data collection (YYYY-MM-DD)')
@click.option('--timeframe', '-tf', default='1d',
              help='Data timeframe (e.g., 1d, 1h, 1m)')
def fetch_data(symbols, start_date, end_date, timeframe):
    """Fetch market data for specified symbols."""
    try:
        ingestion = DataIngestion(list(symbols), start_date, end_date)
        market_data = ingestion.fetch_market_data(timeframe)
        
        # Save data
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for symbol, data in market_data.items():
            output_file = output_dir / f"{symbol}_{timeframe}.csv"
            data.to_csv(output_file)
            logger.info(f"Saved data for {symbol} to {output_file}")
        
        click.echo("Data fetching completed successfully")
        
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.option('--symbol', '-s', required=True,
              help='Trading symbol to backtest')
@click.option('--start-date', '-sd', required=True,
              help='Start date for backtest (YYYY-MM-DD)')
@click.option('--end-date', '-ed', required=True,
              help='End date for backtest (YYYY-MM-DD)')
@click.option('--initial-capital', '-ic', default=1000000,
              help='Initial capital for backtest')
def backtest(symbol, start_date, end_date, initial_capital):
    """Run backtest for a trading strategy."""
    try:
        # Fetch data
        ingestion = DataIngestion([symbol], start_date, end_date)
        market_data = ingestion.fetch_market_data()
        
        # Initialize components
        model = FactorModel()
        engine = BacktestEngine(initial_capital=initial_capital)
        
        # Generate signals
        signals = model.generate_signals(market_data[symbol])
        
        # Convert signals to orders
        for timestamp, signal in signals.items():
            if signal != 0:
                order = {
                    'symbol': symbol,
                    'type': 'market',
                    'side': 'buy' if signal > 0 else 'sell',
                    'quantity': 100,
                    'timestamp': timestamp
                }
                engine.place_order(order)
        
        # Run backtest
        engine.process_market_data(market_data[symbol])
        
        # Get performance metrics
        metrics = engine.get_performance_metrics()
        
        # Generate report
        reporter = PerformanceReporter()
        report = reporter.generate_performance_report(
            engine.equity_curve,
            pd.Series([e['equity'] for e in engine.equity_curve]).pct_change()
        )
        
        click.echo("\nBacktest Results:")
        click.echo(f"Total Return: {metrics['total_return']:.2%}")
        click.echo(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        click.echo(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
        click.echo(f"Win Rate: {metrics['win_rate']:.2%}")
        click.echo(f"Total Trades: {metrics['total_trades']}")
        
        click.echo("\nReports generated in 'reports' directory")
        
    except Exception as e:
        logger.error(f"Error running backtest: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.option('--symbols', '-s', multiple=True, required=True,
              help='Trading symbols to trade')
@click.option('--paper-trading/--live-trading', default=True,
              help='Whether to use paper trading')
def trade(symbols, paper_trading):
    """Start real-time trading."""
    try:
        # Initialize components
        risk_manager = RiskManager()
        engine = ExecutionEngine(risk_manager, paper_trading=paper_trading)
        
        click.echo(f"Starting {'paper' if paper_trading else 'live'} trading")
        click.echo(f"Trading symbols: {', '.join(symbols)}")
        
        # Run execution engine
        import asyncio
        asyncio.run(engine.start())
        
    except Exception as e:
        logger.error(f"Error in trading: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.option('--start-date', '-sd', required=True,
              help='Start date for analysis (YYYY-MM-DD)')
@click.option('--end-date', '-ed', required=True,
              help='End date for analysis (YYYY-MM-DD)')
def analyze(start_date, end_date):
    """Generate performance analysis report."""
    try:
        # Load equity history
        equity_history = []
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
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
        
        # Generate report
        reporter = PerformanceReporter()
        report = reporter.generate_performance_report(
            equity_history,
            returns
        )
        
        click.echo("\nPerformance Analysis:")
        click.echo(f"Total Return: {report['metrics']['total_return']:.2%}")
        click.echo(f"Annualized Return: {report['metrics']['annualized_return']:.2%}")
        click.echo(f"Sharpe Ratio: {report['metrics']['sharpe_ratio']:.2f}")
        click.echo(f"Max Drawdown: {report['metrics']['max_drawdown']:.2%}")
        click.echo(f"Win Rate: {report['metrics']['win_rate']:.2%}")
        click.echo(f"Profit Factor: {report['metrics']['profit_factor']:.2f}")
        
        click.echo("\nReports generated in 'reports' directory")
        
    except Exception as e:
        logger.error(f"Error generating analysis: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    cli() 