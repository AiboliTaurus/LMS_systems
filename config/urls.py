from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from lms.views import CourseViewSet
from users.views import UserProfileViewSet, PaymentViewSet

# Создаем роутер для ViewSet'ов
router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserProfileViewSet)
router.register(r'payments', PaymentViewSet)  # Добавляем маршруты для платежей

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('lms.urls')),
]

# Добавляем URL для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
