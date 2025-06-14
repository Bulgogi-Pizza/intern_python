# Django JWT 인증/인가 프로젝트

## 📖 프로젝트 개요
이 프로젝트는 Python의 웹 프레임워크인 Django와 Django REST Framework를 사용하여 JWT(Json Web Token) 기반의 사용자 인증 및 인가 시스템을 구현하는 과제입니다. 사용자는 회원가입과 로그인을 할 수 있으며, 발급된 JWT를 통해 보호된 API에 접근할 수 있습니다. 또한, 역할(is_staff) 기반의 접근 제어를 적용하여 관리자만 접근할 수 있는 API를 구현했습니다.

모든 기능은 Pytest를 통해 테스트되었으며, API 명세는 drf-spectacular(Swagger)를 통해 문서화되었습니다. 최종적으로 완성된 애플리케이션은 AWS EC2에 Gunicorn과 Nginx를 사용하여 배포되었습니다.

## ✨ 주요 기능
- **사용자 인증**
  - 사용자 회원가입 (`/signup`)
  - 사용자 로그인 및 JWT 발급 (`/login`)
- **JWT 기반 인가**
  - JWT 토큰 검증을 통한 API 접근 제어
  - 인증된 사용자 정보 조회 (`/profile`)
- **역할 기반 접근 제어 (RBAC)**
  - `is_staff` 필드를 이용한 관리자와 일반 사용자 구분
  - 관리자 전용 API에 대한 접근 제한
- **커스텀 예외 처리**
  - DRF의 전역 예외 처리기를 커스터마이징하여 일관된 에러 응답 형식 제공
- **API 문서화**
  - `drf-spectacular`(Swagger)를 이용한 API 명세 자동화 및 UI 제공

## ⚙️ 사용 기술
- **Backend**: Python, Django, Django REST Framework
- **Security & JWT**: djangorestframework-simplejwt
- **Database**: SQLite3 (기본 설정)
- **Testing**: Pytest, pytest-django
- **API Docs**: drf-spectacular (Swagger UI)
- **Deployment**: AWS EC2, Gunicorn, Nginx
- **Build Tool**: Pip, venv
- **Utilities**: Lombok (Java 프로젝트 해당) -> Python에서는 별도 라이브러리 미사용

## 🚀 API 명세
- **Swagger UI 주소**: `http://13.203.155.208/swagger/`
- **API Base URL**: `http://13.203.155.208`

---

### 👤 User API

#### 1. 회원가입
- **Endpoint**: `POST /signup`
- **Description**: 새로운 사용자를 시스템에 등록합니다.
- **Request Body**:
  ```
  {
    "username": "newuser",
    "password": "password1234",
    "nickname": "mynickname"
  }
  ```

- **Success Response (201 CREATED)**:
  ```
  { 
    "username": "newuser",
    "nickname": "mynickname"
  }
  ```

- **Failure Response (409 Conflict)**:

  ```
  {
    "error": {
      "code": "USER_ALREADY_EXISTS",
      "message": "이미 가입된 사용자입니다."
    }
  }
  ```

#### 2. 로그인
- **Endpoint**: `POST /login`
- **Description**: 사용자 인증 후 JWT를 발급합니다.
- **Request Body**:
  ```
  {
    "username": "newuser",
    "password": "password1234"
  }
  ```
- **Success Response (200 OK)**:
  ```
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2..."
  }
  ```

- **Failure Response (400 Bad Request)**:
  ```
  {
    "error": {
      "code": "INVALID_CREDENTIALS",
      "message": "아이디 또는 비밀번호가 올바르지 않습니다."
    }
  }
  ```


#### 3. 프로필 조회
- **Endpoint**: `GET /profile`
- **Description**: 현재 로그인된 사용자의 프로필 정보를 조회합니다. (JWT 인증 필요)
- **Success Response (200 OK)**:
  ```
  {
    "username": "newuser",
    "nickname": "mynickname"
  }
  ```

- **Failure Response (401 Unauthorized)**:
  ```
  {
    "error": {
      "code": "TOKEN_NOT_FOUND",
      "message": "토큰이 없습니다."
    }
  }
  ```

---

### 🛠️ Admin API
> **[필독]** 아래 API는 **관리자(is_staff=True)** 역할의 사용자만 호출할 수 있습니다.

#### 1. 관리자 권한 부여
- **Endpoint**: `PATCH /api/admin/users/{user_id}/roles`
- **Description**: 특정 사용자에게 관리자 권한을 부여합니다. (JWT 인증 필요)
- **Path Variable**:
- `user_id` (Long): 권한을 부여할 사용자의 ID
- **Success Response (200 OK)**:
  ```
  {
    "username": "someuser",
    "nickname": "somenickname"
  }
  ```

- **Failure Responses**:
- **403 Forbidden** (접근 권한 없음):
  ```
  {
    "error": {
      "code": "ACCESS_DENIED",
      "message": "관리자 권한이 필요한 요청입니다. 접근 권한이 없습니다."
    }
  }
  ```
- **404 Not Found** (존재하지 않는 사용자):
  ```
  {
    "message": "해당 ID의 사용자를 찾을 수 없습니다."
  }
  ```

## ❗ 주요 에러 코드
| Error Code             | HTTP Status        | Description                            |
| ---------------------- | ------------------ | -------------------------------------- |
| `USER_ALREADY_EXISTS`  | 409 Conflict       | 회원가입 시 이미 존재하는 사용자 이름/닉네임일 경우 |
| `INVALID_CREDENTIALS`  | 400 Bad Request    | 로그인 시 아이디 또는 비밀번호가 틀렸을 경우 |
| `TOKEN_NOT_FOUND`      | 401 Unauthorized   | Authorization 헤더에 토큰이 없는 경우        |
| `INVALID_TOKEN`        | 401 Unauthorized   | JWT 토큰이 유효하지 않을 경우              |
| `TOKEN_EXPIRED`        | 401 Unauthorized   | JWT 토큰이 만료되었을 경우                 |
| `ACCESS_DENIED`        | 403 Forbidden      | 해당 API에 접근할 권한이 없는 경우         |


## 🏃‍ 로컬 실행 방법

### 1. 사전 요구사항
- Python 3.9+
- pip

### 2. 설정 및 실행
프로젝트 루트 디렉토리에서 아래 명령어들을 순서대로 실행합니다.
1. 파이썬 가상환경 생성 및 활성화
```
python -m venv venv
source venv/bin/activate # macOS/Linux

venv\Scripts\activate # Windows
```
2. 의존성 라이브러리 설치
`pip install -r requirements.txt`

3. 데이터베이스 마이그레이션
`python manage.py migrate`

4. 개발 서버 실행
`python manage.py runserver`

애플리케이션은 기본적으로 `8000` 포트에서 실행됩니다.


## ☁️ 배포
- **플랫폼**: AWS EC2
- **서버 스택**: Nginx (Web Server) + Gunicorn (Application Server)
- Nginx를 리버스 프록시로 사용하여 외부의 80번 포트 요청을 내부의 8000번 포트에서 실행 중인 Gunicorn으로 전달하는 방식으로 구성되었습니다.

