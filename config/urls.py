from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from lms.views import CourseViewSet
from users.views import UserProfileViewSet, PaymentViewSet, UserRegistrationViewSet

# Создаем роутер для ViewSet'ов
router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserProfileViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'register', UserRegistrationViewSet, basename='register')  # 👈 Регистрация

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT эндпоинты (доступны без авторизации)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API эндпоинты
    path('api/', include(router.urls)),
    path('api/', include('lms.urls')),
]

# Добавляем URL для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
