from django.shortcuts import redirect, render
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

def home_view(request):
    return render(request, "home.html")

def register_view(request):
    return render(request, "register.html")

def dashboard_view(request):
    return render(request, "dashboard.html")

def login_validation(request):
    if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            auth_check = auth_user(username, password)

            logger.info("FUCK")

            print(auth_check)
            
            if auth_check == True:
                return redirect('main:dashboard')
            else:
                return render(request, 'main/home.html', {'error': 'Invalid username or password.'})
            
def auth_user(username, password):
     return True

def logout_user(request):
     logger.info("FUCK2")
     return render(request, "home.html")
    

