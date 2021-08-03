from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<str:listingid>", views.listing, name="listing"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
]
