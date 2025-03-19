Welcome to Alpha-to-Execution (A2E)'s documentation!
==============================================

A2E is a comprehensive algorithmic trading system that combines machine learning models with robust execution and risk management capabilities.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   development
   changelog

Features
--------

* **Data Ingestion**: Support for multiple data sources including yfinance and CCXT
* **Signal Generation**: Machine learning models for trading signal generation
* **Risk Management**: Comprehensive risk controls and monitoring
* **Execution Engine**: Efficient order execution and management
* **Backtesting**: Historical performance simulation
* **Analytics**: Performance analysis and reporting

Quick Start
----------

Install the package:

.. code-block:: bash

   pip install a2e

Basic usage:

.. code-block:: python

   from a2e import ExecutionEngine, RiskManager

   # Initialize components
   risk_manager = RiskManager()
   engine = ExecutionEngine(risk_manager=risk_manager)

   # Start trading
   engine.run()

For more detailed information, see the :doc:`usage` guide.

Installation
-----------

See the :doc:`installation` guide for detailed installation instructions.

API Reference
------------

The complete API reference is available in the :doc:`api` section.

Development
----------

Information for developers can be found in the :doc:`development` guide.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 