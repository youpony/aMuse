from django.test import TestCase, Client
from muse.rest import models


class SimpleTest(TestCase):
    fixtures = ['tour.json']

    def setUp(self):
        self.client = Client()
        self.tour = models.Tour.objects.all()[0]
        self.posts = self.tour.post_set.all()

    @staticmethod
    def _serialize_post(list_of_post):
        key = '&post[]='
        list_of_id = [str(post.id) for post in list_of_post]
        return key[1:] + key.join(list_of_id)

    def test_sort_post(self):
        # reorder with a lost post.
        serial_rappr = self._serialize_post(self.posts[1:])
        data = {
            'order': serial_rappr,
            'tour_private_id': str(self.tour.private_id)
        }
        response = self.client.post('/storyteller/sort_post/', data)
        self.assertEqual(response.status_code, 400)

        # reorder correct
        temp_posts = self.posts
        comment = temp_posts[0].text
        serial_rappr = self._serialize_post(temp_posts.reverse())
        data = {
            'order': serial_rappr,
            'tour_private_id': str(self.tour.private_id)
        }
        response = self.client.post('/storyteller/sort_post/', data)
        self.assertEqual(response.status_code, 200)

        reorder_posts = self.tour.post_set.all()
        for i, post in enumerate(reorder_posts):
            if i != post.ordering_index:
                self.fail('reordering fail')

        self.assertEqual(comment, reorder_posts.latest('ordering_index').text)

        # missing private_id
        serial_rappr = self._serialize_post(temp_posts)
        data = {
            'order': serial_rappr,
        }
        response = self.client.post('/storyteller/sort_post/', data)
        self.assertEqual(response.status_code, 400)

        # missing order
        serial_rappr = self._serialize_post(temp_posts)
        data = {
            'tour_private_id': str(self.tour.private_id)
        }
        response = self.client.post('/storyteller/sort_post/', data)
        self.assertEqual(response.status_code, 400)

        # wrong private_id, differen number of item
        tour = models.Tour.objects.all()[1]
        data = {
            'order': serial_rappr,
            'tour_private_id': str(tour.private_id)
        }
        response = self.client.post('/storyteller/sort_post/', data)
        self.assertIn(response.status_code, (400, 404))

        # wrong private_id, same number of item
        tour = models.Tour.objects.all()[2]
        data = {
            'order': serial_rappr,
            'tour_private_id': str(tour.private_id)
        }
        response = self.client.post('/storyteller/sort_post/', data)
        self.assertEqual(response.status_code, 404)

        # id modified by user
        temp_posts = self.posts
        temp_posts[0].id = 13
        serial_rappr = self._serialize_post(temp_posts)
        data = {
            'order': serial_rappr,
            'tour_private_id': str(self.tour.private_id)
        }
        response = self.client.post('/storyteller/sort_post/', data)
        self.assertEqual(response.status_code, 404)
