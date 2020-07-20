#!/bin/bash
virtualenv flask
cd flask
source bin/activate || exit

pip install setuptools --upgrade
pip install cffi --upgrade
pip install enum34 ipaddress
pip install pyOpenSSL==19.0.0
pip install cryptography==2.7
pip install requests oauthlib
pip install flask==0.12.5
pip install werkzeug==0.14.0
pip install dpath==1.4.2
pip install pygresql
pip install flask_login
pip install flask-sqlalchemy
pip install psycopg2
