from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PaginatorViewsTest(TestCase):

    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
        )
        cls.user = User.objects.create(username='TestUser')
        cls.NUMBER_OF_POSTS = 3
        posts = [
            Post(
                group=cls.group,
                author=cls.user,
                text=f'Тестовый текст {i}',
            )for i in range(
                settings.NUMBER_OF_RECORDS_ON_THE_PAGINATOR_PAGE
                + cls.NUMBER_OF_POSTS)
        ]
        Post.objects.bulk_create(posts)

    def test_number_of_posts_on_the_first_page(self):
        """Проверка: количество постов на первой странице равно константе."""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list),
                         settings.NUMBER_OF_RECORDS_ON_THE_PAGINATOR_PAGE
                         )

    def test_second_page_containse_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list),
                         PaginatorViewsTest.NUMBER_OF_POSTS)
