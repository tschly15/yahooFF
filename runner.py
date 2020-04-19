#!/usr/bin/env python
import os
from app import app

if os.getenv('FLASK_APP',None) is None:
    os.environ['FLASK_APP'] = 'runner.py'

#app.run(debug=True, ssl_context='adhoc', port=app.port)
#cli: flask run --cert=adhoc

