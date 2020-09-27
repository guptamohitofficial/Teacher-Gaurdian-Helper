from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('home',views.home,name='home'),
    path('signup',views.signup,name='signup'),
    path('show_stu',views.show_stu,name='shows_tu'),
    path('add_stu',views.add_stu,name='add_stu'),
    path('add_sem',views.add_sem,name='add_sem'),
    path('VerifyEmail',views.VerifyEmail,name='VerifyEmail'),
    path('del_sem',views.del_sem,name='del_sem'),
    path('mid_sem',views.mid_sem,name='mid_sem'),
    path('sem_marks',views.sem_marks,name='sem_marks'),
    path('update_pinof',views.update_pinof,name='update_pinof'),
    path('search_stu',views.search_stu,name='search_stu'),
    path('UploadImg',views.UploadImg,name='UploadImg'),
    path('UploadImgtg',views.UploadImgtg,name='UploadImgtg'),
    path('logout',views.logout,name='logout'),
    path('about_us',views.about_us,name='about_us'),
    path('reject',views.reject,name='reject'),
    path('accept',views.accept,name='accept'),
    path('add_notification',views.add_notification,name='add_notification'),
]
