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
    avatar = models.ImageField(upload_to='img/', default='img/default.png')
    objects = ProfileManager()

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


# Модель "Лайка" для оценки
class Like(models.Model):
    count = models.IntegerField(null=False)


# Модель ответа на вопрос
class Answer(models.Model):
    content = models.TextField()
    like = models.ForeignKey(Like, on_delete=models.CASCADE, related_name='answer_likes')
    dislike = models.ForeignKey(Like, on_delete=models.CASCADE, related_name='answer_dislikes')
    correct = models.BooleanField()
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def get_total_rating(self):
        # Получение общей оценки ответа
        return str(int(self.like.count - self.dislike.count))


# Менеджер модели вопроса
class QuestionManager(models.Manager):
    def best_questions(self):
        # Получение лучших вопросов с использованием аннотации и сортировки
        return self.get_queryset().annotate(
            rating=models.F('like__count') - models.F('dislike__count')
        ).order_by('-rating')[:10]

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
    like = models.ForeignKey(Like, on_delete=models.CASCADE, related_name='question_likes')
    dislike = models.ForeignKey(Like, on_delete=models.CASCADE, related_name='question_dislikes')
    answer_count = models.IntegerField()
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    objects = QuestionManager()

    def get_absolute_url(self):
        # Получение абсолютного URL для вопроса
        return f'/question/{self.id}'

    def get_total_rating(self):
        # Получение общей оценки вопроса
        return str(int(self.like.count - self.dislike.count))

    @staticmethod
    def paginate_questions(objects, page, per_page=15):
        # Пагинация вопросов с использованием Django Paginator
        paginator = Paginator(objects, per_page)
        return paginator.get_page(page)
