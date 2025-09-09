Auto Mudfish VPN Documentation
==============================

A secure, automated solution for connecting to Mudfish VPN with encrypted credential storage and comprehensive automation features.

Features
--------

- **Secure Credential Storage** - Encrypted using Windows DPAPI
- **Full Automation** - One-click VPN connection
- **Multiple Connection Methods** - HTTP requests and WebDriver fallback
- **Process Management** - Automatic Mudfish launcher detection and startup
- **Security First** - No plain text passwords, user-specific encryption
- **Comprehensive Logging** - Detailed operation logs and error reporting
- **Full Test Coverage** - 38 unit tests ensuring reliability

Quick Start
-----------

The easiest way to get started is with the GUI application:

.. code-block:: bash

   # Install dependencies
   pip install -r requirements.txt

   # Launch GUI (requires administrator privileges)
   python src/gui/gui.py

   # OR use the provided PowerShell script to run as administrator
   run_as_admin.ps1

For command-line usage, see the :ref:`command-line-interface` section.

Installation
------------

See the :ref:`installation` section for detailed installation instructions.

API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: API Documentation:

   modules/auto_mudfish
   modules/gui

User Guide
----------

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   command-line-interface
   gui-application
   configuration
   troubleshooting

Developer Guide
---------------

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide:

   development
   testing
   contributing
   architecture

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

