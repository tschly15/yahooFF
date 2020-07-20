#!/usr/bin/env python
import os
from app import app

app.run(debug=True, ssl_context=('cert.pem','key.pem'), port=app.config['PORT'])

#if os.getenv('FLASK_APP',None) is None:
#    os.environ['FLASK_APP'] = 'runner.py'
#cli: flask run --cert=adhoc
