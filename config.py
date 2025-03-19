"""
Configuration settings for the A2E trading system.
"""
import os
from pathlib import Path
from typing import Dict, List

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FEATURES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Trading parameters
TRADING_PARAMS = {
    "initial_capital": 1_000_000,
    "position_size": 0.02,  # 2% of capital per position
    "max_positions": 50,
    "stop_loss": 0.02,  # 2% stop loss
    "take_profit": 0.04,  # 4% take profit
}

# Backtesting parameters
BACKTEST_PARAMS = {
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "commission_rate": 0.001,  # 0.1% commission
    "slippage": 0.0001,  # 0.01% slippage
}

# Risk management parameters
RISK_PARAMS = {
    "max_drawdown": 0.15,  # 15% maximum drawdown
    "var_confidence": 0.95,
    "position_limit": 0.1,  # 10% of capital per position
    "sector_limit": 0.25,  # 25% of capital per sector
}

# Model parameters
MODEL_PARAMS = {
    "factor_model": {
        "lookback_period": 60,  # days
        "factor_count": 5,
        "rebalance_frequency": "monthly"
    },
    "stat_arb": {
        "lookback_period": 20,  # days
        "entry_threshold": 2.0,  # standard deviations
        "exit_threshold": 1.0
    },
    "rl_agent": {
        "state_dim": 10,
        "action_dim": 3,  # buy, sell, hold
        "learning_rate": 0.001,
        "batch_size": 64
    }
}

# API configurations
API_CONFIG = {
    "data_provider": "yfinance",  # or "alpha_vantage", "polygon", etc.
    "paper_trading": True,
    "api_key": os.getenv("API_KEY", ""),
    "api_secret": os.getenv("API_SECRET", "")
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": ROOT_DIR / "logs" / "a2e.log"
}

# Create logs directory
LOGGING_CONFIG["file"].parent.mkdir(parents=True, exist_ok=True)

# Feature engineering parameters
FEATURE_PARAMS = {
    "technical_indicators": [
        "sma", "ema", "rsi", "macd", "bollinger_bands",
        "atr", "volume_profile", "momentum"
    ],
    "fundamental_indicators": [
        "pe_ratio", "market_cap", "dividend_yield",
        "beta", "volatility"
    ],
    "sentiment_indicators": [
        "news_sentiment", "social_sentiment", "market_sentiment"
    ]
}

# Performance metrics
PERFORMANCE_METRICS = [
    "returns", "sharpe_ratio", "sortino_ratio",
    "max_drawdown", "win_rate", "profit_factor",
    "calmar_ratio", "information_ratio"
] 