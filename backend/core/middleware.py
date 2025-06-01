# core/middleware.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken)


class DisableCSRFForAPI(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)


class ClearInvalidTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, (InvalidToken, AuthenticationFailed)):
            response = JsonResponse({"detail": "Token is invalid or expired"},
                                    status=401)
            response.delete_cookie('access_token')  # Удаляем куку с токеном
            return response
        return None
