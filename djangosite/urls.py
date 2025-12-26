"""
URL configuration for djangosite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from operations.views import OperationList
from operations import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', OperationList.as_view(), name='operation_list'),

    path('mongo/', views.mongo_list, name='mongo_list'),
    path('mongo/create/', views.mongo_create, name='mongo_create'),
    path('mongo/edit/<str:op_id>/', views.mongo_edit, name='mongo_edit'),
    path('mongo/delete/<str:op_id>/', views.mongo_delete, name='mongo_delete'),
]
