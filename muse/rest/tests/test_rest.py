# pylint: disable=R0904

import datetime
from mock import patch, ANY
from os.path import join, dirname

from django.test import TestCase, Client
import simplejson as json

from muse.rest import models


class TestModels(TestCase):
    def test_csrng_key(self):
        self.assertNotEqual(models.csrng_key(), models.csrng_key())
## test also with private_id key


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
        self.assertEqual(
            models.Exhibition.objects.filter(
                end_date__gte=datetime.date.today()
            ).count(),
            len(exhibitions)
        )

        e = exhibitions[0]
        for key in 'title', 'description':
            self.assertIn(key, e)

        self.assertIn(self.exhibition.title,
                      [e['title'] for e in exhibitions])

    def test_exhibition_details(self):
        response = self.client.get('/api/m/123456789/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/api/m/{}/'.format(self.exhibition.pk))
        details = json.loads(response.content)
        for key in 'museum', 'title', 'description', 'image', 'video':
            self.assertIn(key, details)

        response = self.client.get(r'/api/m/\'\0\x86/')
        self.assertEqual(response.status_code, 404)

    def test_exhibition_items(self):
        self.item.exhibitions.add(self.exhibition)

        response = self.client.get('/api/m/44444222222222222222/o/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/api/m/{}/o/'.format(self.exhibition.pk))
        self.assertEqual(response.status_code, 200)
        items = json.loads(response.content).get('data')
        self.assertGreater(len(items), 0)
        self.assertEqual(items[0]['name'], self.item.name)
        self.assertEqual(len(items[0]['images']),
                         self.item.itemimage_set.count())


class TestStory(TestCase):
    fixtures = ['item.json']

    def setUp(self):
        self.client = Client()

    @patch('muse.rest.models.send_mail')
    def test_story_sendmail(self, mock_send_mail):
        story = {
            'fullname': 'test test',
            'email': 'test@example.com',
            'posts': json.dumps(
                [{'item_pk': i.pk}
                 for i in models.Item.objects.all()[:20:2]]),
        }
        response = self.client.post('/api/s/', story)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'completed'})

        m = models.Museum.objects.latest('pk')
        mock_send_mail.assert_called_with(
            ANY, ANY, m.referral, [story['email']])

    def test_story_posts(self):
        story = {
            'fullname': 'test test',
            'email': 'test@example.com',
        }

        # a story without any post is invalid.
        response = self.client.post('/api/s/', story)
        self.assertEqual(response.status_code, 400)
        story['posts'] = json.dumps([])
        response = self.client.post('/api/s/', story)
        self.assertEqual(response.status_code, 400)

        # a story containing a post without any item or image is invalid.
        story['posts'] = json.dumps([{}])
        response = self.client.post('/api/s/', story)
        self.assertEqual(response.status_code, 400)

        # a valid story should have a completed status
        item_pk, item_pk1 = models.Item.objects.all()[:2].values_list(
            'pk',
            flat=True,
        )
        with open(join(dirname(__file__), 'image64')) as f:
            image = f.read()
        story['posts'] = json.dumps([
                {'item_pk': item_pk, 'image': image},
                {'item_pk': item_pk1},
                { 'image': image},
        ])
        response = self.client.post('/api/s/', story)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'completed'})


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
        exhibitions = json.loads(
            response.content
        ).get('data').get('exhibitions')
        self.assertEqual(len(exhibitions), 0)

        response = self.client.get('/api/o/{}/'.format(self.item.pk))
        self.assertEqual(response.status_code, 200)
        item = json.loads(response.content)
        self.assertTrue(
            all(key in models.Item._meta_fields) for key in item.keys()
        )
