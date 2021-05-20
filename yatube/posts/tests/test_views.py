import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User, Follow
from ..forms import PostForm, CommentForm


class PostViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b\x01\x00\x00'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='test_description',
        )
        cls.user = User.objects.create(username='TestUser')
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.post = Post.objects.create(
            group=PostViewsTests.group,
            author=PostViewsTests.user,
            text='Тестовый текст',
            image=cls.uploaded,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostViewsTests.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        authorized_client = Client()
        authorized_client.force_login(PostViewsTests.user)
        group_slug = PostViewsTests.group.slug
        post_id = PostViewsTests.post.id
        username = PostViewsTests.user

        urls_reverse_name = (
            ('index', None, 'posts/index.html'),
            ('posts_group', (group_slug,), 'posts/group.html',),
            ('new_post', None, 'posts/new_post.html'),
            ('profile', (username,), 'posts/profile.html'),
            ('post', (username, post_id), 'posts/post.html'),
            ('post_edit', (username, post_id), 'posts/new_post.html'),
            ('follow_index', None, 'posts/follow.html'),
            ('page_not_found', None, 'misc/404.html'),
        )

        for reverse_name, args, url in urls_reverse_name:
            with self.subTest(reverse_name=reverse_name,
                              args=args,
                              url=url):
                reverse_name = self.authorized_client.get(
                    reverse(reverse_name, args=args))
                self.assertTemplateUsed(reverse_name, url)

    def context_test_expectat(self, context_page, is_post):
        if is_post:
            self.assertIn('post', context_page.context)
            post_page = context_page.context['post']
        else:
            self.assertIn('page', context_page.context)
            post_page = context_page.context.get('page')[0]

        self.assertEqual(post_page.text, PostViewsTests.post.text)
        self.assertEqual(post_page.author, PostViewsTests.user)
        self.assertEqual(post_page.group, PostViewsTests.group)
        self.assertEqual(post_page.pub_date, self.post.pub_date)

    def test_index_page_show_correct_context(self):
        response = self.client.get(reverse('index'))
        self.context_test_expectat(response, is_post=False)

    def test_posts_group_shows_new_post(self):
        group_slug = PostViewsTests.group.slug
        response = self.authorized_client.get(
            reverse('posts_group', args=(group_slug,))
        )
        self.assertIn('group', response.context)
        group = response.context['group']
        self.assertEqual(group.title, PostViewsTests.group.title)
        self.assertEqual(group.description, PostViewsTests.group.description)
        self.context_test_expectat(response, is_post=False)

    def test_profile_page_show_correct_context(self):
        username = PostViewsTests.user
        response = self.authorized_client.get(
            reverse('profile', args=(username,))
        )
        self.assertIn('author', response.context)
        author = response.context['author']
        self.assertEqual(author, PostViewsTests.post.author)
        self.assertIn('following', response.context)
        self.context_test_expectat(response, is_post=False)

    def test_post_view_page_show_correct_context(self):
        post_id = PostViewsTests.post.id
        username = PostViewsTests.user
        response = self.authorized_client.get(
            reverse('post', args=(username, post_id))
        )
        self.assertIn('author', response.context)
        author = response.context['author']
        self.assertEqual(author, PostViewsTests.post.author)
        self.assertIn('form', response.context)
        comment_form = response.context['form']
        self.assertIsInstance(comment_form, CommentForm)
        self.assertIn('comments', response.context)
        self.assertIn('following', response.context)
        self.context_test_expectat(response, is_post=True)

    def test_post_edit_page_show_correct_context(self):
        post_id = PostViewsTests.post.id
        username = PostViewsTests.user
        response = self.authorized_client.get(
            reverse('post_edit', args=(username, post_id))
        )
        self.assertIn('form', response.context)
        post_form = response.context['form']
        self.assertIsInstance(post_form, PostForm)
        self.assertIn('edit', response.context)
        self.assertIs(response.context['edit'], True)
        self.context_test_expectat(response, is_post=True)

    def test_new_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertIn('form', response.context)
        post_form = response.context['form']
        self.assertIsInstance(post_form, PostForm)
        self.assertIn('edit', response.context)
        self.assertIs(response.context['edit'], False)

    def test_new_post_does_not_appear_on_another_group_page(self):
        group_second = Group.objects.create(
            title='Тестовый заголовок второй группы',
            slug='group-second',
            description='Description',
        )
        group_slug = group_second.slug
        response = self.authorized_client.get(
            reverse('posts_group', args=(group_slug,))
        )
        response_context = response.context['page'].object_list.count()
        self.assertEqual(response_context, 0)

    def test_index_cache(self):
        cache = 'Тест кэша'
        PostViewsTests.post.text = cache
        PostViewsTests.post.save()
        response = self.client.get(reverse('index'))
        page = response.context.get('page')[0]
        self.assertEqual(page.text, cache)
        PostViewsTests.post.text = 'Тестовый текст'
        PostViewsTests.post.save()
        self.assertEqual(page.text, cache)

    def test_authorized_user_can_subscribe_other_users(self):
        before = Follow.objects.count()
        username = PostViewsTests.user
        response = reverse('profile_follow', args=(username,))
        self.authorized_client_author.get(response)
        after = Follow.objects.count()
        self.assertEqual(after, before + 1)

    def user_can_unsubscribe_from_others(self):
        username = PostViewsTests.user
        response = reverse('profile_follow', args=(username,))
        self.authorized_client_author.get(response)
        before = Follow.objects.count()
        response = reverse('profile_follow', args=(username,))
        self.authorized_client_author.get(response)
        after = Follow.objects.count()
        self.assertEqual(after, before - 1)

    def test_show_follow_posts(self):
        username = PostViewsTests.user
        response = reverse('profile_follow', args=(username,))
        self.authorized_client_author.get(response)
        response = self.authorized_client_author.get(reverse('follow_index'))
        response_two = self.authorized_client.get(reverse('follow_index'))
        self.assertFalse(response_two.context['page'])
        self.assertNotEqual(response.content, response_two.content)
