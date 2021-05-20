from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
        )
        cls.post = Post.objects.create(
            author=PostModelTest.user,
            text="Тестовый текст",
            group=cls.group,
        )

    def test_object_name_is_title_filds_and_text_filds(self):
        object_names = (
            (PostModelTest.post, PostModelTest.post.text[:15]),
            (PostModelTest.group, PostModelTest.group.title)
        )
        for key, value in object_names:
            with self.subTest(key=key, value=value):
                self.assertEqual(str(key), value)
