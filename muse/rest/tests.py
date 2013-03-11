"""
"""

from django.test import TestCase, Client

import simplejson as json
from muse.rest import models


class TestExhibitions(TestCase):
    fixtures = ['item.json']

    def setUp(self):
        self.client = Client()

    def test_exhibitions_publiclist(self):
        response = self.client.get('/api/m')
        self.assertEqual(response.status_code, 200)
        exhibitions = json.loads(response.content).get('data')
        self.assertGreater(len(exhibitions), 1)

        e = exhibitions[0]
        for key in 'title', 'description':
            self.assertIn(key, e)

