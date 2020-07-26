#!/usr/bin/env python
import os
from app import app

#use for 'flask db init'
if True:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

else:
    if __name__ == '__main__':
        app.run(debug=True, ssl_context=('cert.pem','key.pem'), port=app.config['PORT'])

#if os.getenv('FLASK_APP',None) is None:
#    os.environ['FLASK_APP'] = 'runner.py'
#cli: flask run --cert=adhoc
