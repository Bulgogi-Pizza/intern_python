from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSignupSerializer, UserLoginSerializer, \
  UserProfileSerializer

from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes


class SignupView(APIView):
  @extend_schema(
      tags=["User API"],
      summary="회원가입",
      description="새로운 사용자를 등록합니다.",
      request=UserSignupSerializer,
      responses={
        201: UserProfileSerializer,
        409: OpenApiTypes.OBJECT,
      },
      examples=[
        OpenApiExample(
            '성공 예시',
            summary='회원가입 성공',
            description='회원가입 성공 시, 생성된 사용자의 정보를 반환합니다.',
            value={'username': 'newuser', 'nickname': 'newnickname'},
            response_only=True,
            status_codes=[201]
        ),
        OpenApiExample(
            '실패 예시 (중복된 사용자)',
            summary='중복된 사용자 에러',
            description='이미 가입된 사용자 이름이나 닉네임으로 가입 시도 시 발생하는 에러입니다.',
            value={'error': {'code': 'USER_ALREADY_EXISTS',
                             'message': '이미 가입된 사용자입니다.'}},
            response_only=True,
            status_codes=[409]
        )
      ]
  )
  def post(self, request):
    if User.objects.filter(username=request.data.get('username')).exists():
      return Response({
        "error": {"code": "USER_ALREADY_EXISTS", "message": "이미 가입된 사용자입니다."}
      }, status=status.HTTP_409_CONFLICT)

    serializer = UserSignupSerializer(data=request.data)

    if serializer.is_valid():
      try:
        user = serializer.save()
        response_serializer = UserProfileSerializer(user)
        return Response(response_serializer.data,
                        status=status.HTTP_201_CREATED)
      except IntegrityError:
        return Response({
          "error": {"code": "USER_ALREADY_EXISTS", "message": "닉네임이 중복됩니다."}
        }, status=status.HTTP_409_CONFLICT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
  @extend_schema(
      tags=["User API"],
      summary="로그인",
      description="사용자 로그인을 하고 JWT를 발급합니다.",
      request=UserLoginSerializer,
      responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
      },
      examples=[
        OpenApiExample(
            '성공 예시',
            summary='로그인 성공',
            value={
              'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjox...'},
            response_only=True,
            status_codes=[200]
        ),
        OpenApiExample(
            '실패 예시',
            summary='로그인 실패',
            value={'error': {'code': 'INVALID_CREDENTIALS',
                             'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}},
            response_only=True,
            status_codes=[400]
        )
      ]
  )
  def post(self, request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return Response({"token": access_token}, status=status.HTTP_200_OK)


class ProfileView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
      tags=["User API"],
      summary="프로필 조회",
      description="인증된 사용자의 프로필 정보(username, nickname)를 조회합니다. **(JWT 인증 필요)**",
      responses={200: UserProfileSerializer}
  )
  def get(self, request):
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class AdminRoleGrantView(APIView):
  permission_classes = [IsAdminUser]

  @extend_schema(
      tags=["Admin API"],
      summary="관리자 권한 부여",
      description="관리자가 특정 사용자에게 관리자 권한(is_staff=True)을 부여합니다. **(관리자 JWT 인증 필요)**",
      responses={
        200: UserProfileSerializer,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
      },
      examples=[
        OpenApiExample(
            '권한 부여 성공 (200)',
            value={'username': 'targetuser', 'nickname': 'targetnick'},
            response_only=True, status_codes=[200]
        ),
        OpenApiExample(
            '접근 거부 (403)',
            value={'error': {'code': 'ACCESS_DENIED',
                             'message': '관리자 권한이 필요한 요청입니다. 접근 권한이 없습니다.'}},
            response_only=True, status_codes=[403]
        ),
        OpenApiExample(
            '사용자 없음 (404)',
            value={'message': '해당 ID의 사용자를 찾을 수 없습니다.'},
            response_only=True, status_codes=[404]
        )
      ]
  )
  def patch(self, request, user_id):
    try:
      target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
      return Response({"message": "해당 ID의 사용자를 찾을 수 없습니다."},
                      status=status.HTTP_404_NOT_FOUND)

    target_user.is_staff = True
    target_user.save()

    serializer = UserProfileSerializer(target_user)
    return Response(serializer.data, status=status.HTTP_200_OK)