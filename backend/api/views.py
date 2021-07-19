from django.http.response import HttpResponse
from rest_framework.decorators import action
from django.db.models import Value as V
from django.db.models import Sum
from django.db.models.functions import StrIndex
from django.db.models.functions.text import Lower
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from api.permissions import IsAdminOrAuthorOrReadOnly
from recipes.models import FavoriteRecipe, ShoppingRecipe, Tag, Recipe, Ingredient
from api.serializers import (CustomUserSerializer, FavoriteRecipeSerializer, FollowUserCreateSerializer,
                             FollowUserSerializer, RecipeShortSerializer, RecipeSerializer, ShoppingRecipeSerializer,
                             TagSerializer, IngredientSerializer, RecipeCreateUpdateSerializer)
from djoser.views import UserViewSet
from users.models import FollowUser, User


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    subscriptions_serializer_class = FollowUserSerializer
    queryset = User.objects.all().order_by('id')
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['retrieve', 'subscriptions']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'subscriptions':
            return self.subscriptions_serializer_class
        return super().get_serializer_class(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {}
        if request.user.is_authenticated:
            context = {'following': request.user.follower.all().values_list('pk', flat=True)}
        serializer = self.get_serializer(instance, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        context = {}
        if request.user.is_authenticated:
            context = {'following': request.user.follower.all().values_list('pk', flat=True)}
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(users, many=True, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False)
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        recipes_limit = int(request.query_params.get('recipes_limit', 3))
        context = {'recipes_limit': recipes_limit}
        following = self.get_queryset().filter(following__in=user.follower.all())
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(following, many=True, context=context)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'delete'])
    def subscribe(self, request, *args, **kwargs):
        if self.request.method == 'GET':
            return self.follow_add_relation(request, *args, **kwargs)
        return self.follow_delete(request, *args, **kwargs)

    def follow_add_relation(self, request, *args, **kwargs):
        author = self.get_object()
        data = {'user': request.user.pk, 'author': author.pk}
        serializer = FollowUserCreateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = FollowUserSerializer(self.get_object()).data
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def follow_delete(self, request, *args, **kwargs):
        author = self.get_object()
        data = {'user': request.user.pk, 'author': author.pk}
        follow = FollowUser.objects.filter(**data).first()
        if not follow:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(follow)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    create_update_seializer = RecipeCreateUpdateSerializer

    shopping_recipe_serializer = ShoppingRecipeSerializer
    shopping_recipe_queryset = ShoppingRecipe.objects.all()

    favorite_recipe_serializer = FavoriteRecipeSerializer
    favorite_recipe_queryset = FavoriteRecipe.objects.all()

    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['create', 'shopping_cart', 'favorite', 'download_shopping_cart']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'delete']:
            return [IsAdminOrAuthorOrReadOnly()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST']:
            return self.create_update_seializer
        elif self.request.method in ['GET']:
            if self.action == 'shopping_cart':
                return self.shopping_recipe_serializer
            elif self.action == 'favorite':
                return self.favorite_recipe_serializer
        return self.serializer_class

    def get_relation_queryset(self):
        if self.request.method in ['DELETE']:
            if self.action == 'shopping_cart':
                return self.shopping_recipe_queryset
            elif self.action == 'favorite':
                return self.favorite_recipe_queryset
        return super().get_queryset()

    @action(detail=True, methods=['get', 'delete'])
    def shopping_cart(self, request, *args, **kwargs):
        if self.request.method == 'GET':
            return self.add_relation(request, *args, **kwargs)
        return self.remove_relation(request, *args, **kwargs)

    @action(detail=True, methods=['get', 'delete'])
    def favorite(self, request, *args, **kwargs):
        if self.request.method == 'GET':
            return self.add_relation(request, *args, **kwargs)
        return self.remove_relation(request, *args, **kwargs)

    def add_relation(self, request, *args, **kwargs):
        recipe = self.get_object()
        data = {'user': request.user.pk, 'recipe': recipe.pk}
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = RecipeShortSerializer(self.get_object()).data
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def remove_relation(self, request, *args, **kwargs):
        recipe = self.get_object()
        data = {'user': request.user.pk, 'recipe': recipe.pk}
        shopping = self.get_relation_queryset().filter(**data).first()
        if not shopping:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(shopping)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients = Recipe.objects.filter(
            shopping_recipe__user=2
        ).order_by('ingredients__name').values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(total_amount=Sum('ingredient_amounts__amount'))

        file_data = ""

        for item in ingredients:
            name = item.get('ingredients__name').capitalize()
            amount = item.get('total_amount')
            unit = item.get('ingredients__measurement_unit')
            line = f'{name} - {amount} {unit}'
            file_data += line + '\n'

        response = HttpResponse(
            file_data, content_type='text/plain'
        )
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        return response

    def list(self, request, *args, **kwargs):
        recipes = self.filter_queryset(self.get_queryset())
        following, shopping = [], []
        if request.user.is_authenticated:
            following = list(self.request.user.follower_recipe.values_list('recipe', flat=True))
            shopping = list(self.request.user.shopper_recipe.values_list('recipe', flat=True))
        context = {'following': following, 'shopping': shopping}

        page = self.paginate_queryset(recipes)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recipes, many=True, context=context)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        params = self.request.query_params
        author_id = params.get('author', None)
        tags = params.getlist('tags', None)
        is_favorited = bool(params.get('is_favorited', 0))
        is_in_shopping_cart = bool(params.get('is_in_shopping_cart', 0))

        if author_id is not None:
            queryset = queryset.filter(author__id=author_id)

        if tags is not None:
            query = Q()
            [query.add(Q(tags__slug=tag), Q.OR) for tag in tags]
            queryset = queryset.filter(query)

        if is_favorited is True:
            favorited = list(self.request.user.follower_recipe.values_list('recipe', flat=True))
            queryset = queryset.filter(id__in=favorited)

        if is_in_shopping_cart is True:
            shopping_cart = list(self.request.user.shopper_recipe.values_list('recipe', flat=True))
            queryset = queryset.filter(id__in=shopping_cart)

        return super().filter_queryset(queryset)

    def create(self, request, *args, **kwargs):
        data = request.data
        data.update({'author': request.user.pk, 'text': self.request.build_absolute_uri()})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(serializer.validated_data)

        data = self.serializer_class(instance).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    def update(self, request, **kwargs):
        instance = get_object_or_404(Recipe, pk=kwargs.get('id'))
        data = request.data
        data.update({'author': request.user.pk})
        serializer = self.get_serializer(instance=instance, data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(serializer.validated_data)

        data = self.serializer_class(self.get_object()).data
        return Response(data=data, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = []
    lookup_field = 'id'
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        lookup = self.request.query_params.get('name')
        if lookup is not None:
            queryset = queryset.filter(name__icontains=lookup)
            queryset = queryset.annotate(name_lookup=Lower('name'))
            queryset = queryset.annotate(name_pos=StrIndex('name_lookup', V(lookup)))
            queryset = queryset.order_by('name_pos')
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = []
    lookup_field = 'slug'
    pagination_class = None
    permission_classes = [AllowAny, ]
