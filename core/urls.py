"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Simple health check view
def health_check(request):
    return JsonResponse({"status": "ok"})
    
    # Collect system information for debugging
    # debug_info = {
    #     "status": "ok",
    #     "message": "Service is running",
    #     "django_version": django.get_version(),
    #     "python_version": sys.version,
    #     "environment": {
    #         "DJANGO_SETTINGS_MODULE": os.environ.get("DJANGO_SETTINGS_MODULE", "Not set"),
    #         "DATABASE_URL_SET": os.environ.get("DATABASE_URL") is not None,
    #         "MYSQL_VARS_SET": any(os.environ.get(var) for var in ["MYSQLHOST", "MYSQL_HOST"]),
    #     },
    #     "request_meta": {
    #         "HTTP_HOST": request.META.get("HTTP_HOST", "Not available"),
    #         "REMOTE_ADDR": request.META.get("REMOTE_ADDR", "Not available"),
    #     }
    # }
    
    return JsonResponse(debug_info)

# Schema configuration for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Community API",
        default_version='v1',
        description="API for community groups and posts",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Health check endpoint for Railway
    path('health-check', health_check, name='health_check'),
    
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('community.urls')),
    
    # API documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
