from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("diagnostic/<int:step_number>/", views.diagnostic_step, name="diagnostic_step"),
    path("diagnostic/redo/", views.redo_diagnostic, name="redo_diagnostic"),
    path("routine/", views.routine_result, name="routine_result"),
    path("products/", views.product_catalog, name="product_catalog"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("routine/save/", views.save_routine, name="save_routine"),
    path("account/signup/", views.signup, name="signup"),
    path(
        "account/login/",
        auth_views.LoginView.as_view(template_name="routines/login.html"),
        name="login",
    ),
    path("account/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("account/routines/", views.my_routines, name="my_routines"),
    path("account/routines/<int:pk>/", views.routine_detail, name="routine_detail"),
]
