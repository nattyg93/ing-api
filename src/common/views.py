"""Views common to the whole project."""


class AuthorisedQuerySetMixin:
    """Limits querysets to those permitted for the requesting user."""

    def get_queryset(self):
        """Limit for the request user."""
        queryset = super().get_queryset()
        assert hasattr(
            queryset, "for_user"
        ), f"{self.__class__.__name__}'s queryset should have a `for_user` method."
        return queryset.for_user(self.request.user)
