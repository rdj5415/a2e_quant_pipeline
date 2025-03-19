Usage Guide
===========

This guide will help you get started with using the Alpha-to-Execution (A2E) package.

Basic Usage
----------

Fetching Market Data
~~~~~~~~~~~~~~~~~~

To fetch market data using yfinance:

.. code-block:: python

   from a2e.data import YFinanceDataIngestion
   from datetime import datetime, timedelta

   # Initialize data ingestion
   data_ingestion = YFinanceDataIngestion()

   # Fetch data for a symbol
   symbol = "AAPL"
   start_date = datetime.now() - timedelta(days=30)
   end_date = datetime.now()
   timeframe = "1h"

   data = data_ingestion.fetch_data(
       symbol=symbol,
       start_date=start_date,
       end_date=end_date,
       timeframe=timeframe
   )

Using CCXT for Cryptocurrency Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from a2e.data import CCXTDataIngestion

   # Initialize CCXT data ingestion
   data_ingestion = CCXTDataIngestion()

   # Fetch cryptocurrency data
   symbol = "BTC/USDT"
   start_date = datetime.now() - timedelta(days=7)
   end_date = datetime.now()
   timeframe = "1h"

   data = data_ingestion.fetch_data(
       symbol=symbol,
       start_date=start_date,
       end_date=end_date,
       timeframe=timeframe
   )

Running Backtests
~~~~~~~~~~~~~~~~

.. code-block:: python

   from a2e.backtest import BacktestEngine
   from a2e.models import MLModel
   from a2e.risk import RiskManager

   # Initialize components
   model = MLModel()
   risk_manager = RiskManager()
   backtest = BacktestEngine(
       model=model,
       risk_manager=risk_manager,
       initial_capital=100000
   )

   # Run backtest
   results = backtest.run(
       data=data,
       start_date=start_date,
       end_date=end_date
   )

   # Print performance metrics
   print(results.metrics)

Live Trading
~~~~~~~~~~~

.. code-block:: python

   from a2e.execution import ExecutionEngine
   from a2e.risk import RiskManager

   # Initialize components
   risk_manager = RiskManager()
   engine = ExecutionEngine(risk_manager=risk_manager)

   # Start trading
   engine.run(
       symbol=symbol,
       timeframe=timeframe,
       paper_trading=True  # Set to False for live trading
   )

Advanced Usage
-------------

Custom Risk Management
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from a2e.risk import RiskManager

   # Initialize risk manager with custom parameters
   risk_manager = RiskManager(
       max_position_size=100000,
       max_drawdown=0.1,
       max_daily_loss=0.05,
       max_leverage=2.0
   )

Custom Model Development
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from a2e.models import MLModel
   import torch
   import torch.nn as nn

   class CustomModel(nn.Module):
       def __init__(self):
           super().__init__()
           self.lstm = nn.LSTM(
               input_size=10,
               hidden_size=64,
               num_layers=2,
               batch_first=True
           )
           self.fc = nn.Linear(64, 1)

       def forward(self, x):
           lstm_out, _ = self.lstm(x)
           return self.fc(lstm_out[:, -1, :])

   # Initialize custom model
   model = CustomModel()

Performance Analysis
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from a2e.analytics import PerformanceAnalyzer

   # Initialize analyzer
   analyzer = PerformanceAnalyzer()

   # Generate performance report
   report = analyzer.generate_report(
       equity_history=results.equity_history,
       trades=results.trades,
       start_date=start_date,
       end_date=end_date
   )

   # Print report
   print(report)

Command Line Interface
--------------------

A2E provides a command-line interface for common operations:

Fetching Data
~~~~~~~~~~~

.. code-block:: bash

   a2e fetch-data --symbol AAPL --start-date 2023-01-01 --end-date 2023-12-31 --timeframe 1h

Running Backtests
~~~~~~~~~~~~~~~

.. code-block:: bash

   a2e backtest --symbol AAPL --start-date 2023-01-01 --end-date 2023-12-31 --initial-capital 100000

Live Trading
~~~~~~~~~~~

.. code-block:: bash

   a2e trade --symbol AAPL --timeframe 1h --paper-trading

Performance Analysis
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   a2e analyze --start-date 2023-01-01 --end-date 2023-12-31

Configuration
------------

A2E can be configured using environment variables or a configuration file:

Environment Variables
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   export A2E_API_KEY=your_api_key
   export A2E_SECRET_KEY=your_secret_key
   export A2E_RISK_MAX_POSITION_SIZE=100000
   export A2E_RISK_MAX_DRAWDOWN=0.1

Configuration File
~~~~~~~~~~~~~~~~

Create a `config.yaml` file:

.. code-block:: yaml

   api:
     key: your_api_key
     secret: your_secret_key

   risk:
     max_position_size: 100000
     max_drawdown: 0.1
     max_daily_loss: 0.05
     max_leverage: 2.0

   execution:
     paper_trading: true
     max_slippage: 0.001
     min_volume: 1000

Next Steps
---------

1. Check out the :doc:`api` reference for detailed documentation of all components
2. Look at the :doc:`development` guide if you want to contribute
3. Join our `Discord Community <https://discord.gg/your-server>`_ for support and discussions 