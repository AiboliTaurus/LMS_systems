from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModerator(BasePermission):
    """
    Права доступа для модераторов
    Проверяет, входит ли пользователь в группу 'moderators'
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """
    Права доступа для владельца объекта
    Проверяет, является ли пользователь владельцем объекта
    Универсально работает с:
    - Моделями, у которых есть поле 'owner' (Course, Lesson)
    - Моделью User (сравнение по id)
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Если у объекта есть поле 'owner' (Course, Lesson и др.)
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        # Если объект является моделью User (сравниваем id)
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id

        return False


class IsOwnerOrModerator(BasePermission):
    """
    Права доступа: владелец ИЛИ модератор
    """

    def has_object_permission(self, request, view, obj):
        # Модератор имеет полный доступ
        if IsModerator().has_permission(request, view):
            return True

        # Владелец имеет доступ к своему объекту
        if not request.user or not request.user.is_authenticated:
            return False

        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id

        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Права доступа: владелец может всё, остальные только читают
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем
        if request.method in SAFE_METHODS:
            return True

        # Для остальных методов проверяем владельца
        if not request.user or not request.user.is_authenticated:
            return False

        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id

        return False
