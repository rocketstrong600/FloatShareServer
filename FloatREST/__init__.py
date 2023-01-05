from flask import Flask
from logging.config import dictConfig
from FloatREST.database import db_session
import os

api_info = {
    "Version": 0.1,
    "API": "FloatREST",
    "FloatPackageCompat": 0.7
}

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

from FloatREST import route

app.logger.info("FloatShare Server Started")

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()