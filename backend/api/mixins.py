from rest_framework import mixins, viewsets

from .permissions import IsAdminOrReadOnlyPermission


class ListRetriveCreateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Миксины для пользователей."""

    pass


class ListRetriveCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Миксины для тегов и ингредиентов."""

    permission_classes = (IsAdminOrReadOnlyPermission,)
    pagination_class = None
