# Generated by Django 3.2.5 on 2021-07-15 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20210711_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='media/recipes', verbose_name='Изображение'),
        ),
    ]