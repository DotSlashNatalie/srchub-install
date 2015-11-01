#!/bin/bash

rootcheck=`whoami`

if [ "$rootcheck" == "root" ]
then
    apt-get update
    apt-get install -y --assume-yes python-pip wget dialog vim
    pip install python2-pythondialog
    wget -qO- "https://srchub.org/p/srchub-install/source/file/master/srchub-install.py" | python
    cd /home/www/indefero/src
else
    echo "You must be root to use this script"
fi
