from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/accounts/login')
    return render(request,'home.html')