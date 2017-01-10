# -*- coding: utf-8 -*-
"""
Defines views.
"""
from flask import (
    abort,
    redirect,
    render_template,
    url_for
)

from main import app
from utils import (
    get_data,
    group_by_weekday,
    group_by_weekday_by_start_end,
    jsonify,
    mean
)

import calendar
import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name

@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('presence_weekday'))

@app.route('/presence_weekday')
def presence_weekday():
    """
    Returns presence weekday page.
    """
    return render_template('presence_weekday.html')

@app.route('/mean_time_weekday')
def mean_time_weekday():
    """
    Returns mean time weekday page.
    """
    return render_template('mean_time_weekday.html')

@app.route('/presence_start_end')
def presence_start_end():
    """
    Returns presence start end page.
    """
    return render_template('presence_start_end.html')

@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


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
