from django.urls import path
from .views import *

app_name = 'inventory'
urlpatterns = [
    path('add_item', add_item, name='add_item'),
    path('item_list', item_list, name='item_list'),
]