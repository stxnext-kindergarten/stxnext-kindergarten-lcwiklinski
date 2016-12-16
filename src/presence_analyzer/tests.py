# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path, sys
import json
import datetime
import unittest

my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, my_path + '/../')

from presence_analyzer import main, views, utils

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
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
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_mainpage_header(self):
        """
        Test main page header.
        """
        resp = self.client.get('/', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Presence analyzer', resp.data)

    """
    PRESENCE BY WEEKDAY
    """

    def test_presence_by_weekday_header(self):
        """
        Test presence by weekday header.
        """
        resp = self.client.get('/static/presence_weekday.html')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Presence by weekday', resp.data)

    def test_presence_by_weekday_api_route_parameter_is_correct(self):
        """
        Test presence by weekday api route parameter is correct.
        """
        weekdays = {u'Weekday': u'Presence (s)',
                    u'Mon': 0,
                    u'Tue': 30047,
                    u'Wed': 24465,
                    u'Thu': 23705,
                    u'Fri': 0,
                    u'Sat': 0,
                    u'Sun': 0
                    }

        resp = self.client.get('/api/v1/presence_weekday/10',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        # import ipdb; ipdb.set_trace()
        self.assertDictEqual(weekdays, dict(data))

    def test_presence_by_weekday_api_route_parameter_is_incorrect(self):
        """
        Test presence by weekday api route parameter is incorrect.
        """
        resp = self.client.get('/api/v1/presence_weekday/wrong',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    """
    PRESENCE MEAN TIME
    """

    def test_presence_mean_time_header(self):
        """
        Test presence mean time header.
        """
        resp = self.client.get('/static/mean_time_weekday.html')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Presence mean time by weekday', resp.data)

    def test_presence_mean_time_api_route_parameter_is_correct(self):
        """
        Test presence by weekday api route parameter is correct.
        """
        weekdays = {u'Mon': 0,
                    u'Tue': 30047.0,
                    u'Wed': 24465.0,
                    u'Thu': 23705.0,
                    u'Fri': 0,
                    u'Sat': 0,
                    u'Sun': 0
                    }

        resp = self.client.get('/api/v1/mean_time_weekday/10',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        # import ipdb; ipdb.set_trace()
        self.assertDictEqual(weekdays, dict(data))

    def test_presence_mean_tme_api_route_parameter_is_incorrect(self):
        """
        Test presence by weekday api route parameter is incorrect.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/wrong',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

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
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_by_weekday(self):
        """
        Test Group by weekday.
        """
        self.assertEqual(utils.group_by_weekday({datetime.date(2013, 9, 10): {'start': datetime.time(9, 39, 5), 'end': datetime.time(17, 59, 52)},
                                                 datetime.date(2013, 9, 12): {'start': datetime.time(10, 48, 46), 'end': datetime.time(17, 23, 51)},
                                                 datetime.date(2013, 9, 11): {'start': datetime.time(9, 19, 52), 'end': datetime.time(16, 7, 37)}}),
                         [[], [30047], [24465], [23705], [], [], []])

    def test_seconds_since_midnight(self):
        """
        Test seconds since midnight.
        """
        self.assertEqual(utils.seconds_since_midnight(datetime.time(10, 30, 50)), 37850)

    def test_interval(self):
        """
        Test interval.
        """
        self.assertEqual(utils.interval(datetime.time(10,10,10), datetime.time(10, 30, 50)), 1240)

    def test_mean(self):
        """
        Test mean.
        """
        self.assertEqual(utils.mean([]), 0)

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
