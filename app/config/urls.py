from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # swagger-ui
    path('api/v1/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/schema/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # applications
    path("admin", admin.site.urls),
    path("api/v1/alerts", include("alerts.urls")),
    path("api/v1/bookmarks", include("bookmarks.urls")),
    path("api/v1/comments", include("comments.urls")),
    path("api/v1/fridges", include("fridges.urls")),
    path("api/v1/ingredients", include("ingredients.urls")),
    path("api/v1/likes", include("likes.urls")),
    path("api/v1/main", include("main.urls")),
    path("api/v1/recipes", include("recipes.urls")),
    path("api/v1/users", include("users.urls")),
    path("api/v1/collabo", include("collabo.urls"))
]