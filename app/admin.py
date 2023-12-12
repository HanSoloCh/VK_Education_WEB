from django.contrib import admin

# Register your models here.

from .models import Question, Profile, Tag, Like, Answer

admin.site.register(Question)
admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(Answer)
