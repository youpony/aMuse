# pylint: disable=R0904

import datetime
from itertools import cycle
from mock import patch, ANY
from os.path import join, dirname

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
import simplejson as json

from muse.rest import models


class TestModels(TestCase):
    fixtures = ['item.json']

    def test_csrng_key(self):
        self.assertNotEqual(models.csrng_key(), models.csrng_key())
## test also with private_id key

    def test_item_save(self):
        item = models.Item.objects.latest('pk')

        invalid_dates = ['foo-bar', '1968-foo', 'a1-1', '0x10-0x100',
                         '', '111_1', '1-1a']
        for invalid_date in invalid_dates:
            item.year = invalid_date
            try:
                item.save()
            except ValidationError:
                continue
            else:
                self.fail('ValidationError: {}'.format(invalid_date))

        valid_dates = ['1-1', '2013-2015', '1992']
        for valid_date in valid_dates:
            item.year = valid_date
            try:
                item.save()
            except ValidationError:
                self.fail('cannot save date {}'.format(valid_date))

    def test_exhibition_save(self):
        exhibition = models.Exhibition.objects.latest('pk')

        exhibition.start_date = datetime.datetime.now()
        exhibition.end_date = datetime.datetime.now()
        try:
            exhibition.save()
        except ValidationError:
            self.fail('saving exhibition.start_date == exhibition.end_date')

        exhibition.start_date = datetime.datetime.now()
        exhibition.end_date = datetime.datetime.now()-datetime.timedelta(days=1)
        self.assertRaises(ValidationError, exhibition.save)



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

    def test_exhibition_items_sentiment(self):
        """
        Assert sentiment analysis properly search and recognizes tweets.
        """
        from pattern.web import Result

        def mock_search(name, cached=0, count=False):
            results = []
            for text in ['I love #ponies',
                         'I am really #happy',
                         '#life is good'] * 10:
                result = Result('')
                result.text = text
                results.append(result)
            return results

        self.item.exhibitions.add(self.exhibition)
        items = models.Item.objects.filter(
            exhibitions__pk__contains=self.exhibition.pk
        )
        for item, city in zip(items, cycle(('rome', 'london', 'paris'))):
            item.city = city
            item.save()

        with patch('muse.rest.views.twengine', search=mock_search):
            response = self.client.get('/api/m/{}/o/'.format(self.exhibition.pk))

        self.assertEqual(response.status_code, 200)
        items = json.loads(response.content).get('data')
        for item in items:
            self.assertGreater(item['sentiment'], 0.5)


class TestStory(TestCase):
    fixtures = ['item.json']

    def setUp(self):
        self.client = Client()

    @patch('muse.rest.models.send_mail')
    def test_story_sendmail(self, mock_send_mail):
        e = models.Exhibition.objects.get(pk=6)
        story = {
            'name': 'test test',
            'email': 'test@example.com',
            'exhibition': e.pk,
            'posts': json.dumps(
                [{'item_pk': i.pk}
                 for i in e.item_set.all()[:20:2]]),
        }
        response = self.client.post('/api/s/', story)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'completed'})

        m = models.Museum.objects.latest('pk')
        mock_send_mail.assert_called_with(
            ANY, ANY, m.referral, [story['email']])

    @patch('muse.rest.models.send_mail')
    def test_story_posts(self, mock_send_mail):
        e = models.Exhibition.objects.get(pk=6)
        story = {
            'name': 'test test',
            'exhibition': e.pk,
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

    def test_story_get(self):
        story = models.Tour.objects.latest('public_id')

        response = self.client.get('/api/s/lalalal/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/s/lalalal/', {'edit':'lalalala'})
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/api/s/{}/'.format(story.public_id), {'edit':'false'})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertIn('posts', response)
        self.assertIn('name', response)


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
