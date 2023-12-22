from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Question, Answer, Profile, Tag


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

    def save(self, **kwargs):
        profile = super().save(**kwargs)

        profile.avatar = self.cleaned_data.get('avatar')
        profile.save()

        return profile


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

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        super(QuestionForm, self).__init__(*args, **kwargs)

    def get_tags(self):
        tags_input = self.cleaned_data.get('tags')
        tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

        if len(tag_names) > 3:
            raise forms.ValidationError('Максимальное количество тегов - 3.')

        return tag_names

    def save(self, commit=True):
        question_item = super().save(commit=False)
        question_item.author = self.author

        try:
            tag_names = self.get_tags()
            tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tag_names]
        except forms.ValidationError as e:
            self.add_error('tags', e.message)
            return question_item

        if commit:
            question_item.save()
            question_item.tags.add(*tags)

        return question_item


class AnswerForm(forms.ModelForm):
    content = forms.CharField(label='Ваш ответ', widget=forms.Textarea)

    class Meta:
        model = Answer
        fields = ['content']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.item = kwargs.pop('item', None)
        super(AnswerForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        answer_item = super().save(commit=False)
        answer_item.author = self.user.profile
        answer_item.question = self.item
        if commit:
            answer_item.save()
        return answer_item
