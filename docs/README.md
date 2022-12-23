ACP requires Python 3.9 or higher. For Debian-based systems that ship with Python 3.8, Python 3.9 or higher can be manually installed:

```shell
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt update
$ sudo apt install python3.9    # Or python3.10 or 3.11 or...
```

`acp.py` can then be invoked by `python3.9 acp.py` instead of `python3 acp.py`. 

If you're using a precompiled binary you do not need to worry about this.