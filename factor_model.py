"""
Factor-based trading model implementation.
"""
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats

from ..config.config import MODEL_PARAMS, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    filename=LOGGING_CONFIG["file"]
)
logger = logging.getLogger(__name__)

class FactorModel:
    """Implements a factor-based trading strategy."""
    
    def __init__(self, lookback_period: int = 60, factor_count: int = 5):
        """
        Initialize the factor model.
        
        Args:
            lookback_period: Number of days to look back for factor calculation
            factor_count: Number of factors to use
        """
        self.lookback_period = lookback_period
        self.factor_count = factor_count
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=factor_count)
        self.factors = None
        self.factor_returns = None
        
    def calculate_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate factor exposures from market data.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with factor exposures
        """
        logger.info("Calculating factor exposures")
        
        # Calculate basic technical factors
        factors = pd.DataFrame(index=data.index)
        
        # Momentum factor
        factors['momentum'] = data['close'].pct_change(self.lookback_period)
        
        # Volatility factor
        factors['volatility'] = data['close'].pct_change().rolling(
            self.lookback_period
        ).std()
        
        # Volume factor
        factors['volume'] = data['volume'].rolling(
            self.lookback_period
        ).mean()
        
        # Price-to-volume factor
        factors['price_volume'] = (
            data['close'] * data['volume']
        ).rolling(self.lookback_period).mean()
        
        # Trend factor
        factors['trend'] = (
            data['close'].rolling(self.lookback_period).mean() /
            data['close'].rolling(self.lookback_period).std()
        )
        
        # Scale factors
        factors_scaled = self.scaler.fit_transform(factors)
        
        # Apply PCA to get orthogonal factors
        self.factors = self.pca.fit_transform(factors_scaled)
        self.factors = pd.DataFrame(
            self.factors,
            index=factors.index,
            columns=[f'factor_{i+1}' for i in range(self.factor_count)]
        )
        
        return self.factors
    
    def calculate_factor_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate factor returns.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with factor returns
        """
        logger.info("Calculating factor returns")
        
        if self.factors is None:
            raise ValueError("Factors must be calculated first")
        
        # Calculate forward returns
        forward_returns = data['close'].pct_change().shift(-1)
        
        # Calculate factor returns using linear regression
        factor_returns = pd.DataFrame(index=self.factors.columns)
        
        for factor in self.factors.columns:
            X = self.factors[factor].values.reshape(-1, 1)
            y = forward_returns.values
            
            # Remove NaN values
            mask = ~np.isnan(y)
            X = X[mask]
            y = y[mask]
            
            # Calculate factor return using linear regression
            slope, _, r_value, _, _ = stats.linregress(X, y)
            factor_returns.loc[factor, 'return'] = slope
            factor_returns.loc[factor, 'r_squared'] = r_value ** 2
        
        self.factor_returns = factor_returns
        return factor_returns
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on factor exposures.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with trading signals (-1: sell, 0: hold, 1: buy)
        """
        logger.info("Generating trading signals")
        
        if self.factors is None or self.factor_returns is None:
            raise ValueError("Factors and factor returns must be calculated first")
        
        # Calculate expected returns
        expected_returns = pd.Series(0.0, index=data.index)
        
        for factor in self.factors.columns:
            factor_return = self.factor_returns.loc[factor, 'return']
            expected_returns += self.factors[factor] * factor_return
        
        # Generate signals based on expected returns
        signals = pd.Series(0, index=data.index)
        signals[expected_returns > 0.01] = 1  # Buy signal
        signals[expected_returns < -0.01] = -1  # Sell signal
        
        return signals
    
    def backtest(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Run a simple backtest of the factor strategy.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary with performance metrics
        """
        logger.info("Running backtest")
        
        # Calculate factors and generate signals
        self.calculate_factors(data)
        signals = self.generate_signals(data)
        
        # Calculate returns
        returns = data['close'].pct_change()
        strategy_returns = signals.shift(1) * returns
        
        # Calculate performance metrics
        total_return = (1 + strategy_returns).prod() - 1
        sharpe_ratio = np.sqrt(252) * strategy_returns.mean() / strategy_returns.std()
        max_drawdown = (strategy_returns.cumsum() - strategy_returns.cumsum().cummax()).min()
        
        performance = {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': (strategy_returns > 0).mean()
        }
        
        return performance

def main():
    """Main function to demonstrate the factor model."""
    # Example usage
    from ..data.ingest import DataIngestion
    
    # Fetch data
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    ingestion = DataIngestion(symbols, start_date, end_date)
    market_data = ingestion.fetch_market_data()
    
    # Run factor model
    model = FactorModel()
    performance = model.backtest(market_data["AAPL"])
    
    logger.info(f"Backtest results: {performance}")

if __name__ == "__main__":
    main() 