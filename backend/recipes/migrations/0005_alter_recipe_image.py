# Generated by Django 3.2.5 on 2021-07-17 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes', verbose_name='Изображение'),
        ),
    ]
