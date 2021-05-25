import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

dir_temp = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=dir_temp)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='test_description',
        )
        cls.user = User.objects.create(username='TestUser')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(dir_temp, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b\x01\x00\x00'
        )
        uploaded = SimpleUploadedFile(
            name='small_test_create.gif',
            content=small_gif,
            content_type='image/gif'
        )
        text_test = 'Тестовый текст'
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': text_test,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), count + 1)
        post = Post.objects.first()
        self.assertEqual(post.group, PostCreateFormTests.group)
        self.assertEqual(post.author, PostCreateFormTests.user)
        self.assertEqual(post.text, text_test)
        self.assertEqual(post.image, f'posts/{uploaded.name}')

    def test_post_edit_existing_post(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b\x01\x00\x00'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b\x01\x00\x00'
        )
        uploaded = SimpleUploadedFile(
            name='small_test_edit.gif',
            content=small_gif,
            content_type='image/gif'
        )
        text_test = 'Тестовый текст'
        post = Post.objects.create(
            text=text_test,
            author=PostCreateFormTests.user,
            group=PostCreateFormTests.group,
        )
        group_second = Group.objects.create(
            title='Тестовый заголовок второй группы',
            slug='test_slug_second',
        )
        edit_text = 'Измененый тестовый текст'
        form_data = {
            'text': edit_text,
            'group': group_second.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=(PostCreateFormTests.user, post.id)),
            data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse('post', args=(PostCreateFormTests.user, post.id))
        )
        post = Post.objects.get(id=post.id)
        self.assertEqual(post.group, group_second)
        self.assertEqual(post.author, PostCreateFormTests.user)
        self.assertEqual(post.text, edit_text)
        self.assertEqual(post.image, f'posts/{uploaded.name}')

    def test_guest_client_cannot_create_a_new_post(self):
        count = Post.objects.count()
        new_text = 'Новый текст'
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': new_text,
        }
        response = self.client.post(
            reverse('new_post'), data=form_data, follow=False
        )
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('new_post'))
        self.assertEqual(Post.objects.count(), count)

    def test_not_author_post_edit(self):
        not_author = User.objects.create(username='NotAuthor')
        not_author_client = Client()
        not_author_client.force_login(not_author)
        text_test = 'Тестовый текст'
        post = Post.objects.create(
            text=text_test,
            author=PostCreateFormTests.user,
            group=PostCreateFormTests.group,
        )
        new_group = Group.objects.create(
            title='Новый тестовый заголовок',
            slug='new_slug',
            description='new_description',
        )
        count = Post.objects.count()
        new_text = 'Новый текст'
        form_data_test = {
            'text': new_text,
            'group': new_group.id
        }
        response = not_author_client.post(
            reverse('post_edit', args=(PostCreateFormTests.user, post.id)),
            data=form_data_test, follow=False
        )
        self.assertRedirects(
            response, reverse('post', args=(PostCreateFormTests.user, post.id))
        )
        self.assertEqual(Post.objects.count(), count)
        post = Post.objects.get(id=post.id)
        self.assertNotEqual(post.group, new_group)
        self.assertEqual(post.author, PostCreateFormTests.user)
        self.assertNotEqual(post.text, new_text)


class CommentCreateFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('TestAuthor')
        cls.user = User.objects.create_user('TestUser')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Пост №1'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentCreateFormTest.user)

    def test_authorized_client_create_comment(self):
        username = CommentCreateFormTest.author
        post_id = CommentCreateFormTest.post.id
        count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('add_comment', args=(username, post_id)),
            data=form_data, follow=True
        )
        self.assertRedirects(response, reverse('post', args=(username,
                                                             post_id)))
        self.assertEqual(Comment.objects.count(), count + 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.post, CommentCreateFormTest.post)
        self.assertEqual(comment.author, CommentCreateFormTest.user)
        self.assertEqual(comment.text, form_data['text'])

    def test_guest_client_cannot_create_comment(self):
        username = CommentCreateFormTest.author
        post_id = CommentCreateFormTest.post.id
        count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        self.client.post(
            reverse('add_comment', args=(username, post_id)),
            data=form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), count)
