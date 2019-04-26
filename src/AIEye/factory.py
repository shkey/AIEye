#!/usr/bin/env python3
from flask import Flask
from flask_mongoengine import MongoEngine

db = MongoEngine()


def create_app():
    app = Flask(__name__)

    app.config['DEBUG'] = True
    app.config['MONGODB_SETTINGS'] = {
        'db': 'AIEye',
        'host': 'mongo',
        'username': 'aieye',
        'password': '123456'
    }

    db.init_app(app)

    return app
