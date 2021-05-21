from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=200)
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True)
    description = models.TextField(
        verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True)
    text = models.TextField(
        verbose_name='Текст')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='posts',
        on_delete=models.CASCADE)
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        related_name='posts',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Выберите изображение',
        verbose_name='Изображение')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',)
    text = models.TextField(
        max_length=200,
        verbose_name='Текст комментария',
        help_text='Напишите комментарий!')
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')
