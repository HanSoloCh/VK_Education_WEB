from django.core.management.base import BaseCommand
from app.models import Profile, Question, Answer, Tag, Vote
from django.contrib.auth.models import User
import random

content_examples = [
    "Текст очень интересного вопроса, ответ на который я хочу получить!!!!",
    "Как вы думаете, какой из покемонов самый милый?",
    "Люблю смотреть советские фильмы, какие советские фильмы нравятся вам больше всего?",
    "Вас когда-нибудь спрашивали на улице, сколько стоит ваш шмот? Или так только в видео бывает",
    "Что делать, если я не понимаю программирование?",
    "Это текст очень интересного вопроса. Пожалуйста, не отвечайте на него."
]
answer_examples = [
    "Такой глупый вопрос, что даже отвечать на него не буду((",
    "О! Тоже ищу ответ на этот вопрос. Пни, когда ответят.",
    "Все просто. Просто проинтегрируй это и все получится.",
    "Изучение питона лучше всего начать с похода в зоопарк, не так ли? Или я сам не в теме?",
]


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Ratio for data generation (recommended:10000)')

    def handle(self, *args, **options):
        ratio = options['ratio']

        # Создание пользователя
        for i in range(ratio):
            print(f'user-{str(i)}')
            user = User.objects.create(username=f'user-{str(i)}')
            Profile.objects.create(user=user, nickname=f'nickname-{str(i)}',
                                   avatar=f'img/{random.randint(1, 10)}.png')

        # Создание тегов
        for i in range(ratio):
            print(f'tag-{str(i)}')
            Tag.objects.create(name=f'tag-{str(i)}')

        # Создание вопросов и ответов
        for i in range(ratio * 10):
            print(f'Question-{str(i)}')
            author = Profile.objects.get(id=random.randint(1, ratio))
            question = Question.objects.create(title=f'Question-{str(i)}',
                                               content=random.choice(content_examples),
                                               answer_count=random.randint(0, 10), author=author)
            tag_nums = set()

            max_tags = 3
            for _ in range(max_tags):
                tag_nums.add(random.randint(1, ratio))
            tag_nums = list(tag_nums)

            for j in range(len(tag_nums)):
                question.tags.add(Tag.objects.get(id=tag_nums[j]))

            for _ in range(10):
                author = Profile.objects.get(id=random.randint(1, ratio))
                answer = Answer.objects.create(content=random.choice(answer_examples), correct=bool(random.getrandbits(1)),
                                      question=question, author=author)
                # Лайки ответа
                for j in range(3):
                    Vote.objects.create(profile=Profile.objects.get(id=random.randint(1, ratio)),
                                        vote_type=random.choice(['like', 'dislike']),
                                        answer=answer)

            # Лайки вопроса
            for j in range(3):
                Vote.objects.create(profile=Profile.objects.get(id=random.randint(1, ratio)),
                                    vote_type=random.choice(['like', 'dislike']),
                                    question=question)
