#!/usr/bin/env python3
from gevent import monkey
from gevent.pywsgi import WSGIServer

from app import app

monkey.patch_all()

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
