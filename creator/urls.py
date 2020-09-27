from django.urls import path
#from __init__ import * 
from . import views


urlpatterns = [
    path('',views.home),
    path('home',views.home,name='home'),
    path('go',views.go),
    path('show_tg',views.show_tg,name='show_tg'),
    path('show_stu',views.show_stu,name='shows_tu'),
    path('add_tg',views.add_tg,name='add_tg'),
    path('logout',views.logout,name='logout'),
]
