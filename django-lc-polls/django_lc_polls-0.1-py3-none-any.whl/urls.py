from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.index, name='index'),
    #example : /polls/5
    path('<int:question_id>/', views.detail, name='detail'),
    #example : /polls/5/results
    path('<int:question_id>/results', views.results, name='results'),
    #example : /polls/5/votes
    path('<int:question_id>/votes', views.vote, name='votes'),
]   