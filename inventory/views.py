from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Item, Product, ProductMaterial
from .forms import ItemForm, ProductForm
from django.contrib import messages
from django.views.decorators.http import require_POST
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
    field = request.GET.get('field', '')
    items = Item.objects.all()
    if q:
        if field == 'ts_id':
            if q.isdigit():  # id는 숫자이므로
                items = items.filter(id=int(q))
            else:
                items = Item.objects.none()  # 숫자가 아니면 검색 결과 없음
        elif field == 'name':
            items = items.filter(name__icontains=q)
        elif field == 'supply_id':
            items = items.filter(supply_id__icontains=q)
        elif field == 'spec':
            items = items.filter(spec__icontains=q)
        elif field == 'production_company':
            items = items.filter(production_company__icontains=q)
        elif field == 'supply_company':
            items = items.filter(supply_company__icontains=q)
        else:  # 전체(모든 항목)
            items = items.filter(
                Q(id__iexact=q) |  # id도 문자열로 비교
                Q(name__icontains=q) |
                Q(supply_id__icontains=q) |
                Q(spec__icontains=q) |
                Q(production_company__icontains=q) |
                Q(supply_company__icontains=q)
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
    return render(request, 'html/item_add.html', {'form': form})

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
    return render(request, 'html/item_edit.html', {'form' : form, 'item': item})




    # if request.method == 'POST':
    #     form = ItemForm(request.POST, instance=item)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('item_list')
    # else:
    #     form = ItemForm(instance=item)


@login_required
def item_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    #products = item.products.all()
    product_materials = ProductMaterial.objects.filter(item=item).select_related('product')
    # products 리스트와, 각 제품별 quantity를 딕셔너리로 준비
    products = [pm.product for pm in product_materials]
    product_quantities = {pm.product.pk: pm.quantity for pm in product_materials}
    return render(request, 'html/item_view.html', {
        'item': item,
        'products': products,
        'product_quantities': product_quantities,
    })

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

# @login_required
# def item_in(request, pk):
#     item = get_object_or_404(Item, id=pk)
#     item.quantity += 1  # 입고: 수량 1 증가
#     item.save()
#     messages.success(request, f"{item.name} 입고 완료 (현재 수량: {item.quantity})")
#     return redirect('item_list')  # 재고 리스트 페이지로 리다이렉트
#
# @login_required
# def item_out(request, pk):
#     item = get_object_or_404(Item, id=pk)
#     if item.quantity > 0:
#         item.quantity -= 1  # 출고: 수량 1 감소
#         item.save()
#         messages.success(request, f"{item.name} 출고 완료 (현재 수량: {item.quantity})")
#     else:
#         messages.error(request, f"{item.name}의 재고가 부족합니다.")
#     return redirect('item_list')

@login_required
@require_POST
def item_stock_update(request, pk):
    item = get_object_or_404(Item, id=pk)
    action = request.POST.get('action')
    try:
        qty = int(request.POST.get('quantity', 1))
        if qty < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "수량을 올바르게 입력하세요.")
        return redirect('item_list')

    if action == "in":
        item.quantity += qty
        item.save()
        messages.success(request, f"{item.name} 입고 완료 (현재 수량: {item.quantity})")
    elif action == "out":
        if item.quantity >= qty:
            item.quantity -= qty
            item.save()
            messages.success(request, f"{item.name} 출고 완료 (현재 수량: {item.quantity})")
        else:
            messages.error(request, f"{item.name}의 재고가 부족합니다.")
    else:
        messages.error(request, "잘못된 동작입니다.")

    return redirect('item_list')



@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)  # 새 제품 생성
            product.save()
            form.save_m2m()

            # 자재 수량 처리
            items = Item.objects.all()
            for item in items:
                qty = request.POST.get(f'quantity_{item.pk}', 0)
                try:
                    qty = int(qty)
                except (TypeError, ValueError):
                    qty = 0

                if qty > 0:
                    ProductMaterial.objects.update_or_create(
                        product=product,
                        item=item,
                        defaults={'quantity': qty}
                    )

            return redirect('product_list')
    else:
        form = ProductForm()

    items = Item.objects.all()
    return render(request, 'html/product_add.html', {
        'form': form,
        'materials': items,
    })
    # product = get_object_or_404(Product)
    # items = Item.objects.all()
    # if request.method == 'POST':
    #     form = ProductForm(request.POST, instance=product)
    #     if form.is_valid():
    #         for item in items:
    #             qty = int(request.POST.get(f'quantity_{item.pk}', 0))
    #             ProductMaterial.objects.update_or_create(
    #                 product=product,
    #                 item=item,
    #                 defaults={'quantity': qty}
    #             )
    #         #product = form.save(commit=False)
    #         # product.modified_by = request.user  # 예: 수정자 필드가 있다면 할당
    #         product.save()
    #         form.save_m2m()
    #         return redirect('product_list')
    #     # if form.is_valid():
    #     #     product = form.save(commit=False)
    #     #     # product.created_by = request.user  # 예: 추가 필드가 있다면 할당
    #     #     product.save()
    #     #     form.save_m2m()
    #     #     return redirect('product_list')
    #
    # else:
    #     form = ProductForm()
    # return render(request, 'html/product_add.html', {
    #     'form': form,
    #     'materials': items,
    # })

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'html/product_list.html', {'products': products})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    items = Item.objects.all()
    product_materials = product.materials.values_list('pk', flat=True)
    material_quantities = {
        pm.item_id: pm.quantity
        for pm in product.productmaterial_set.all()
    }
    if request.method == 'POST':

        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            for item in items:
                qty = int(request.POST.get(f'quantity_{item.pk}', 0))
                ProductMaterial.objects.update_or_create(
                    product=product,
                    item=item,
                    defaults={'quantity': qty}
                )
            product = form.save(commit=False)
            # product.modified_by = request.user  # 예: 수정자 필드가 있다면 할당
            product.save()
            form.save_m2m()
            return redirect('product_list')
    else:

        form = ProductForm(instance=product)
    return render(request, 'html/product_edit.html', {
        'form': form,
        'materials': items,
        'product': product,
        'product_materials': list(product_materials),
        'material_quantities': material_quantities,
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