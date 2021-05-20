from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutURLTests(TestCase):

    def test_about_public_url_exists_at_desired_location(self):
        urls = {
            '/about/author/': 'about:author',
            '/about/tech/': 'about:tech',
        }

        for url, reverse_name in urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(url, reverse(reverse_name))
