from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Импортируем ViewSet'ы
from lms.views import CourseViewSet
from users.views import UserProfileViewSet

# Создаем роутер для ViewSet'ов
router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserProfileViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # Маршруты для ViewSet'ов
    path('api/', include('lms.urls')),   # Маршруты для Generic-классов уроков
]

# Добавляем URL для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
