from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if (
            request.method in ['PUT', 'DELETE']
                and not request.user.is_anonymous
            ):
            return (
                request.user == obj.author
                or request.user.is_superuser
                or request.user.is_staff
            )
        return request.method in permissions.SAFE_METHODS
