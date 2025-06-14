from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSignupSerializer, UserLoginSerializer, UserProfileSerializer
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User
from rest_framework.permissions import IsAdminUser


class SignupView(APIView):
  def post(self, request):
    if User.objects.filter(username=request.data.get('username')).exists():
      return Response({
        "error": {
          "code": "USER_ALREADY_EXISTS",
          "message": "이미 가입된 사용자입니다."
        }
      }, status=status.HTTP_409_CONFLICT)

    # 중복이 아닐 경우, 기존의 시리얼라이저 로직을 그대로 수행합니다.
    serializer = UserSignupSerializer(data=request.data)

    if serializer.is_valid():
      try:
        user = serializer.save()
        response_data = {
          "username": user.username,
          "nickname": user.nickname,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

      except IntegrityError:
        return Response({
          "error": {
            "code": "USER_ALREADY_EXISTS",
            "message": "이미 가입된 사용자이거나 닉네임이 중복됩니다."
          }
        }, status=status.HTTP_409_CONFLICT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
  def post(self, request):
    serializer = UserLoginSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return Response({
      "token": access_token
    }, status=status.HTTP_200_OK)

class ProfileView(APIView):
  # permission_classes에 IsAuthenticated를 추가하여,
  # 인증된 사용자만 이 View에 접근할 수 있도록 설정합니다.
  permission_classes = [IsAuthenticated]

  def get(self, request):
    # IsAuthenticated 권한을 통과하면, request.user에 인증된 사용자 객체가 담겨있습니다.
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

class AdminRoleGrantView(APIView):
  # 이 View에 접근하기 위해서는 관리자(is_staff=True) 권한이 필요합니다.
  permission_classes = [IsAdminUser]

  def patch(self, request, user_id):
    try:
      # 권한을 변경할 대상 사용자를 찾습니다.
      target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
      # 사용자가 존재하지 않을 경우 404 에러를 반환합니다.
      return Response({"message": "해당 ID의 사용자를 찾을 수 없습니다."},
                      status=status.HTTP_404_NOT_FOUND)

    # 대상 사용자의 is_staff 필드를 True로 변경하여 관리자 권한을 부여합니다.
    target_user.is_staff = True
    target_user.save()

    # 변경된 사용자 정보를 응답으로 보냅니다.
    serializer = UserProfileSerializer(target_user)
    return Response(serializer.data, status=status.HTTP_200_OK)
