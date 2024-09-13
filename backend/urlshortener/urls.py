from django.urls import path

from . import views

urlpatterns = [
    path('s/<str:short_url>/',
         views.redirect_to_original,
         name='redirect_to_original'),
]
