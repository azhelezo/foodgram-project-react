from django.urls import path
from django.urls.conf import include
from rest_framework.routers import SimpleRouter

from api.views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                       TagViewSet)

router = SimpleRouter()
router.register("users", CustomUserViewSet)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
