from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Question, Profile, Tag, Like, Answer


top_users = Profile.objects.get_top_users()
popular_tags = Tag.get_popular_tags()


def paginate(objects, page_num, per_page=15):
    paginator = Paginator(objects, per_page)

    return paginator.page(page_num)


def index(request):
    page = request.GET.get('page', 1)
    paginated_questions = Question.paginate_questions(Question.objects.sort_questions(), page)
    return render(request, 'index.html', {'questions': paginated_questions, 'top_users': top_users, 'popular_tags': popular_tags})


def question(request, question_id):
    item = Question.objects.get(id=question_id)
    page = request.GET.get('page', 1)
    paginated_answer = Question.paginate_questions(item.answer_set.all(), page, 5)
    return render(request, 'question.html', {'question': item, 'answers': paginated_answer, 'top_users': top_users})


def ask(request):
    return render(request, 'ask.html', {'top_users': top_users})


def login(request):
    return render(request, 'login.html', {'top_users': top_users})


def signup(request):
    return render(request, 'signup.html', {'top_users': top_users})


def settings(request):
    return render(request, 'settings.html', {'top_users': top_users})
