from django.urls import path

from . import views

urlpatterns = [
    path('<slug:slug>/',
         views.redirect_to_original,
         name='redirect_to_original'),
]
