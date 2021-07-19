from django.contrib import admin
from recipes.models import Ingredient, IngredientAmount, Tag, Recipe, FavoriteRecipe, ShoppingRecipe


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    search_fields = ('ingredient',)
    list_display = ('ingredient', 'recipe', 'amount')
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'favorited')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = (IngredientAmountInline,)

    def favorited(self, obj):
        return obj.following_recipe.count()


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user', )
    search_fields = ('id', 'recipe', 'user', )
    list_filter = ('id', 'recipe', 'user', )
    empty_value_display = '-пусто-'


class ShoppingRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user', )
    search_fields = ('id', 'recipe', 'user', )
    list_filter = ('id', 'recipe', 'user', )
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingRecipe, ShoppingRecipeAdmin)
