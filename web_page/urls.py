# web_page/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('vesti/', views.article_list, name='article_list'),
    path('vesti/<int:pk>/', views.article_detail, name='article_detail'),
    path('galerija', views.gallery_view, name='gallery'),
]