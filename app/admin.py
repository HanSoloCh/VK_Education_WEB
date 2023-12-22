from django.contrib import admin

# Register your models here.

from .models import Question, Profile, Tag, Answer, Vote

admin.site.register(Question)
admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Answer)
admin.site.register(Vote)

