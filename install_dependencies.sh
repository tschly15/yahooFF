#!/bin/bash
virtualenv flask
cd flask
source bin/activate || exit

pip install setuptools --upgrade
pip install cffi --upgrade
pip install enum34 ipaddress
pip install flask requests pyopenssl cryptography oauthlib dpath
pip install pygresql
pip install flask_login
pip install flask-sqlalchemy
pip install flask-migrate
