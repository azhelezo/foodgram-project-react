from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import FavoriteRecipe, IngredientAmount, ShoppingRecipe, Tag, Recipe, Ingredient
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from users.models import FollowUser

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'id', 'password', )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'id', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        return obj.pk in self.context.get('following', [])


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(read_only=True, source='ingredient.measurement_unit')
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientAmount
        fields = ('amount', 'name', 'measurement_unit', 'id')


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(ingredients, many=True).data

    def get_author(self, obj):
        return CustomUserSerializer(instance=obj.author).data

    def get_is_favorited(self, obj):
        following = self.context.get('following', [])
        return obj.id in following

    def get_is_in_shopping_cart(self, obj):
        shopping = self.context.get('shopping', [])
        return obj.id in shopping


class RecipeCreateUpdateSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    ingredients = IngredientAmountSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def save(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().save()
        IngredientAmount.objects.filter(recipe=instance).delete()
        for ing in ingredients:
            amount = ing['amount']
            ingredient = Ingredient.objects.get(id=ing['ingredient']['id'])
            obj, created = IngredientAmount.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient,
                defaults={'amount': amount}
            )
        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=['user', 'recipe']
            )
        ]


class RecipeShortSerializer(RecipeSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FollowUser
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=FollowUser.objects.all(),
                fields=['user', 'author']
            )
        ]


class FollowUserSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'id', 'is_subscribed', 'recipes')

    def get_recipes(self, obj):
        author_recipes = obj.recipes.all()[:self.context.get('recipes_limit', 2)]
        return RecipeShortSerializer(author_recipes, many=True).data


class ShoppingRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingRecipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingRecipe.objects.all(),
                fields=['user', 'recipe']
            )
        ]
