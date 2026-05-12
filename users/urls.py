from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("list/", views.UserListView.as_view(), name="user_list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("edit-profile/", views.UserEditView.as_view(), name="user_edit"),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
]
