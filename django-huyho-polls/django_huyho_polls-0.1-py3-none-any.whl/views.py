from django.shortcuts import render, HttpResponse, get_list_or_404
from .models import Question
# Create your views here.
def index(request):
    # return HttpResponse('Hi there! Welcome to my page! You\'re not find any page better!')
    name = 'Huy Ho'
    myFavorite = ['Abc', 'Xyz', 'Hihi', 'Haha']
    package = {'name': name, 'favorite': myFavorite}
    return render(request, "polls/index.html", package)

def question_list(request):
    # list_ = Question.objects.all()
    list_ = get_list_or_404(Question)
    package = {'list': list_}
    return render(request, 'polls/question_list.html', package)

def detail(request, question_id):
    o = Question.objects.get(id = question_id)
    return render(request, 'polls/detail_question.html', {'obj': o})

def vote(request, question_id):
    try:
        question = Question.objects.get(id = question_id)
        data = request.POST['choice']
    except:
        return HttpResponse('Empty choice error!')
    choice = question.choice_set.get(id = data)
    choice.votes += 1
    choice.save()
    return render(request, 'polls/result.html', {'question': question})