from django.test import TestCase
from django.urls import reverse


class AboutViewTests(TestCase):

    def test_about_pages_guest_client_correct_template(self):
        templates_page_names = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech',
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.client.get(reverse(reverse_name))
                self.assertTemplateUsed(response, template)
