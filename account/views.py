from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

# Create your views here.

from django.http import HttpResponse

# Create your views here.
def index(request):

    return render(request, "html/index.html")


def login(request):

    return render(request, "html/login.html")

def logout(request):

    return render(request, "html/logout.html")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 회원가입 후 로그인 페이지로 이동
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register1.html', {'form': form})