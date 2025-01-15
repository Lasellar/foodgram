from rest_framework.permissions import BasePermission


class IsAuthenticatedAndAuthor(BasePermission):
    """
    Класс для ограничения доступа.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
