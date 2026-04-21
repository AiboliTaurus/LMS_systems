from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModerator(BasePermission):
    """
    Права доступа для модераторов
    Проверяет, входит ли пользователь в группу 'moderators'
    """
    def has_permission(self, request, view):
        # Если пользователь не авторизован - доступ запрещён
        if not request.user or not request.user.is_authenticated:
            return False
        # Проверяем, состоит ли пользователь в группе модераторов
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """
    Права доступа для владельца объекта
    Проверяет, является ли пользователь владельцем объекта
    """
    def has_object_permission(self, request, view, obj):
        # Если пользователь не авторизован - доступ запрещён
        if not request.user or not request.user.is_authenticated:
            return False
        # Проверяем, является ли пользователь владельцем
        # У объектов Course и Lesson есть поле 'owner'
        return obj.owner == request.user


class IsOwnerOrModerator(BasePermission):
    """
    Права доступа: владелец ИЛИ модератор
    """
    def has_object_permission(self, request, view, obj):
        # Модератор имеет полный доступ
        if IsModerator().has_permission(request, view):
            return True
        # Владелец имеет доступ к своему объекту
        return obj.owner == request.user


class IsOwnerOrReadOnly(BasePermission):
    """
    Права доступа: владелец может всё, остальные только читают
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем
        if request.method in SAFE_METHODS:
            return True
        # Для остальных методов проверяем, является ли пользователь владельцем
        return obj.owner == request.user
