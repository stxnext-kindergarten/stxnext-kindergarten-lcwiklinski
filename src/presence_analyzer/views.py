# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import abort
from flask_mako import render_template
from jinja2 import TemplateNotFound

from main import app
from mako.exceptions import TopLevelLookupException
from utils import (
    get_data,
    get_xml_data,
    group_by_weekday,
    group_by_weekday_by_start_end,
    jsonify,
    mean,
)

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/', defaults={'page_name' : 'presence_weekday'})
@app.route('/<string:page_name>')
def static_page(page_name):
    try:
        return render_template('{}.html'.format(page_name))
    except (TemplateNotFound, TopLevelLookupException):
        abort(404)


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_xml_data()

    return [
        {
            'user_id': value['user_id'],
            'name': value['name'],
            'avatar': value['avatar']
        }
        for value in data
    ]

    return data


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result

@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_of_start_and_end_work(user_id):
    """
    Returns mean time of start and end of work.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday_by_start_end(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(values['start']), mean(values['end']))
        for weekday, values in weekdays.iteritems()
    ]

    return result
