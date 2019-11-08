#!/usr/bin/env python
from app import app
app.run(debug=True, ssl_context='adhoc', port=app.port)
