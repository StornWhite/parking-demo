from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins


class NoCreateModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    """
    A Modelview that allows read, update and destroy but does not allow
    create.
    """
    pass
