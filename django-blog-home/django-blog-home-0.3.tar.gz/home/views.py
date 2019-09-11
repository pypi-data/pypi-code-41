from django.shortcuts import render
from django.contrib.auth.models import User
from .models import *


def HomeView(request):
    posts = Post.objects.filter()
    return render(request, template_name="home.html", context={"posts":posts})

def PostView(request, slug):
    post = Post.objects.filter(slug=slug).get()
    return render(request, template_name="article.html", context={"post":post})

def AuthorPostsView(request, username):
    author_posts = User.objects.filter(username=username).get().posts.all()
    return render(request, template_name="home.html", context={"posts":author_posts})

def ProfileView(request):
    return render(request, template_name="profile.html", context={"user":request.user}) 