"""
Data ingestion module for the A2E trading system.
"""
import logging
from typing import List, Dict, Optional
import pandas as pd
import yfinance as yf
import ccxt
from pathlib import Path
import dask.dataframe as dd
from concurrent.futures import ThreadPoolExecutor

from ..config.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    API_CONFIG,
    LOGGING_CONFIG
)

# Configure logging
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    filename=LOGGING_CONFIG["file"]
)
logger = logging.getLogger(__name__)

class DataIngestion:
    """Handles data ingestion from various sources."""
    
    def __init__(self, symbols: List[str], start_date: str, end_date: str):
        """
        Initialize the data ingestion system.
        
        Args:
            symbols: List of trading symbols
            start_date: Start date for data collection
            end_date: End date for data collection
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.exchange = self._setup_exchange()
        
    def _setup_exchange(self) -> Optional[ccxt.Exchange]:
        """Setup the exchange connection."""
        if API_CONFIG["data_provider"] == "ccxt":
            exchange = ccxt.binance({
                'apiKey': API_CONFIG["api_key"],
                'secret': API_CONFIG["api_secret"],
                'enableRateLimit': True
            })
            return exchange
        return None
    
    def fetch_market_data(self, timeframe: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Fetch market data for all symbols.
        
        Args:
            timeframe: Data timeframe (e.g., "1d", "1h", "1m")
            
        Returns:
            Dictionary mapping symbols to their respective DataFrames
        """
        logger.info(f"Fetching market data for {len(self.symbols)} symbols")
        
        if API_CONFIG["data_provider"] == "yfinance":
            return self._fetch_yfinance_data(timeframe)
        elif API_CONFIG["data_provider"] == "ccxt":
            return self._fetch_ccxt_data(timeframe)
        else:
            raise ValueError(f"Unsupported data provider: {API_CONFIG['data_provider']}")
    
    def _fetch_yfinance_data(self, timeframe: str) -> Dict[str, pd.DataFrame]:
        """Fetch data using yfinance."""
        data_dict = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_symbol = {
                executor.submit(self._fetch_single_yfinance, symbol, timeframe): symbol
                for symbol in self.symbols
            }
            
            for future in future_to_symbol:
                symbol = future_to_symbol[future]
                try:
                    data_dict[symbol] = future.result()
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        return data_dict
    
    def _fetch_single_yfinance(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Fetch data for a single symbol using yfinance."""
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=self.start_date,
            end=self.end_date,
            interval=timeframe
        )
        return df
    
    def _fetch_ccxt_data(self, timeframe: str) -> Dict[str, pd.DataFrame]:
        """Fetch data using CCXT."""
        if not self.exchange:
            raise ValueError("Exchange not properly initialized")
            
        data_dict = {}
        for symbol in self.symbols:
            try:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe=timeframe,
                    since=self.start_date,
                    limit=1000
                )
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                data_dict[symbol] = df
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        return data_dict
    
    def process_market_data(self, data_dict: Dict[str, pd.DataFrame]) -> None:
        """
        Process and save market data.
        
        Args:
            data_dict: Dictionary of DataFrames containing market data
        """
        logger.info("Processing market data")
        
        for symbol, df in data_dict.items():
            # Basic data cleaning
            df = df.dropna()
            df = df.sort_index()
            
            # Save processed data
            output_path = PROCESSED_DATA_DIR / f"{symbol}_processed.csv"
            df.to_csv(output_path)
            logger.info(f"Saved processed data for {symbol}")
    
    def run(self) -> None:
        """Run the complete data ingestion pipeline."""
        logger.info("Starting data ingestion pipeline")
        
        # Fetch market data
        market_data = self.fetch_market_data()
        
        # Process and save data
        self.process_market_data(market_data)
        
        logger.info("Completed data ingestion pipeline")

def main():
    """Main function to run the data ingestion pipeline."""
    # Example usage
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    ingestion = DataIngestion(symbols, start_date, end_date)
    ingestion.run()

if __name__ == "__main__":
    main() 