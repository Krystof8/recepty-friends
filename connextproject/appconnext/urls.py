from django.urls import path
from . import views
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from .forms import LoginForm


urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='appconnext/login.html', authentication_form=LoginForm, redirect_authenticated_user=True), name='login-page'),
    path('logout', auth_views.LogoutView.as_view(), name='logout-page'),
    path('register', views.register, name='register-page'),
    path('main-page', views.main_page, name='main-page'),
    path('main-page/<int:id>', views.edit, name='edit-page'),
    path('main-page/delete/<int:id>', views.delete, name='delete-page'),
    path('main-page/detail-food/<int:id>', views.detail_food, name='detail-food-page'),
    path('select-food', views.select_food, name='select-food-page'),
    path('add-meal', views.add_meal, name='add-meal-page'),
    path('my-profile', views.profile, name='profile-page'),
    path('search-friends', views.search_friends, name='search-friends-page'), 
    path('<slug:slug>', views.profile_detail, name='profile-detail-page'),
    path('<slug:slug>/friends-list', views.friends_list, name='friends-list-page'),
    path('<slug:slug>/food-list', views.friend_food_list, name='friend-food-list-page')  
]
