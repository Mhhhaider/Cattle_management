from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

##================Login==========================##
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # User 1 - Special Dashboard
            if user.username == 'vasai':
                return redirect('cow-home')

            # User 2 - Normal Dashboard
            return redirect('home')

        else:
            messages.error(request, 'Username or Password is incorrect !!')
            return redirect('log-in')

    return render(request, 'Dashboard/login.html')


def Logout_user(request):
    logout(request)
    return redirect('log-in')



##================Registration==========================##
def registration(request):
    return render(request,'Dashboard/registration.html')


##================Home-page==========================##
@login_required(login_url="log-in")
def home(request):
    return render(request,'Dashboard/home-page.html')



@login_required(login_url="log-in")
def admin_home(request):
    return render(request,'Dashboard/admin.html')
