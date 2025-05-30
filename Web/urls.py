"""
URL configuration for Web project.

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
from django.urls import path, include
from django.contrib.auth import views as auth_views

import account
import inventory.views
from account import views

urlpatterns = [
    path('', inventory.views.item_list),

    path('item_list/', inventory.views.item_list, name='item_list'),
    path('add_item/', inventory.views.add_item, name='add_item'),
    path('item/<str:pk>/edit/', inventory.views.item_edit, name='item_edit'),
    path('item/<str:pk>/view/', inventory.views.item_view, name='item_view'),
    path('item/<str:pk>/delete/', inventory.views.item_delete, name='item_delete'),
    # path('item/in/<str:pk>/', inventory.views.item_in, name='item_in'),
    # path('item/out/<str:pk>/', inventory.views.item_out, name='item_out'),
    path('item/<int:pk>/stock_update/', inventory.views.item_stock_update, name='item_stock_update'),

    path('add_product/', inventory.views.add_product, name='add_product'),
    path('product_list/', inventory.views.product_list, name='product_list'),
    path('products_edit/<str:pk>/', inventory.views.product_edit, name='product_edit'),
    path('products_delete/<str:pk>/', inventory.views.product_delete, name='product_delete'),

    #path('history/', inventory.views.HistoryListView.as_view(), name='history-list'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('inventory/', include('inventory.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login1.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/item_list'), name='logout'),
    path('register/', account.views.register, name='register'),

    path('test/', inventory.views.test, name='test'),
]
