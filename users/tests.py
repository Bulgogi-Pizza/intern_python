# users/tests.py

import pytest
from django.urls import reverse
from rest_framework import status
from .models import User
import json

@pytest.mark.django_db
class TestUserSignup:
  def test_signup_success(self, client):
    # given: 회원가입에 필요한 데이터
    url = reverse('signup')
    data = {
      'username': 'testuser',
      'password': 'testpassword123',
      'nickname': 'testnick'
    }

    # when: /signup API에 POST 요청
    response = client.post(url, data=json.dumps(data),
                           content_type='application/json')

    # then: 성공적으로 생성되었는지 확인
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['username'] == 'testuser'
    assert User.objects.filter(username='testuser').exists()

  def test_signup_fail_duplicate_username(self, client):
    # given: 먼저 사용자를 하나 생성
    User.objects.create_user(username='testuser', password='password',
                             nickname='nick')

    url = reverse('signup')
    data = {
      'username': 'testuser',  # 중복된 이름
      'password': 'testpassword123',
      'nickname': 'new_nick'
    }

    # when: 중복된 이름으로 다시 POST 요청
    response = client.post(url, data=json.dumps(data),
                           content_type='application/json')

    # then: 409 Conflict 에러가 발생하는지 확인
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()['error']['code'] == 'USER_ALREADY_EXISTS'


@pytest.mark.django_db
class TestUserLogin:
  @pytest.fixture
  def test_user(self):
    # 로그인을 테스트하기 위한 사전 사용자 생성
    return User.objects.create_user(username='testuser',
                                    password='testpassword123',
                                    nickname='testnick')

  def test_login_success(self, client, test_user):
    # given
    url = reverse('login')
    data = {
      'username': 'testuser',
      'password': 'testpassword123'
    }

    # when
    response = client.post(url, data=json.dumps(data),
                           content_type='application/json')

    # then
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.json()

  def test_login_fail_wrong_password(self, client, test_user):
    # given
    url = reverse('login')
    data = {
      'username': 'testuser',
      'password': 'wrongpassword'
    }

    # when
    response = client.post(url, data=json.dumps(data),
                           content_type='application/json')

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['error']['code'] == 'INVALID_CREDENTIALS'


@pytest.mark.django_db
class TestAdminRoleGrant:
  @pytest.fixture
  def admin_user(self):
    # 관리자 사용자 생성
    return User.objects.create_superuser(username='admin', password='password',
                                         nickname='admin_nick')

  @pytest.fixture
  def normal_user(self):
    # 일반 사용자 생성
    return User.objects.create_user(username='user', password='password',
                                    nickname='user_nick')

  def get_token(self, client, username, password):
    # 테스트에 필요한 토큰을 발급받는 헬퍼 함수
    url = reverse('login')
    data = {'username': username, 'password': password}
    response = client.post(url, data=json.dumps(data),
                           content_type='application/json')
    return response.json()['token']

  def test_grant_role_success(self, client, admin_user, normal_user):
    # given: 관리자 토큰과 대상 사용자의 ID
    admin_token = self.get_token(client, 'admin', 'password')
    url = reverse('admin-role-grant', kwargs={'user_id': normal_user.id})

    # when: 관리자 토큰으로 권한 부여 요청
    response = client.patch(
        url,
        HTTP_AUTHORIZATION=f'Bearer {admin_token}',
        content_type='application/json'
    )

    # then: 성공적으로 역할이 변경되었는지 확인
    assert response.status_code == status.HTTP_200_OK
    normal_user.refresh_from_db()  # DB에서 최신 정보를 다시 불러옴
    assert normal_user.is_staff is True

  def test_grant_role_fail_not_admin(self, client, normal_user):
    # given: 일반 사용자 토큰
    normal_user_token = self.get_token(client, 'user', 'password')
    # 자기 자신에게 권한 부여를 시도
    url = reverse('admin-role-grant', kwargs={'user_id': normal_user.id})

    # when: 일반 사용자 토큰으로 권한 부여 요청
    response = client.patch(
        url,
        HTTP_AUTHORIZATION=f'Bearer {normal_user_token}',
        content_type='application/json'
    )

    # then: 403 Forbidden 에러가 발생하는지 확인
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()['error']['code'] == 'ACCESS_DENIED'