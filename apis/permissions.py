# apis/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed

class HasAutToken(BasePermission):
    def has_permission(self, request, view):
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            raise AuthenticationFailed(detail="Your request has no user auth. token", code=401)
        return True