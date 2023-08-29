from rest_framework import permissions


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    """Права для работы с ингредиентами и тегами."""

    def has_permission(self, request, _):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdminOrAuthorOrReadOnlyPermission(permissions.BasePermission):
    """Права для работы с рецептами."""

    def has_permission(self, request, _):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, _, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or obj.author == request.user
        )
