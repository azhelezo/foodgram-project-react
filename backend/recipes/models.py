from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):

    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='amounts', verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='ingredient_amounts', verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количества ингредиентов'
    
    def __str__(self):
        return self.ingredient.name


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    color = ColorField(default='#888888', verbose_name='Цвет в HEX')
    slug = models.CharField(max_length=200, verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='recipes', verbose_name='Автор', null=True
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(verbose_name='Изображение', upload_to='recipes')
    text = models.TextField('Описание', max_length=1000)
    ingredients = models.ManyToManyField(
        Ingredient, through=IngredientAmount, related_name='recipes', verbose_name='Список ингредиентов'
    )
    tags = models.ManyToManyField(Tag, related_name='recipes', verbose_name='Тэги')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления', validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_recipe")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="following_recipe")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='favorite_unique'
            )
        ]
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'

    def __str__(self):
        return f'{self.user} follows recipe {self.recipe}'


class ShoppingRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shopper_recipe")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="shopping_recipe")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='shopping_unique'
            )
        ]
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self):
        return f'{self.user} shopping for recipe {self.recipe}'
