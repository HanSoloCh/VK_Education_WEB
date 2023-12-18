from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect

from .forms import ProfileEditorForm, LoginForm, RegisterForm, QuestionForm, AnswerForm
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
    return render(request, 'index.html', {'page_name': page_name,
                                          'questions': paginated_questions,
                                          'top_users': top_users,
                                          'popular_tags': popular_tags})


def tag_page(request, tag_name):
    page_name = f'Вопросы по тегу {tag_name}'
    # Получаем объект тега по имени
    tag = Tag.objects.get(name=tag_name)
    # Получаем вопросы с этим тегом
    questions_with_tag = Question.objects.filter(tags=tag)
    page = request.GET.get('page', 1)
    paginated_questions = Question.paginate_questions(questions_with_tag, page)
    return render(request, 'index.html', {'page_name': page_name,
                                          'top_users': top_users,
                                          'popular_tags': popular_tags,
                                          'questions': paginated_questions})


def hottest(request):
    page_name = f'Самое популярное'
    page = request.GET.get('page', 1)
    hot_questions = Question.objects.best_questions()
    paginated_questions = Question.paginate_questions(hot_questions, page)
    return render(request, 'index.html', {'page_name': page_name,
                                          'questions': paginated_questions,
                                          'top_users': top_users,
                                          'popular_tags': popular_tags})


def question(request, question_id):
    item = Question.objects.get(id=question_id)
    page = request.GET.get('page', 1)
    paginated_answer = Question.paginate_questions(item.answer_set.all(), page, 5)

    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer_item = answer_form.save(commit=False)
            answer_item.author = request.user.profile
            answer_item.question = item
            answer_item.save()
            return redirect('question', question_id=question_id)
    else:
        answer_form = AnswerForm()
    return render(request, 'question.html', {'question': item,
                                             'answers': paginated_answer,
                                             'top_users': top_users,
                                             'popular_tags': popular_tags,
                                             'form': answer_form})


@login_required(login_url='login')
def ask(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            tags_input = question_form.cleaned_data['tags']
            tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tag_names]

            if len(tags) > 3:
                question_form.add_error('tags', 'Максимальное количество тегов - 3.')
            else:
                # Создаем вопрос, но не сохраняем его
                question_item = question_form.save(commit=False)

                # Устанавливаем автора вопроса
                question_item.author = request.user.profile

                # Сначала сохраняем вопрос, чтобы получить его id
                question_item.save()

                # Добавляем теги к вопросу
                question_item.tags.add(*tags)

                return redirect('question', question_id=question_item.id)
    else:
        question_form = QuestionForm()
    return render(request, 'ask.html', {'top_users': top_users,
                                        'popular_tags': popular_tags,
                                        'form': question_form})


def login_view(request):
    if request.method == 'POST':
        log_form = LoginForm(request.POST)
        if log_form.is_valid():
            user_name = log_form.cleaned_data['user_name']
            password = log_form.cleaned_data['password']
            user = authenticate(request, username=user_name, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('continue', '/'))
            else:
                log_form.add_error('password', 'Неверный логин или пароль')
    else:
        log_form = LoginForm()
    return render(request, 'login.html', {'top_users': top_users,
                                          'popular_tags': popular_tags,
                                          'form': log_form})


def signup(request):
    if request.method == 'POST':
        reg_form = RegisterForm(request.POST)
        if reg_form.is_valid():
            user = reg_form.save()
            if user:
                login(request, user)
                Profile.objects.create(user=user, nickname=reg_form.cleaned_data['username'])
                return redirect(reverse('index'))
            else:
                reg_form.add_error(None, 'Ошибка регистрации. Попробуйте еще раз')
    else:
        reg_form = RegisterForm()
    return render(request, 'signup.html', {'top_users': top_users,
                                           'popular_tags': popular_tags,
                                           'form': reg_form})


@login_required(login_url='login')
def settings(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = ProfileEditorForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

            user.username = form.cleaned_data['nickname']
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('settings')
    else:
        form = ProfileEditorForm(instance=profile)

    return render(request, 'settings.html', {'top_users': top_users,
                                             'popular_tags': popular_tags,
                                             'form': form})


def logout_view(request):
    logout(request)

    # Получаем предыдущий URL из HTTP_REFERER
    prev_url = request.META.get('HTTP_REFERER', None)

    if prev_url:
        return redirect(prev_url)
    else:
        return redirect(reverse('index'))
