from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='test_description',
        )
        cls.user = User.objects.create(username='TestUser')
        cls.post = Post.objects.create(
            group=PostsURLTests.group,
            author=PostsURLTests.user,
            text='Тестовый текст',
        )

    def test_urls_correct_anonymous_and_authorized(self):
        authorized_client = Client()
        authorized_client.force_login(PostsURLTests.user)
        authorized_user_not_author = Client()
        user_not_author = User.objects.create(username='TestUser_2')
        authorized_user_not_author.force_login(user_not_author)

        group_slug = PostsURLTests.group.slug
        post_id = PostsURLTests.post.id
        username = PostsURLTests.user

        urls_status_code = (
            (self.client, ''),
            (self.client, f'/group/{group_slug}/'),
            (self.client, f'/{username}/'),
            (self.client, f'/{username}/{post_id}/'),
            (authorized_client, '/new/'),
            (authorized_client, f'/{username}/{post_id}/edit/'),
        )

        for client, url in urls_status_code:
            with self.subTest(client=client, url=url,):
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_checking_whether_direct_links_match(self):
        authorized_client = Client()
        authorized_client.force_login(PostsURLTests.user)

        group_slug = PostsURLTests.group.slug
        post_id = PostsURLTests.post.id
        username = PostsURLTests.user

        urls_reverse_name = (
            ('index', None, '/'),
            ('posts_group', (group_slug,), f'/group/{group_slug}/',),
            ('new_post', None, '/new/'),
            ('profile', (username,), f'/{username}/'),
            ('post', (username, post_id), f'/{username}/{post_id}/'),
            ('post_edit', (username, post_id), f'/{username}/{post_id}/edit/'),
            ('follow_index', None, '/follow/'),
            ('profile_follow', (username,), f'/{username}/follow/'),
            ('profile_unfollow', (username,), f'/{username}/unfollow/'),
            ('add_comment', (username, post_id),
             f'/{username}/{post_id}/comment/'),
            ('page_not_found', None, '/404/'),
            ('server_error', None, '/500/'),
        )

        for reverse_name, args, url in urls_reverse_name:
            with self.subTest(reverse_name=reverse_name,
                              args=args,
                              url=url):
                reverse_name = reverse(reverse_name, args=args)
                self.assertEqual(reverse_name, url)

    def test_urls_anonymous_redirect(self):
        post_id = PostsURLTests.post.id
        username = PostsURLTests.user
        login = reverse('login')
        new_post = reverse('new_post')
        post_edit = reverse('post_edit', args=(username, post_id))
        profile_follow = reverse('profile_follow', args=(username,))
        profile_unfollow = reverse('profile_unfollow', args=(username,))
        add_comment = reverse('add_comment', args=(username, post_id))
        url_login = {
            new_post: f'{login}?next={new_post}',
            post_edit: f'{login}?next={post_edit}',
            profile_follow: f'{login}?next={profile_follow}',
            profile_unfollow: f'{login}?next={profile_unfollow}',
            add_comment: f'{login}?next={add_comment}',
        }
        for url, url_redirect in url_login.items():
            with self.subTest():
                response = self.client.get(url, follow=True)
                self.assertRedirects(response, url_redirect)

    def test_edit_post_for_authorized_user_not_the_author(self):
        not_author_client = Client()
        not_author = User.objects.create(username='TestUser_2')
        not_author_client.force_login(not_author)

        post_id = PostsURLTests.post.id
        username = PostsURLTests.user
        response = not_author_client.get(
            reverse('post_edit', args=(username, post_id)), follow=True
        )
        expectation = reverse('post', args=(username, post_id))
        self.assertRedirects(response, expectation)

    def test_page_not_found(self):
        response = self.client.get('/not-found/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
