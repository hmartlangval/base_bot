# i had issues where install failed saying OSError etc. etc, even if i was in the conda env
``python -m pip install --user browser-use``

- the ``--user`` key actually did the trick


--- how i installed browser-use locally
- folder structure is very important in python

## Folder structure of browser use
Maintain this exact folder structure for it to work in python when you custom build the package.
You can use any project directory as root

1. Any directory as "root"

```
root > browser_use
root > browser_use > **all browser use codes are in this folder**
root > pyproject.toml

```

2. To deploy: build it first using ``cd root && python -m build``
3. For build important to have ``setup.py`` or ``pyproject.toml`` AND ``README.md``
4. after build will be stored in ``dist\browser-use<verstion>.tar.gz and *whl``
5. install this using ``pip install <relative>\dist\browser-use-<version>.tar.gx or *.whl`` either one works
6. if install fails due to OSError then try module based install ``python -m pip install --user <path.tar.gz>``



# PACKING base_bot
Run ``python basebot_setup.py sdist``