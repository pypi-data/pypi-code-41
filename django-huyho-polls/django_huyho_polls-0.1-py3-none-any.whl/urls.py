from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    # ex: /polls/detail/5/
    path('detail/<int:question_id>/', views.detail, name = 'detail'),
    #: /polls/list
    path('list/', views.question_list, name = 'question_list'),
    path('', views.index, name = 'index'),
    path('<int:question_id>/', views.vote, name = 'vote'),
]