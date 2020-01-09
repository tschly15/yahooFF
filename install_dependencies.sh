#!/bin/bash
cd flask
source bin/activate

pip install setuptools --upgrade
pip install cffi --upgrade
pip install enum34 ipaddress
pip install flask requests pyopenssl cryptography oauthlib dpath
pip install flask_login
pip install pygresql
