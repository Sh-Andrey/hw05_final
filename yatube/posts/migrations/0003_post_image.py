# Generated by Django 2.2.6 on 2021-05-17 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20210511_0706'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Выберите изображение', null=True, upload_to='posts/', verbose_name='Изображение'),
        ),
    ]
