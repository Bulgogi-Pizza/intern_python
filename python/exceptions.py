# python/exceptions.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        custom_data = {
            'error': {
                'code': 'TOKEN_NOT_FOUND',
                'message': '토큰이 없습니다.'
            }
        }
        return Response(custom_data, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, InvalidToken):
        custom_data = {
            'error': {
                'code': 'INVALID_TOKEN',
                'message': '토큰이 유효하지 않습니다.'
            }
        }
        if 'expired' in str(exc.detail).lower():
            custom_data['error']['code'] = 'TOKEN_EXPIRED'
            custom_data['error']['message'] = '토큰이 만료되었습니다.'

        return Response(custom_data, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, PermissionDenied):
        custom_data = {
            'error': {
                'code': 'ACCESS_DENIED',
                'message': '관리자 권한이 필요한 요청입니다. 접근 권한이 없습니다.'
            }
        }
        return Response(custom_data, status=status.HTTP_403_FORBIDDEN)

    return response