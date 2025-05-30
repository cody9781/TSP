
# inventory/forms.py
from django import forms
from .models import Item, Product

#사용자 등록/수정 폼은 Django 내장 UserCreationForm, UserChangeForm 활용 가능.

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'  # id 필드는 자동 제외됨 (AutoField 특성)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'materials', 'description']
        widgets = {
            'materials': forms.CheckboxSelectMultiple,  # 자재를 체크박스로 여러 개 선택
        }
