from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("diagnostic/<int:step_number>/", views.diagnostic_step, name="diagnostic_step"),
    path("diagnostic/redo/", views.redo_diagnostic, name="redo_diagnostic"),
    path("routine/", views.routine_result, name="routine_result"),
    path("products/", views.product_catalog, name="product_catalog"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
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
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart_view, name="remove_from_cart"),
    path("cart/add-routine/", views.add_routine_to_cart, name="add_routine_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("checkout/webhook/", views.stripe_webhook, name="stripe_webhook"),
]
