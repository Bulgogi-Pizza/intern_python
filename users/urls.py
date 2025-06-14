from django.urls import path
from .views import SignupView, LoginView, ProfileView, AdminRoleGrantView

urlpatterns = [
  path('signup', SignupView.as_view(), name='signup'),
  path('login', LoginView.as_view(), name='login'),
  path('profile', ProfileView.as_view(), name='profile'),
  path('api/admin/users/<int:user_id>/roles', AdminRoleGrantView.as_view(),
       name='admin-role-grant'),
]