# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import locale
import logging
from operator import itemgetter

from flask import abort, redirect
from flask_mako import render_template
from jinja2 import TemplateNotFound
from mako.exceptions import TopLevelLookupException

from presence_analyzer.main import app
from presence_analyzer.utils import (
    get_data,
    get_data_by_date,
    get_xml_data,
    get_year_and_months,
    group_by_weekday,
    group_by_weekday_by_start_end,
    jsonify,
    mean,
    top_five
)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def index():
    """
    Redirect to main page.
    """
    return redirect('presence_weekday')


@app.route('/<string:page_name>')
def static_page(page_name):
    """
    Template generator.
    """
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
    locale.setlocale(locale.LC_COLLATE, 'pl_PL.UTF-8')
    data = get_xml_data()

    return sorted(
        [
            {
                'user_id': value['user_id'],
                'name': value['name'],
                'avatar': value['avatar']
            }
            for value in data
        ],
        key=itemgetter('name'), cmp=locale.strcoll
    )


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


@app.route('/api/v1/years_and_months/', methods=['GET'])
@jsonify
def presence_years_and_months():
    """
    Returns work time for users grouped by month.
    Return list of dicts, eg:
    [
         ['2011 - December', 12, 2011],
         ['2011 - July', 7, 2011],
         [...],
    ]
    """
    data = get_year_and_months()
    result = [
        list(date) for date in
        set(tuple(date.values()) for date in data)
    ]

    return result


@app.route('/api/v1/top_five/<int:year>/<int:month>', methods=['GET'])
@jsonify
def top_five_worktime(year, month):
    """
    Returns top 5 work time for users grouped by date.
    """
    worktime = get_data_by_date()
    result = [
        (values)
        for date, values in worktime.iteritems()
        if date.year == year and date.month == month
    ]

    return top_five(result)


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
