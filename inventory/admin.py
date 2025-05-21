from django.contrib import admin

# Register your models here.

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Item

@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    list_display = ['supply_id', 'name', 'spec', 'production_company', 'quantity', 'moq']