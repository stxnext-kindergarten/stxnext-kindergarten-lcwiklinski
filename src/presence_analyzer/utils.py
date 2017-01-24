# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import logging
import threading
import time
from datetime import datetime
from functools import wraps
from json import dumps

from flask import Response
from lxml import etree

from main import app

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


lock = threading.Lock()

def cache(expire_time=60):
    """
    Cache decorator. Return cached data if it's not expired.
    """
    cache = {}
    timeout = {}

    lock = threading.Lock()
    def decorator_wrapper(function):
        lock = threading.Lock()
        def cache_wrapper(*args, **kwargs):
            if kwargs:
                key = args, frozenset(kwargs.items())
            else:
                key = args
            now = time.time()

            with lock:
                if key in cache:
                    if timeout[key] > now:
                        return cache[key]
                else:
                    rv = function(*args, **kwargs)
                    cache[key] = rv
                    timeout[key] = now + expire_time
                    return rv

        return cache_wrapper
    return decorator_wrapper


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


@cache(600)
def get_xml_data():
    """
    Extracts presence data from XML file and groups it by user_id.

    It creates structure like this:
    data = [
        {
            'user_id': 141,
            'name': 'Adam P.',
            'avatar': 'https://intranet.stxnext.pl/api/images/users/141',
        },
        {
            'user_id': 176,
            'name': 'Adrian K.',
            'avatar': 'https://intranet.stxnext.pl/api/images/users/176',
        },
    ]
    """
    with open(app.config['DATA_XML'], 'r') as xmlfile:
        xml_data = etree.parse(xmlfile)
        server = xml_data.find('server')
        link = '{}://{}'.format(
            server.find('protocol').text,
            server.find('host').text
        )
        users = xml_data.find('users')

        try:
            data = [
                {
                    'user_id': int(user.get('id')),
                    'name': user.find('name').text,
                    'avatar': '{}{}'.format(
                        link,
                        user.find('avatar').text
                    )
                } for i, user in enumerate(users.findall('user'))
            ]
        except (ValueError, TypeError):
            log.debug('Problem with line %d: ', i, exc_info=True)

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[] for i in range(7)] # one list for every day of the week.
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result

def group_by_weekday_by_start_end(items):
    """
    Groups presence entries by weekday start and end.
    """
    result = {i: {'start': [], 'end': []} for i in range(7)}

    for date in items:
        start = items[date]['start']
        end = items[date]['end']

        result[date.weekday()]['start'].append(seconds_since_midnight(start))
        result[date.weekday()]['end'].append(seconds_since_midnight(end))

    return result

def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
