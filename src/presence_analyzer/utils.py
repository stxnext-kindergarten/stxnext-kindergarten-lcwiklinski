# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import logging
import pickle
import threading
import time

from collections import Counter, defaultdict
from datetime import datetime
from functools import wraps
from json import dumps
from operator import itemgetter

from flask import Response
from lxml import etree

from presence_analyzer.main import app

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
LOCK = threading.Lock()

cache = {}

def memoize(expire_time=60):
    """
    Cache decorator. Return cached data if it's not expired.
    """

    def decorator_wrapper(function):
        """
        Passing function as parameter.
        """
        lock = threading.Lock()

        def cache_wrapper(*args, **kwargs):
            """
            Operates on accepted *args and **kwargs.
            """
            key = pickle.dumps((args, kwargs))
            now = time.time()

            with lock:
                if key in cache and cache[key]['timeout'] > now:
                    return cache[key]['value']
                else:
                    result = function(*args, **kwargs)
                    cache[key] = {
                        'value': result,
                        'timeout': now + expire_time
                    }
                    return result
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


@memoize(600)
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
            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def get_year_and_months():
    """
    Extracts presence data from CSV file and takes unique years and months.

    Returns: list of dicts eg:
    [
        {
            'year': 2011,
            'month': 8,
            'date': '2011 - August'
        },
        {
            'year': 2013,
            'month': 8,
            'date': '2013 - August'
        }
    ]
    """
    data = []
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            try:
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.append({
                'year': date.year,
                'month': date.month,
                'date': date.strftime('%Y - %B')
            })

    return data


def get_data_by_date():
    """
    Converts representation of data return from get_data().

    Returns: Dict of dicts eg:
    {
        datetime.date(2013, 10, 1): {
            10: 31395,
            12: 45863
        },
        (...)
    }
    """
    data = get_data()
    result = {}

    for user_id, values in data.iteritems():
        for date, worktime in values.iteritems():
            if date in result:
                result[date][user_id] = interval(
                    worktime['start'], worktime['end']
                )
            else:
                result[date] = {
                    user_id: interval(worktime['start'], worktime['end'])
                }

    return result


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
    result = [[] for i in range(7)]  # one list for every day of the week.
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))

    return result


def top_five(items):
    """
    Summs month top 5 worktime for user.
    """
    month_total = defaultdict(list)
    for values in items:
        for user, worktime in values.iteritems():
            if user not in month_total:
                month_total[user] = 0

            month_total[user] += worktime

    result = dict(Counter(month_total).most_common(5))

    return sorted(result.items(), key=itemgetter(1), reverse=True)


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
