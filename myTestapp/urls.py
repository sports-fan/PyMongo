from django.urls import path

from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('hello/', views.hello_world, name='hello_world'),
    path('create/', views.create, name='create'),
    path('bap_teens_levels/', views.bap_teens_levels, name='bap_teens_levels')
]