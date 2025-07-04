from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.urls import path, include
urlpatterns = [
    path('login/',views.login_view,name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/',views.registration, name='register'),
    path('activate/<uidb64>/<token>',views.activate,name='activate'),
    path('captcha/', include('captcha.urls')),
]
