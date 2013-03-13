from django.test import TestCase, Client

import simplejson as json
from muse.rest import models


class TestExhibitions(TestCase):
    fixtures = ['item.json']

    def setUp(self):
        self.client = Client()

        # a sampled exhibition (XXX. use earliest, when relased)
        self.exhibition = models.Exhibition.objects.latest('pk')
        self.item = models.Item.objects.latest('pk')

    def test_exhibitions_publiclist(self):
        response = self.client.get('/api/m/')
        self.assertEqual(response.status_code, 200)
        exhibitions = json.loads(response.content).get('data')
        self.assertGreater(len(exhibitions), 1)

        e = exhibitions[0]
        for key in 'title', 'description':
            self.assertIn(key, e)

        self.assertIn(self.exhibition.title,
                      [e['title'] for e in exhibitions])

    def test_exhibition_details(self):
        response = self.client.get('/api/m/123456789/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/api/m/\'\0\x86/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/api/m/{}/'.format(self.echibition.pk))
        details = json.loads(reponse.content)
        for key in 'museum', 'title', 'description', 'image':
            self.assertIn(key, details)

    def test_exhibition_items(self):
        # XXX. provide new fixtures
        self.item.exhibitions.add(self.exhibition)

        response = self.client.get('/api/m/44444222222222222222/o/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/api/m/{}/o/'.format(self.exhibition.pk))
        self.assertEqual(response.status_code, 200)
        items = json.loads(response.content).get('data')
        self.assertGreater(len(items), 0)
        self.assertEqual(items[0]['name'], self.item.name)


class TestItem(TestCase):
    fixtures = ['item.json']

    def setUp(self):
        self.client = Client()
        self.item = models.Item.objects.latest('pk')

    def test_item_details(self):
        response = self.client.get('/api/o/34723084723985629/')
        self.assertEqual(response.status_code, 404)

        item = models.Item(name='a mock item', desc='foo',
                           author='Foo', year=2013)
        item.save()
        response = self.client.get('/api/o/{}/'.format(item.pk))
        self.assertEqual(response.status_code, 200)
        exhibitions = json.loads(response.content).get('exhibitions')
        self.assertEqual(len(exhibitions), 0)


        response = self.client.get('/api/o/{}/'.format(self.item.pk))
        self.assertEqual(response.status_code, 200)
        item = json.loads(response.content)
        self.assertTrue(all(key in models.Item._meta_fields)
                            for key in item.keys())
