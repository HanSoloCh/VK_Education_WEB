from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Question, Answer, Profile


class LoginForm(forms.Form):
    user_name = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Электронная почта')
    username = forms.CharField(
        label='Имя пользователя',
        max_length=30,
        error_messages={
            'max_length': 'Максимальная длинна имени - 30 символов.'
        }
    )
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    re_password = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 're_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        re_password = cleaned_data.get('re_password')

        if password and re_password and password != re_password:
            raise ValidationError('Пароли должны совпадать')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
        return user


class ProfileEditorForm(forms.ModelForm):
    nickname = forms.CharField(label='Имя пользователя')
    email = forms.EmailField(label='Электронная почта')
    avatar = forms.ImageField(label='Аватар', required=False)

    class Meta:
        model = Profile
        fields = ['nickname', 'email', 'avatar']

    def __init__(self, *args, **kwargs):
        super(ProfileEditorForm, self).__init__(*args, **kwargs)
        # Заполняем поле nickname текущим никнеймом пользователя
        self.initial['nickname'] = self.instance.nickname
        self.initial['email'] = self.instance.user.email


class QuestionForm(forms.ModelForm):
    title = forms.CharField(
        label='Заголовок',
        max_length=100,
        error_messages={
            'max_length': 'Заголовок вопроса не может превышать 100 символов'
        }
    )
    content = forms.CharField(label='Текст вопроса', widget=forms.Textarea)
    tags = forms.CharField(
        label='Теги',
        help_text='Можно ввести до 3 тегов через запятую',
        required=False,
    )

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']


class AnswerForm(forms.ModelForm):
    content = forms.CharField(label='Ваш ответ', widget=forms.Textarea)

    class Meta:
        model = Answer
        fields = ['content']
