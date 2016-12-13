# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
import os.path
from flask import Flask


MAIN_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'sample_data.csv'
)


app = Flask(__name__)  # pylint: disable=invalid-name
app.config.update(
    DEBUG = True,
    DATA_CSV = MAIN_DATA_CSV
)
