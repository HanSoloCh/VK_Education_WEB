from django.shortcuts import render
from django.core.paginator import Paginator


# Create your views here.

QUESTIONS = [
    {
        'id': i,
        'title': f'question {i}',
        'content': f'blablablablabla {i}',
    } for i in range(30)
]


def paginate(objects, page_num, per_page=15):
    paginator = Paginator(objects, per_page)

    return paginator.page(page_num)


def index(request):
    page_num = request.GET.get('page', 1)
    return render(request, 'index.html', {'questions': paginate(QUESTIONS, page_num)})


def question(request, question_id):
    item = QUESTIONS[question_id]
    return render(request, 'question.html', {'question': item})


def ask(request):
    return render(request, 'ask.html')


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def settings(request):
    return render(request, 'settings.html')
