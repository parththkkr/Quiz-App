from django.contrib import admin
from .models import QuizResult, Question

# Register your models here.


admin.site.register(Question)
admin.site.register(QuizResult)
