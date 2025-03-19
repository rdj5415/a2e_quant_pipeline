Installation Guide
================

This guide will help you install the Alpha-to-Execution (A2E) package and its dependencies.

Requirements
-----------

* Python 3.8 or higher
* pip (Python package installer)
* Git (for development installation)

Basic Installation
-----------------

The simplest way to install A2E is using pip:

.. code-block:: bash

   pip install a2e

This will install the latest stable version of A2E and its required dependencies.

Development Installation
-----------------------

For development purposes, you can install A2E in editable mode:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/a2e.git
   cd a2e

   # Create and activate a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install the package in editable mode with development dependencies
   pip install -e ".[dev]"

Dependencies
-----------

A2E requires several Python packages:

Core Dependencies:
~~~~~~~~~~~~~~~~~

* numpy>=1.21.0
* pandas>=1.3.0
* torch>=1.9.0
* scikit-learn>=0.24.2
* ccxt>=2.0.0
* yfinance>=0.1.63
* ta>=0.7.0
* matplotlib>=3.4.3
* seaborn>=0.11.2
* click>=8.0.1
* rich>=10.12.0
* aiohttp>=3.8.1
* asyncio>=3.4.3

Development Dependencies:
~~~~~~~~~~~~~~~~~~~~~~~

* pytest>=7.4.3
* pytest-asyncio>=0.21.1
* pytest-cov>=4.1.0
* pytest-mock>=3.12.0
* black>=23.11.0
* flake8>=6.1.0
* isort>=5.12.0
* mypy>=1.7.1
* sphinx>=7.2.6
* sphinx-rtd-theme>=1.3.0
* ipython>=8.17.2
* jupyter>=1.0.0

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

1. **CUDA/GPU Support**
   
   If you want to use GPU acceleration with PyTorch, you may need to install a CUDA-enabled version:

   .. code-block:: bash

      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

2. **CCXT Installation Issues**
   
   If you encounter issues installing CCXT, try:

   .. code-block:: bash

      pip install --upgrade pip
      pip install ccxt --upgrade

3. **Development Tools**
   
   For development, make sure to install all development dependencies:

   .. code-block:: bash

      pip install -e ".[dev]"

Getting Help
~~~~~~~~~~~

If you encounter any issues during installation:

1. Check the `GitHub Issues <https://github.com/yourusername/a2e/issues>`_ page
2. Join our `Discord Community <https://discord.gg/your-server>`_
3. Contact us at support@a2e.com

Next Steps
---------

After installation, you can:

1. Read the :doc:`usage` guide to get started
2. Check out the :doc:`api` reference for detailed documentation
3. Look at the :doc:`development` guide if you want to contribute 