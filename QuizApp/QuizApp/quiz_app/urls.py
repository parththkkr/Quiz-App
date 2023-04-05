from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=True)),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz_question/', views.quiz_question, name='quiz_question'),
    path('result/<int:score>/', views.result, name='result'),
    path('score_history/', views.score_history, name='score_history'),
]

app_name = 'quiz_app'
