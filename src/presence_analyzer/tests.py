# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import datetime
import httplib
import json
import os.path
import unittest

import main
import utils
import views

TEST_DATA_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..',
    'runtime',
    'data',
    'test_data.csv',
)

TEST_DATA_XML = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..',
    'runtime',
    'data',
    'users.xml',
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({
            'DATA_CSV': TEST_DATA_CSV,
            'DATA_XML': TEST_DATA_XML
        })
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page load.
        """
        resp = self.client.get('/')

        self.assertEqual(resp.status_code, httplib.OK)


    def test_mainpage_header(self):
        """
        Test main page header.
        """
        resp = self.client.get('/', follow_redirects=True)

        self.assertEqual(resp.status_code, httplib.OK)
        self.assertIn('Presence analyzer', resp.data)

    def test_presence_by_weekday_header(self):
        """
        Test presence by weekday header.
        """
        resp = self.client.get('/presence_weekday', follow_redirects=True)

        self.assertEqual(resp.status_code, httplib.OK)
        self.assertIn('Presence by weekday', resp.data)


    def test_weekday_parameter(self):
        """
        Test presence by weekday api route parameter is correct.
        """
        resp = self.client.get(
            '/api/v1/presence_weekday/10',
            content_type='application/json',
        )

        self.assertEqual(resp.status_code, httplib.OK)

        weekdays = [
            ['Weekday', 'Presence (s)'],
            ['Mon', 0],
            ['Tue', 30047],
            ['Wed', 24465],
            ['Thu', 23705],
            ['Fri', 0],
            ['Sat', 0],
            ['Sun', 0],
        ]
        data = json.loads(resp.data)

        self.assertListEqual(weekdays, data)

    def test_weekday_parameter_incorrect(self):
        """
        Test presence by weekday api route parameter is incorrect.
        """
        resp = self.client.get(
            '/api/v1/presence_weekday/wrong',
            content_type='application/json',
        )

        self.assertEqual(resp.status_code, httplib.NOT_FOUND)

    def test_presence_mean_time_header(self):
        """
        Test presence mean time header.
        """
        resp = self.client.get('/mean_time_weekday', follow_redirects=True)

        self.assertEqual(resp.status_code, httplib.OK)
        self.assertIn('Presence mean time by weekday', resp.data)

    def test_mean_time_parameter(self):
        """
        Test presence by weekday api route parameter is correct.
        """
        resp = self.client.get(
            '/api/v1/mean_time_weekday/10',
            content_type='application/json',
        )

        self.assertEqual(resp.status_code, httplib.OK)

        weekdays = [
            ['Mon', 0],
            ['Tue', 30047.0],
            ['Wed', 24465.0],
            ['Thu', 23705.0],
            ['Fri', 0],
            ['Sat', 0],
            ['Sun', 0],
        ]
        data = json.loads(resp.data)

        self.assertListEqual(weekdays, data)

    def test_presence_by_start_end(self):
        """
        Test presence header of start end view and
        by start and end api result.
        """
        resp = self.client.get('/presence_start_end', follow_redirects=True)

        self.assertIn('Presence start-end weekday', resp.data)

        api = self.client.get(
            '/api/v1/presence_start_end/10',
            content_type='application/json',
        )

        result = [
            ['Mon', 0, 0],
            ['Tue', 34745.0, 64792.0],
            ['Wed', 33592.0, 58057.0],
            ['Thu', 38926.0, 62631.0],
            ['Fri', 0, 0],
            ['Sat', 0, 0],
            ['Sun', 0, 0],
        ]
        data = json.loads(api.data)

        self.assertListEqual(result, data)

    def test_mean_time_parameter_incorrect(self):
        """
        Test presence by weekday api route parameter is incorrect.
        """
        resp = self.client.get(
            '/api/v1/mean_time_weekday/wrong',
            content_type='application/json',
        )

        self.assertEqual(resp.status_code, httplib.NOT_FOUND)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, httplib.OK)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(len(data), 84)
        self.assertDictEqual(
            data[0],
            {
                'user_id': 141,
                'name': 'Adam P.',
                'avatar': 'https://intranet.stxnext.pl/api/images/users/141'
            },
        )

    def test_static_page(self):
        """
        Test static page method.
        """
        resp = self.client.get('/mean_time_weekday')
        page_not_found = self.client.get('/page_not_exist')

        self.assertEqual(resp.status_code, httplib.OK)
        self.assertTrue('mean_time_weekday' in resp.get_data(as_text=True))
        self.assertEqual(page_not_found.status_code, httplib.NOT_FOUND)
        self.assertTrue('Not Found' in page_not_found.get_data(as_text=True))


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({
            'DATA_CSV': TEST_DATA_CSV,
            'DATA_XML': TEST_DATA_XML
        })

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        sample_date = datetime.date(2013, 9, 10)

        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_get_xml_data(self):
        """
        Test parsing of XML file.
        """
        data = utils.get_xml_data()

        self.assertIsInstance(data, list)
        self.assertItemsEqual(data[0], ['user_id', 'name', 'avatar'])
        self.assertEqual(
            data[10]['avatar'],
            'https://intranet.stxnext.pl/api/images/users/49'
        )

    def test_group_by_weekday(self):
        """
        Test Group by weekday method.
        """
        self.assertEqual(
            utils.group_by_weekday(
                {
                    datetime.date(2013, 9, 10): {
                        'start': datetime.time(9, 39, 5),
                        'end': datetime.time(17, 59, 52),
                    },
                    datetime.date(2013, 9, 12): {
                        'start': datetime.time(10, 48, 46),
                        'end': datetime.time(17, 23, 51),
                    },
                    datetime.date(2013, 9, 11): {
                        'start': datetime.time(9, 19, 52),
                        'end': datetime.time(16, 7, 37),
                    },
                }
            ),
            [[], [30047], [24465], [23705], [], [], [],]
        )

    def test_group_by_weekday_by_start_end(self):
        """
        Test Group by weekday method.
        """
        self.assertEqual(
            utils.group_by_weekday_by_start_end(
                {
                    datetime.date(2013, 9, 10): {
                        'start': datetime.time(0, 0, 0),
                        'end': datetime.time(0, 0, 0),
                    },
                    datetime.date(2013, 9, 12): {
                        'start': datetime.time(10, 48, 46),
                        'end': datetime.time(17, 23, 51),
                    },
                    datetime.date(2013, 9, 11): {
                        'start': datetime.time(9, 19, 52),
                        'end': datetime.time(16, 7, 37),
                    }
                }
            ),
            {
                0: {'start': [], 'end': []},
                1: {'start': [0], 'end': [0]},
                2: {'start': [33592], 'end': [58057]},
                3: {'start': [38926], 'end': [62631]},
                4: {'start': [], 'end': []},
                5: {'start': [], 'end': []},
                6: {'start': [], 'end': []},
            }
        )

    def test_seconds_since_midnight(self):
        """
        Test seconds since midnight method.
        """
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(10, 30, 50)), 37850
        )

    def test_interval(self):
        """
        Test interval method.
        """
        self.assertEqual(
            utils.interval(
                datetime.time(10, 10, 10), datetime.time(10, 30, 50)
            ),
            1240,
        )
        self.assertEqual(
            utils.interval(
                datetime.time(10, 50, 30), datetime.time(10, 30, 50)
            ),
            -1180,
        )

    def test_interval_wrong_parameter(self):
        """
        Test interval method with incorrect parameters.
        """
        with self.assertRaises(AttributeError):
            utils.interval('asd', 5)

    def test_mean(self):
        """
        Test arithmetic mean method.
        """
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([2, 5, 10, 15]), 8)

def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
