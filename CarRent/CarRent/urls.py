"""CarRental URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts import views as accounts_views
from cars import views as cars_views
from bookings import views as bookings_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Car Rental REST API",
      default_version='v1',
      description="Documentation on Car Rental REST API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'cars', cars_views.CarViewSet)
router.register(r'car-photos', cars_views.CarPhotoViewSet)
router.register(r'users', 
                accounts_views.UserViewSet, 
                basename='users')
router.register(r'bookings', bookings_views.BookingViewSet, basename='bookings')



urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include(router.urls)),
    
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', accounts_views.LogoutView.as_view(), name='logout'),
    path('logout-all/', accounts_views.LogoutAllView.as_view(), name='logout-all'),

    path('swagger-doc/', 
        schema_view.with_ui('swagger', cache_timeout=0), 
        name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', 
        cache_timeout=0), 
        name='schema-redoc'),

    path('api-auth/', include('rest_framework.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)