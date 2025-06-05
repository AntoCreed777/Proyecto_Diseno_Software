from django.urls import path
from . import views

urlpatterns = [
    path('',views.bottons_view),
]
