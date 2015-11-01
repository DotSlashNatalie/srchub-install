#!/bin/bash

apt-get install -y --assume-yes python-pip wget
pip install python2-pythondialog
wget -qO- "https://srchub.org/p/srchub-install/source/file/master/srchub-install.py" | python