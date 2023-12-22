import json

from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.paginator import Paginator

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from .forms import ProfileEditorForm, LoginForm, RegisterForm, QuestionForm, AnswerForm
from .models import Question, Profile, Tag, Answer, Vote

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


def hottest(request):
    page_name = f'Самое популярное'
    page = request.GET.get('page', 1)
    hot_questions = Question.objects.best_questions()
    paginated_questions = Question.paginate_questions(hot_questions, page)
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


@csrf_protect
def question(request, question_id):
    item = Question.objects.get(id=question_id)
    page = request.GET.get('page', 1)
    paginated_answer = Question.paginate_questions(item.answer_set.all(), page, 5)

    if request.method == 'POST':
        answer_form = AnswerForm(request.POST, user=request.user, item=item)
        if answer_form.is_valid():
            answer_form.save()
            return redirect('question', question_id=question_id)
    else:
        answer_form = AnswerForm()
    return render(request, 'question.html', {'question': item,
                                             'answers': paginated_answer,
                                             'top_users': top_users,
                                             'popular_tags': popular_tags,
                                             'form': answer_form})


@csrf_protect
@login_required(login_url='login')
def ask(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, author=request.user.profile)
        if question_form.is_valid():
            question_item = question_form.save()
            if question_form.is_valid():
                return redirect('question', question_id=question_item.id)
    else:
        question_form = QuestionForm()
    return render(request, 'ask.html', {'top_users': top_users,
                                        'popular_tags': popular_tags,
                                        'form': question_form})


@csrf_protect
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


@csrf_protect
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


@csrf_protect
@login_required(login_url='login')
def settings(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = ProfileEditorForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            user.username = form.cleaned_data['nickname']
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('settings')
    else:
        form = ProfileEditorForm(instance=profile, initial=model_to_dict(request.user))

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


@csrf_protect
@login_required(login_url='login')
def question_like(request):
    question_id = request.POST.get('question_id')
    like_type = request.POST.get('like_type')

    question_item = get_object_or_404(Question, pk=question_id)

    existing_vote = Vote.objects.filter(profile=request.user.profile, question=question_item).first()

    # Если голос существует и прожат тот же голос
    if existing_vote and existing_vote.vote_type == like_type:
        # Если голос уже существует, удаляем его
        existing_vote.delete()
    # Если голос существует, но прожат обратный голос
    elif existing_vote:
        # Меняем значение на противоположный
        existing_vote.vote_type = like_type
        existing_vote.save()
    else:
        Vote.objects.create(profile=request.user.profile, vote_type=like_type, question=question_item)

    count = question_item.get_total_rating()
    return JsonResponse({'count': count})


@csrf_protect
@login_required(login_url='login')
def answer_like(request):
    answer_id = request.POST.get('answer_id')
    like_type = request.POST.get('like_type')

    answer_item = get_object_or_404(Answer, pk=answer_id)

    existing_vote = Vote.objects.filter(profile=request.user.profile, answer=answer_item).first()

    # Если голос существует и прожат тот же голос
    if existing_vote and existing_vote.vote_type == like_type:
        # Если голос уже существует, удаляем его
        existing_vote.delete()
    # Если голос существует, но прожат обратный голос
    elif existing_vote:
        # Меняем значение на противоположный
        existing_vote.vote_type = like_type
        existing_vote.save()
    else:
        Vote.objects.create(profile=request.user.profile, vote_type=like_type, answer=answer_item)

    count = answer_item.get_total_rating()
    return JsonResponse({'count': count})

