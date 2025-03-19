"""
Risk management module for the A2E trading system.
"""
import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime

from ..config.config import RISK_PARAMS, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    filename=LOGGING_CONFIG["file"]
)
logger = logging.getLogger(__name__)

@dataclass
class RiskMetrics:
    """Container for risk metrics."""
    var: float
    cvar: float
    volatility: float
    beta: float
    correlation: float
    drawdown: float

class RiskManager:
    """Implements risk management functionality."""
    
    def __init__(
        self,
        max_drawdown: float = 0.15,
        var_confidence: float = 0.95,
        position_limit: float = 0.1,
        sector_limit: float = 0.25
    ):
        """
        Initialize the risk manager.
        
        Args:
            max_drawdown: Maximum allowed drawdown
            var_confidence: Confidence level for VaR calculation
            position_limit: Maximum position size as fraction of capital
            sector_limit: Maximum sector exposure as fraction of capital
        """
        self.max_drawdown = max_drawdown
        self.var_confidence = var_confidence
        self.position_limit = position_limit
        self.sector_limit = sector_limit
        self.positions: Dict[str, float] = {}
        self.sector_exposures: Dict[str, float] = {}
        self.equity_history: List[Dict] = []
        
    def update_positions(self, positions: Dict[str, float]) -> None:
        """
        Update current positions.
        
        Args:
            positions: Dictionary mapping symbols to position sizes
        """
        self.positions = positions
        logger.info(f"Updated positions: {positions}")
    
    def update_sector_exposures(self, exposures: Dict[str, float]) -> None:
        """
        Update sector exposures.
        
        Args:
            exposures: Dictionary mapping sectors to exposure sizes
        """
        self.sector_exposures = exposures
        logger.info(f"Updated sector exposures: {exposures}")
    
    def update_equity(self, timestamp: datetime, equity: float) -> None:
        """
        Update equity history.
        
        Args:
            timestamp: Current timestamp
            equity: Current portfolio equity
        """
        self.equity_history.append({
            'timestamp': timestamp,
            'equity': equity
        })
    
    def calculate_risk_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None
    ) -> RiskMetrics:
        """
        Calculate risk metrics.
        
        Args:
            returns: Portfolio returns series
            benchmark_returns: Optional benchmark returns series
            
        Returns:
            RiskMetrics object containing various risk measures
        """
        # Calculate VaR and CVaR
        var = np.percentile(
            returns,
            (1 - self.var_confidence) * 100
        )
        cvar = returns[returns <= var].mean()
        
        # Calculate volatility
        volatility = returns.std() * np.sqrt(252)
        
        # Calculate beta and correlation if benchmark is provided
        beta = 1.0
        correlation = 0.0
        if benchmark_returns is not None:
            beta = np.cov(returns, benchmark_returns)[0, 1] / np.var(benchmark_returns)
            correlation = np.corrcoef(returns, benchmark_returns)[0, 1]
        
        # Calculate drawdown
        equity_series = pd.DataFrame(self.equity_history)['equity']
        drawdown = (
            equity_series.cummax() - equity_series
        ).max() / equity_series.cummax()
        
        return RiskMetrics(
            var=var,
            cvar=cvar,
            volatility=volatility,
            beta=beta,
            correlation=correlation,
            drawdown=drawdown
        )
    
    def check_position_limits(self, symbol: str, size: float) -> bool:
        """
        Check if a position size is within limits.
        
        Args:
            symbol: Trading symbol
            size: Proposed position size
            
        Returns:
            True if position is within limits, False otherwise
        """
        # Get current portfolio value
        if not self.equity_history:
            return True
        
        current_equity = self.equity_history[-1]['equity']
        position_value = size * current_equity
        
        # Check position limit
        if position_value > current_equity * self.position_limit:
            logger.warning(
                f"Position size {size} exceeds position limit for {symbol}"
            )
            return False
        
        return True
    
    def check_sector_limits(self, sector: str, exposure: float) -> bool:
        """
        Check if a sector exposure is within limits.
        
        Args:
            sector: Sector name
            exposure: Proposed sector exposure
            
        Returns:
            True if exposure is within limits, False otherwise
        """
        if exposure > self.sector_limit:
            logger.warning(
                f"Sector exposure {exposure} exceeds sector limit for {sector}"
            )
            return False
        
        return True
    
    def check_drawdown_limit(self) -> bool:
        """
        Check if current drawdown is within limits.
        
        Returns:
            True if drawdown is within limits, False otherwise
        """
        if not self.equity_history:
            return True
        
        equity_series = pd.DataFrame(self.equity_history)['equity']
        current_drawdown = (
            equity_series.cummax() - equity_series
        ).max() / equity_series.cummax()
        
        if current_drawdown > self.max_drawdown:
            logger.warning(f"Current drawdown {current_drawdown:.2%} exceeds limit")
            return False
        
        return True
    
    def generate_risk_report(self) -> Dict:
        """
        Generate a comprehensive risk report.
        
        Returns:
            Dictionary containing risk metrics and limits
        """
        if not self.equity_history:
            return {}
        
        equity_series = pd.DataFrame(self.equity_history)['equity']
        returns = equity_series.pct_change().dropna()
        
        risk_metrics = self.calculate_risk_metrics(returns)
        
        report = {
            'risk_metrics': {
                'var': risk_metrics.var,
                'cvar': risk_metrics.cvar,
                'volatility': risk_metrics.volatility,
                'beta': risk_metrics.beta,
                'correlation': risk_metrics.correlation,
                'drawdown': risk_metrics.drawdown
            },
            'position_limits': {
                'max_position_size': self.position_limit,
                'current_positions': self.positions
            },
            'sector_limits': {
                'max_sector_exposure': self.sector_limit,
                'current_exposures': self.sector_exposures
            },
            'drawdown_limits': {
                'max_drawdown': self.max_drawdown,
                'current_drawdown': risk_metrics.drawdown
            }
        }
        
        return report

def main():
    """Main function to demonstrate the risk manager."""
    # Example usage
    from ..data.ingest import DataIngestion
    from ..backtest.engine import BacktestEngine
    
    # Fetch data
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    ingestion = DataIngestion(symbols, start_date, end_date)
    market_data = ingestion.fetch_market_data()
    
    # Initialize risk manager
    risk_manager = RiskManager()
    
    # Simulate some positions and equity history
    risk_manager.update_positions({
        "AAPL": 0.05,  # 5% of capital
        "MSFT": 0.03,  # 3% of capital
        "GOOGL": 0.04  # 4% of capital
    })
    
    risk_manager.update_sector_exposures({
        "Technology": 0.12,  # 12% of capital
        "Communication": 0.08  # 8% of capital
    })
    
    # Generate some equity history
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    for date in dates:
        risk_manager.update_equity(date, 1_000_000 * (1 + np.random.normal(0, 0.01)))
    
    # Generate risk report
    report = risk_manager.generate_risk_report()
    logger.info(f"Risk report: {report}")

if __name__ == "__main__":
    main() 