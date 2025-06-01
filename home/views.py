from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import render,redirect


def bottons_view(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if 'logout' == accion:
            logout(request)
            return redirect('/accounts/login')
        if 'ingresar' == accion:
            pass
    return render(request,'home.html')