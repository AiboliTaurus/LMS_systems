from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from lms.views import CourseViewSet, SubscriptionAPIView
from users.views import UserProfileViewSet, PaymentViewSet, UserRegistrationViewSet

# Схема для Swagger документации
schema_view = get_schema_view(
    openapi.Info(
        title="LMS API Documentation",
        default_version='v1',
        description="""Документация API для LMS системы

## Возможности API:
- Управление курсами и уроками
- Регистрация и авторизация пользователей
- JWT аутентификация
- Подписка на обновления курсов
- Оплата курсов через Stripe
- Фильтрация, поиск и пагинация

## Тестовые карты Stripe для оплаты:
- **Visa**: 4242 4242 4242 4242
- **Mastercard**: 5555 5555 5555 4444
- **American Express**: 3782 8224 6310 005
- **Discover**: 6011 1111 1111 1117

## Для тестовой оплаты используйте любой из этих номеров,
срок действия (любая будущая дата) и CVV/CVC (любые 3 цифры).
""",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@lms.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Роутер
router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserProfileViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'register', UserRegistrationViewSet, basename='register')

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Swagger документация
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # JWT эндпоинты
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API эндпоинты
    path('api/', include(router.urls)),
    path('api/', include('lms.urls')),

    # Подписка
    path('api/subscribe/', SubscriptionAPIView.as_view(), name='subscription'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
