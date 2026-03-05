from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
def login_view(request):
    print(request.method, request.POST or None) # None refers to request.GET
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print("user is", user)
        if user is not None:
            login(request, user)
            print("login here..!")
            return redirect("/")
    print("invalid login")
    return render(request, "auth/login.html", {})

def register_view(request):
    if request.method == "POST":
        print(request.POST)
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        # django forms 
        # user_exists = User.objects.filter(username__iexact=username).exists()
        # email_exists = User.objects.filter(email__iexact=email).exists()
        try:        
            User.objects.create_user(username=username, email=email, password=password)
        except Exception as e:
            print("Error occurred while creating user:", e)
    return render(request, "auth/register.html", {})