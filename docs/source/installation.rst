Installation
============

System Requirements
-------------------

- Windows 10/11
- Python 3.8+ (for development)
- Chrome browser (for WebDriver fallback)
- Internet connection

Option 1: Executable Distribution (Recommended)
-----------------------------------------------

For users without Python, download the latest release from the `releases <https://github.com/aaronbcarlisle/auto-mudfish/tree/main/releases>`_ folder.

1. Download the latest version folder (e.g., `v1.0.1/`)
2. Run `install.bat` as Administrator
3. The application will be installed to `C:\Program Files\Auto Mudfish\`
4. Desktop and Start Menu shortcuts will be created

Option 2: Python Installation
-----------------------------

For development or if you prefer to run from source:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/aaronbcarlisle/auto-mudfish.git
      cd auto-mudfish

2. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

3. Launch the application:

   .. code-block:: bash

      # GUI (recommended)
      python src/gui/gui.py

      # Command line
      python src/main.py --setup

Prerequisites
-------------

Chrome Browser
~~~~~~~~~~~~~~

Auto Mudfish requires Chrome browser for WebDriver functionality. The application will automatically download the appropriate ChromeDriver version.

Administrator Privileges
~~~~~~~~~~~~~~~~~~~~~~~~

The GUI requires administrator privileges to launch Mudfish. You can either:

- Right-click the command prompt and select "Run as administrator"
- Use the provided `run_as_admin.ps1` file (PowerShell - recommended)

Verification
------------

To verify the installation:

1. Launch Auto Mudfish
2. Go to the "Credentials" tab
3. Set up your Mudfish username and password
4. Use the "Main" tab to test connection

If you encounter issues, check the "Logs" tab for detailed error information.
