"""
Backtesting engine for the A2E trading system.
"""
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..config.config import BACKTEST_PARAMS, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    filename=LOGGING_CONFIG["file"]
)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types supported by the backtesting engine."""
    MARKET = "market"
    LIMIT = "limit"

@dataclass
class Order:
    """Represents a trading order."""
    symbol: str
    order_type: OrderType
    side: str  # "buy" or "sell"
    quantity: float
    price: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class Position:
    """Represents a trading position."""
    def __init__(self, symbol: str, quantity: float, avg_price: float):
        self.symbol = symbol
        self.quantity = quantity
        self.avg_price = avg_price
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0

class BacktestEngine:
    """Implements a backtesting engine with limit order support."""
    
    def __init__(
        self,
        initial_capital: float = 1_000_000,
        commission_rate: float = 0.001,
        slippage: float = 0.0001
    ):
        """
        Initialize the backtesting engine.
        
        Args:
            initial_capital: Initial capital for trading
            commission_rate: Commission rate per trade
            slippage: Slippage rate per trade
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trades: List[Dict] = []
        self.equity_curve = []
        
    def place_order(self, order: Order) -> None:
        """
        Place a new order.
        
        Args:
            order: Order to place
        """
        self.orders.append(order)
        logger.info(f"Placed order: {order}")
    
    def process_market_data(self, data: pd.DataFrame) -> None:
        """
        Process market data and execute orders.
        
        Args:
            data: DataFrame with OHLCV data
        """
        for timestamp, row in data.iterrows():
            # Update positions
            self._update_positions(row)
            
            # Process pending orders
            self._process_orders(row)
            
            # Record equity
            self._record_equity(timestamp)
    
    def _update_positions(self, market_data: pd.Series) -> None:
        """Update position values and calculate PnL."""
        for symbol, position in self.positions.items():
            current_price = market_data['close']
            position.unrealized_pnl = (
                position.quantity * (current_price - position.avg_price)
            )
    
    def _process_orders(self, market_data: pd.Series) -> None:
        """Process pending orders based on current market data."""
        remaining_orders = []
        
        for order in self.orders:
            if order.order_type == OrderType.MARKET:
                self._execute_market_order(order, market_data)
            elif order.order_type == OrderType.LIMIT:
                if self._should_execute_limit_order(order, market_data):
                    self._execute_limit_order(order, market_data)
                else:
                    remaining_orders.append(order)
        
        self.orders = remaining_orders
    
    def _should_execute_limit_order(
        self,
        order: Order,
        market_data: pd.Series
    ) -> bool:
        """Check if a limit order should be executed."""
        if order.side == "buy":
            return market_data['low'] <= order.price
        else:  # sell
            return market_data['high'] >= order.price
    
    def _execute_market_order(
        self,
        order: Order,
        market_data: pd.Series
    ) -> None:
        """Execute a market order."""
        price = market_data['close'] * (1 + self.slippage if order.side == "buy" else 1 - self.slippage)
        self._execute_order(order, price)
    
    def _execute_limit_order(
        self,
        order: Order,
        market_data: pd.Series
    ) -> None:
        """Execute a limit order."""
        self._execute_order(order, order.price)
    
    def _execute_order(self, order: Order, price: float) -> None:
        """Execute an order and update positions."""
        # Calculate commission
        commission = order.quantity * price * self.commission_rate
        
        # Update capital
        if order.side == "buy":
            cost = order.quantity * price + commission
            self.current_capital -= cost
        else:  # sell
            proceeds = order.quantity * price - commission
            self.current_capital += proceeds
        
        # Update position
        if order.symbol in self.positions:
            position = self.positions[order.symbol]
            if order.side == "buy":
                # Update average price
                total_cost = position.quantity * position.avg_price + order.quantity * price
                position.quantity += order.quantity
                position.avg_price = total_cost / position.quantity
            else:  # sell
                # Calculate realized PnL
                pnl = (price - position.avg_price) * order.quantity
                position.realized_pnl += pnl
                position.quantity -= order.quantity
                
                if position.quantity == 0:
                    del self.positions[order.symbol]
        else:
            if order.side == "buy":
                self.positions[order.symbol] = Position(
                    order.symbol,
                    order.quantity,
                    price
                )
        
        # Record trade
        self.trades.append({
            'timestamp': order.timestamp,
            'symbol': order.symbol,
            'side': order.side,
            'quantity': order.quantity,
            'price': price,
            'commission': commission
        })
    
    def _record_equity(self, timestamp: datetime) -> None:
        """Record current portfolio equity."""
        total_equity = self.current_capital
        
        for position in self.positions.values():
            total_equity += position.quantity * position.avg_price
        
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': total_equity
        })
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.equity_curve:
            return {}
        
        equity_df = pd.DataFrame(self.equity_curve)
        returns = equity_df['equity'].pct_change()
        
        total_return = (equity_df['equity'].iloc[-1] / self.initial_capital) - 1
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        max_drawdown = (
            equity_df['equity'].cummax() - equity_df['equity']
        ).max() / equity_df['equity'].cummax()
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': (returns > 0).mean(),
            'total_trades': len(self.trades)
        }

def main():
    """Main function to demonstrate the backtesting engine."""
    # Example usage
    from ..data.ingest import DataIngestion
    from ..models.factor_model import FactorModel
    
    # Fetch data
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    ingestion = DataIngestion(symbols, start_date, end_date)
    market_data = ingestion.fetch_market_data()
    
    # Initialize backtesting engine
    engine = BacktestEngine()
    
    # Generate signals using factor model
    model = FactorModel()
    signals = model.generate_signals(market_data["AAPL"])
    
    # Convert signals to orders
    for timestamp, signal in signals.items():
        if signal != 0:
            order = Order(
                symbol="AAPL",
                order_type=OrderType.MARKET,
                side="buy" if signal > 0 else "sell",
                quantity=100,
                timestamp=timestamp
            )
            engine.place_order(order)
    
    # Run backtest
    engine.process_market_data(market_data["AAPL"])
    
    # Get performance metrics
    metrics = engine.get_performance_metrics()
    logger.info(f"Backtest results: {metrics}")

if __name__ == "__main__":
    main() 