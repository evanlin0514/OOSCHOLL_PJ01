from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("login/", views.user_login, name="login"),
    path("signup/", views.user_signup, name="signup"),
    path("logout/", views.user_logout, name="logout"),
    path("add-to-watchlist/<int:stock_id>/", views.add_to_watchlist, name="add_to_watchlist"),
    path('remove-from-watchlist/<int:watchlist_id>/<int:stock_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path("create-watchlist/", views.create_watchlist, name="create_watchlist"),
    path("remove-watchlist/<int:watchlist_id>/", views.remove_watchlist, name="remove_watchlist"),
]