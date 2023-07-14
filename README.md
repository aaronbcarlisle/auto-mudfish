Mudfish Auto
================================

A rough script that automates logging in and connecting to Mudfish.

---

# How To Use

### Setup
Ensure requirements are installed

```bash
$ pip install -r requirements.txt
```

### Run

```bash
$ python main.py -u <mudfish-username> -p <mudfish-password>
```

###### *NOTE: I'm running a `bash` file so I don't expose my password. Feel free to set it up however you please.*
![Mudfish Demo](resources/images/mudfish-demo.gif)

# Usage

It's suggested that you either use a rest API for a password manager, like Onepassword's [connect-sdk-python](https://youtu.be/0guOMTiwmhk](https://github.com/1Password/connect-sdk-python)), or to encrypt your password to disk.

```bash
usage: mudfish-auto/main.py [-h] -u USERNAME -p PASSWORD [-a ADMINPAGE] [-l LAUNCHER]

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
