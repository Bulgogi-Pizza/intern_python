from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class UserSignupSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['username', 'password', 'nickname']

    extra_kwargs = {'password': {'write_only': True}}

  def create(self, validated_data):
    user = User.objects.create_user(
        username=validated_data['username'],
        password=validated_data['password'],
        nickname=validated_data['nickname']
    )
    return user

class UserLoginSerializer(serializers.Serializer):
  username = serializers.CharField(required=True)
  password = serializers.CharField(required=True, write_only=True)

  def validate(self, data):
    user = authenticate(username=data['username'], password=data['password'])

    if user is None:
      raise serializers.ValidationError({
        "error": {
          "code": "INVALID_CREDENTIALS",
          "message": "아이디 또는 비밀번호가 올바르지 않습니다."
        }
      })

    return user

class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    # 응답에 포함될 필드를 지정합니다.
    fields = ['username', 'nickname']
