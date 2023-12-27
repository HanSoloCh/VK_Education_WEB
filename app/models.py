from django.db import models
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Sum


class ProfileManager(models.Manager):
    def get_top_users(self, count=5):
        # Получение пятерки самых лучших пользователей
        return self.get_queryset().annotate(
            total_rating=Sum(models.Case(
                models.When(answer__correct=True, then=1),
                default=0,
                output_field=models.IntegerField()
            ))
        ).order_by('-total_rating')[:count]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30)
    avatar = models.ImageField(upload_to='img/avatars', default='img/default.png')
    objects = ProfileManager()

    def __str__(self):
        return str(self.nickname)

    def get_user_rating(self):
        return Answer.objects.filter(author=self, correct=True).count()


# Модель тега
class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    @staticmethod
    def get_popular_tags(count=5):
        # Получение популярных тегов с помощью аннотации и сортировки
        return Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:count]


class Vote(models.Model):
    VOTE_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=7, choices=VOTE_CHOICES)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ['profile', 'vote_type', 'question', 'answer']


# Модель ответа на вопрос
class Answer(models.Model):
    content = models.TextField()
    correct = models.BooleanField(default=False)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    votes = models.ManyToManyField(Vote, related_name='answer_votes')

    def get_total_rating(self):
        # Получение общей оценки ответа
        return (Vote.objects.filter(answer=self, vote_type='like').count() -
                Vote.objects.filter(answer=self, vote_type='dislike').count())


# Менеджер модели вопроса
class QuestionManager(models.Manager):
    def best_questions(self):
        # Получение лучших вопросов с использованием аннотации и сортировки
        questions_items = self.get_queryset().annotate(
            total_rating=Sum(models.Case(
                models.When(vote__vote_type='like', then=1),
                models.When(vote__vote_type='dislike', then=-1),
                default=0,
                output_field=models.IntegerField(),
            ))
        ).order_by('-total_rating')
        return questions_items

    def new_questions(self):
        # Получение новых вопросов с сортировкой по убыванию ID
        return self.get_queryset().order_by('-id')

    def sort_questions(self):
        # Сортировка вопросов по убыванию ID
        return self.get_queryset().order_by('-id')[::-1]


# Модель вопроса
class Question(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    answer_count = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    votes = models.ManyToManyField(Vote, related_name='question_votes')
    objects = QuestionManager()

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        # Получение абсолютного URL для вопроса
        return f'/question/{self.id}'

    def get_total_rating(self):
        # Получение общей оценки вопроса
        return (Vote.objects.filter(question=self, vote_type='like').count() -
                Vote.objects.filter(question=self, vote_type='dislike').count())

    @staticmethod
    def paginate_questions(objects, page, per_page=15):
        # Пагинация вопросов с использованием Django Paginator
        paginator = Paginator(objects, per_page)
        return paginator.get_page(page)
