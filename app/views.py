from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Question, Profile, Tag, Like, Answer

top_users = Profile.objects.get_top_users()
popular_tags = Tag.get_popular_tags()


def paginate(objects, page_num, per_page=15):
    paginator = Paginator(objects, per_page)

    return paginator.page(page_num)


def index(request):
    page_name = f'Вопросы'
    page = request.GET.get('page', 1)
    paginated_questions = Question.paginate_questions(Question.objects.new_questions(), page)
    return render(request, 'index.html', {'page_name': page_name, 'questions': paginated_questions,
                                          'top_users': top_users, 'popular_tags': popular_tags})


def tag_page(request, tag_name):
    page_name = f'Вопросы по тегу {tag_name}'
    # Получаем объект тега по имени
    tag = Tag.objects.get(name=tag_name)
    # Получаем вопросы с этим тегом
    questions_with_tag = Question.objects.filter(tags=tag)
    page = request.GET.get('page', 1)
    paginated_questions = Question.paginate_questions(questions_with_tag, page)
    return render(request, 'index.html', {'page_name': page_name, 'top_users': top_users,
                                          'popular_tags': popular_tags, 'questions': paginated_questions})


def hottest(request):
    page_name = f'Самое популярное'
    page = request.GET.get('page', 1)
    hot_questions = Question.objects.best_questions()
    paginated_questions = Question.paginate_questions(hot_questions, page)
    return render(request, 'index.html', {'page_name': page_name, 'questions': paginated_questions,
                                          'top_users': top_users, 'popular_tags': popular_tags})


def question(request, question_id):
    item = Question.objects.get(id=question_id)
    page = request.GET.get('page', 1)
    paginated_answer = Question.paginate_questions(item.answer_set.all(), page, 5)
    return render(request, 'question.html', {'question': item, 'answers': paginated_answer,
                                             'top_users': top_users, 'popular_tags': popular_tags})


def ask(request):
    return render(request, 'ask.html', {'top_users': top_users, 'popular_tags': popular_tags})


def login(request):
    return render(request, 'login.html', {'top_users': top_users, 'popular_tags': popular_tags})


def signup(request):
    return render(request, 'signup.html', {'top_users': top_users, 'popular_tags': popular_tags})


def settings(request):
    return render(request, 'settings.html', {'top_users': top_users, 'popular_tags': popular_tags})
