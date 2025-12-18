from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.



##================Home-page==========================##
@login_required(login_url="log-in")
def shop(request):
    return render(request,'shop_home.html')


@login_required(login_url="log-in")
def home_shop(request):
    return render(request,'shop-home.html')
