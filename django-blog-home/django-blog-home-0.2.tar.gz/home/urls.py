""" Modules... """
from django.urls import path
from .views import (
    HomeView,
    ProfileView,
    PostView,
    AuthorPostsView
) 

urlpatterns = [
    path('', HomeView),
    path('security/profile/', ProfileView),
    path('article/<str:slug>', PostView),
    path('author/<str:username>', AuthorPostsView),
    
]