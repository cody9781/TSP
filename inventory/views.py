from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Item, Product
from .forms import ItemForm, ProductForm
from django.contrib import messages
# Create your views here.

from django.http import HttpResponse

# Create your views here.

def test(request):
    return render(request, 'temp/mine/tables.html')


#def item_list(request):
#    items = Item.objects.all
#    return render(request, 'html/item_list.html', {'items': items})

def item_list(request):
    q = request.GET.get('q', '')
    items = Item.objects.all()
    if q:
        items = items.filter(
            Q(name__icontains=q) |
            Q(supply_id__icontains=q) |
            Q(spec__icontains=q) |
            Q(production_company__icontains=q) |
            Q(supply_company__icontains=q) |
            Q(description__icontains=q)
        )
    return render(request, 'html/item_list.html', {'items': items})



@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            if not item.quantity:  # None, 0, '' 모두 0으로 처리
                item.quantity = 0
            item.created_by = request.user
            item.save()
            form.save_m2m()
            return redirect('/item_list')
    else:
        form = ItemForm()
    return render(request, 'html/form_add.html', {'form': form})

@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'html/form_edit.html', {'form' : form, 'item': item})

@login_required
def item_delete1(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return redirect('item_edit', pk=pk)

@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'html/item_confirm_delete.html', {'item': item})

@login_required
def item_in(request, pk):
    item = get_object_or_404(Item, id=pk)
    item.quantity += 1  # 입고: 수량 1 증가
    item.save()
    messages.success(request, f"{item.name} 입고 완료 (현재 수량: {item.quantity})")
    return redirect('item_list')  # 재고 리스트 페이지로 리다이렉트

@login_required
def item_out(request, pk):
    item = get_object_or_404(Item, id=pk)
    if item.quantity > 0:
        item.quantity -= 1  # 출고: 수량 1 감소
        item.save()
        messages.success(request, f"{item.name} 출고 완료 (현재 수량: {item.quantity})")
    else:
        messages.error(request, f"{item.name}의 재고가 부족합니다.")
    return redirect('item_list')



@login_required
def add_product(request):
    items = Item.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            # product.created_by = request.user  # 예: 추가 필드가 있다면 할당
            product.save()
            form.save_m2m()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'html/add_product.html', {'form': form, 'materials': items})

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'html/product_list.html', {'products': products})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    items = Item.objects.all()
    product_materials = product.materials.values_list('pk', flat=True)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            # product.modified_by = request.user  # 예: 수정자 필드가 있다면 할당
            product.save()
            form.save_m2m()
            return redirect('product_list')
    else:

        form = ProductForm(instance=product)
    return render(request, 'html/edit_product.html', {
        'form': form,
        'materials': items,
        'product': product,
        'product_materials': list(product_materials)
    })

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        # messages.success(request, '제품이 성공적으로 삭제되었습니다.')  # 메시지 프레임워크 사용 시
        return redirect('product_list')

    return render(request, 'html/product_confirm_delete.html', {
        'product': product
    })