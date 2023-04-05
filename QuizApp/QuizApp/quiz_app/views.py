import json
import random

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Min, Max, Avg
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from .models import Question
from .models import QuizResult
from .models import QuizTopic


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('quiz_app:quiz')
    else:
        if request.user.is_authenticated:
            return redirect("quiz_app:quiz")
        form = UserCreationForm()
    return render(request, 'quiz_app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('quiz_app:quiz')
            else:
                form.add_error(None, 'Invalid login credentials.')
    else:
        print(request.user)
        if request.user.is_authenticated:
            return redirect("quiz_app:quiz")
        form = AuthenticationForm()
    return render(request, 'quiz_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('quiz_app:login')


@login_required
def quiz_question(request):
    if request.method == 'POST':
        score = 0
        selected_questions = json.loads(request.POST.get('question_answer'))
        print(selected_questions)
        for key, val in selected_questions.items():
            selected_option = request.POST.get(str(key))
            print("selected_option=", selected_option, "question.correct_answer=", val)
            if selected_option == val:
                score += 1
        json_data = {
            'score': score,
            'redirect_url': reverse('quiz_app:result', kwargs={'score': score})
        }
        return JsonResponse(json_data)
    else:
        selected_topic = request.session.get('topic_id')
        questions = Question.objects.filter(topic__id=selected_topic)
        selected_questions = random.sample(list(questions), 5)
        question_answer = {}
        for question in selected_questions:
            question_answer[question.id] = question.correct_answer
        context = {'questions': selected_questions, 'question_answer_json': json.dumps(question_answer)}
        return render(request, 'quiz_app/quiz_question.html', context)


@login_required
def quiz(request):
    topics = QuizTopic.objects.all()
    if request.method == 'POST':
        topic_id = request.POST.get('topic')
        print(topic_id)
        questions = Question.objects.filter(topic__id=topic_id)
        if not questions.exists():
            messages.error(request, f"No questions found for selected topics. Please choose other topics.")
            return redirect('quiz_app:quiz')
        request.session['topic_id'] = topic_id
        return redirect('quiz_app:quiz_question')
    return render(request, 'quiz_app/quiz.html', {'topics': topics})


@login_required
def result(request, score):
    selected_topic = request.session.get('topic_id')
    user = request.user
    quiz_topic = QuizTopic.objects.get(id=selected_topic)

    quiz_result = QuizResult(user=user, quiz_topic=quiz_topic, score=score)
    quiz_result.save()

    if score <= 2:
        message = "Please try again!"
    elif score == 3:
        message = "Good job!"
    elif score == 4:
        message = "Excellent work!"
    else:
        message = "You are a genius!"

    context = {'score': score, 'message': message}
    return render(request, 'quiz_app/result.html', context)


@login_required
def score_history(request):
    results = QuizResult.objects.filter(user=request.user)
    average_score = results.aggregate(avg_score=Avg('score'))['avg_score']
    highest_score = results.aggregate(max_score=Max('score'))['max_score']
    lowest_score = results.aggregate(min_score=Min('score'))['min_score']
    context = {
        'results': results,
        'average_score': average_score,
        'highest_score': highest_score,
        'lowest_score': lowest_score,
    }
    return render(request, 'quiz_app/score_history.html', context)
