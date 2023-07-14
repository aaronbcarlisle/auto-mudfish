Auto Mudfish
================================

A rough script that automates logging in and connecting to Mudfish.

---

# Installation
Ensure that Python 3 > and PIP are installed and in your `PATH`

[How To add a path to the PATH environment variable](https://learn.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14))
 - **python.exe:** `C:\Users\aaron\AppData\Local\Programs\Python\Python311`
 - **pip.exe:** `C:\Users\aaron\AppData\Local\Programs\Python\Python311\Scripts`


### Download and Install
##### **Run the following in a Command Prompt*

```batch
cd %USERPROFILE% && git clone https://github.com/aaronbcarlisle/auto-mudfish.git && cd auto-mudfish && pip install -r requirements.txt
```

# How To Use

### Commandline

```batch
$ python main.py -u <mudfish-username> -p <mudfish-password>
```

### Batch Script

Replace `<username>` and `<password>` with your own and save to disk as a `cmd` file next to the `main.py` script for an easy double-click solution.

```batch
@echo off
python .\main.py -u <username> -p <password>
pause

```

# Usage

It's suggested that you either use a rest API for a password manager, like Onepassword's [connect-sdk-python](https://youtu.be/0guOMTiwmhk](https://github.com/1Password/connect-sdk-python)), or to encrypt your password to disk.

```bash
usage: main.py [-h] -u USERNAME -p PASSWORD [-a ADMINPAGE] [-l LAUNCHER]

Auto-connect Mudfish

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username to Mudfish account.
  -p PASSWORD, --password PASSWORD
                        Password to Mudfish account.
  -a ADMINPAGE, --adminpage ADMINPAGE
                        Optional admin page url. (Default is 'http://127.0.0.1:8282/signin.html')
  -l LAUNCHER, --launcher LAUNCHER
                        Optional Mudfish Launcher location override. (Default is `C:/Program Files (x86)/Mudfish Cloud VPN/mudrun.exe` for Desktop.)
```

# Demo

###### ***NOTE:** I'm running a `cmd` file so I don't expose my password. Feel free to set it up however you please.*
![Mudfish Demo](resources/images/mudfish-demo.gif)
