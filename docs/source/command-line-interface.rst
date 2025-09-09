Command Line Interface
======================

The command-line interface provides full functionality for automated Mudfish VPN connections.

Basic Usage
-----------

.. code-block:: bash

   python src/main.py [OPTIONS]

Credential Management
--------------------

Store Credentials Securely
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py --setup

This will prompt you to enter your Mudfish username and password, which will be encrypted and stored securely using Windows DPAPI.

Use Stored Credentials
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py --use-stored

This uses the previously stored credentials to connect to Mudfish.

View Stored Credentials
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py --show-credentials

Shows stored credential information (password is hidden for security).

Clear Stored Credentials
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py --clear-credentials

Removes all stored credentials from secure storage.

Manual Authentication
---------------------

Use Explicit Credentials
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py -u username -p password

With Custom Admin Page
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py -u username -p password -a http://192.168.1.1:8282/signin.html

With Custom Launcher Path
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py -u username -p password -l "C:/Custom/Path/mudfish.exe"

Advanced Options
----------------

Verbose Logging
~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py --use-stored -v

Show Browser Window
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/main.py --use-stored --show-browser

This displays the browser window during operation for debugging purposes.

Complete Command Reference
--------------------------

.. code-block:: text

   usage: src/main.py [-h] [--setup] [--use-stored] [--show-credentials] [--clear-credentials] 
                      [-u USERNAME] [-p PASSWORD] [-a ADMINPAGE] [-l LAUNCHER] [-v]

   Auto-connect Mudfish VPN

   options:
     -h, --help            show this help message and exit
     --setup               Setup and store credentials securely
     --use-stored          Use stored credentials (no need to provide username/password)
     --show-credentials    Show stored credential information
     --clear-credentials   Clear stored credentials
     -u USERNAME, --username USERNAME
                           Username for the Mudfish account
     -p PASSWORD, --password PASSWORD
                           Password for the Mudfish account
     -a ADMINPAGE, --adminpage ADMINPAGE
                           Admin page URL (default: http://127.0.0.1:8282/signin.html)
     -l LAUNCHER, --launcher LAUNCHER
                           Custom Mudfish launcher path (default: auto-detect)
     -v, --verbose         Enable verbose logging

Examples
--------

First-time Setup
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Store credentials securely
   python src/main.py --setup

   # Connect using stored credentials
   python src/main.py --use-stored

Debugging Connection Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Enable verbose logging and show browser
   python src/main.py --use-stored -v --show-browser

Custom Network Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use custom admin page for different network
   python src/main.py --use-stored -a http://192.168.0.1:8282/signin.html
