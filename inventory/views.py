from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Item, Product, ProductMaterial
from .forms import ItemForm, ProductForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from reversion import create_revision  # 수정된 임포트 경로
from django.views.generic import ListView
from reversion.models import Version
from reversion import set_user, set_comment
from django.utils.functional import cached_property
from collections import defaultdict
from django.core.paginator import Paginator



# Create your views here.

from django.http import HttpResponse

# Create your views here.

def test(request):
    return render(request, 'temp/mine/tables.html')


# def get_changed_fields(version, previous_version):
#     """두 버전의 field_dict를 비교해 변경된 필드와 값을 반환"""
#     if not previous_version:
#         # 최초 생성 버전도 동일한 구조로 반환
#         return [(key, {'old': None, 'new': value}) for key, value in version.field_dict.items()]
#     changed = []
#     for key, value in version.field_dict.items():
#         prev_value = previous_version.field_dict.get(key)
#         if value != prev_value:
#             changed.append((key, {'old': prev_value, 'new': value}))
#     return changed
#
#
# class HistoryListView(ListView):
#     template_name = 'html/history_list.html'
#     context_object_name = 'page_obj'
#     paginate_by = 20
#
#     def get_queryset(self):
#         # 모든 버전을 한 번에 조회 (쿼리 최적화)
#         return Version.objects.select_related('revision', 'content_type').filter(
#             content_type__model__in=['item', 'product', 'productmaterial']
#         ).order_by('-revision__date_created')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['main_fields'] = ['ts_id', 'name', 'supply_id', 'product', 'item', 'quantity']
#
#         # 객체별 버전 그룹화 함수
#         def group_versions(versions):
#             groups = defaultdict(list)
#             for v in versions:
#                 key = (v.content_type.id, v.object_id)
#                 groups[key].append(v)
#             return groups
#
#         # 모든 버전 그룹화
#         all_versions = list(self.object_list)
#         grouped = group_versions(all_versions)
#
#         # 그룹별 버전 페어 생성
#         version_pairs = []
#         for group in grouped.values():
#             sorted_versions = sorted(group, key=lambda x: x.revision.date_created, reverse=True)
#             for i, version in enumerate(sorted_versions):
#                 prev = sorted_versions[i + 1] if i + 1 < len(sorted_versions) else None
#                 version_pairs.append({
#                     'version': version,
#                     'prev_version': prev,
#                     'changed_fields': get_changed_fields(version, prev)
#                 })
#
#         # 최종 정렬 및 페이징
#         version_pairs.sort(key=lambda x: x['version'].revision.date_created, reverse=True)
#         paginator = Paginator(version_pairs, self.paginate_by)
#         page_number = self.request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#
#         context['version_pairs'] = page_obj.object_list
#         context['version_pairs'] = [
#             pair for pair in context['version_pairs']
#             if pair['changed_fields']
#         ]
#         context['page_obj'] = page_obj
#         return context







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


# @create_revision()  # 리비전 생성 데코레이터 추가
@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            form.save_m2m()

            # 리비전에 사용자 정보 추가
            # set_user(request.user)
            # set_comment("Item 생성")

            return redirect('/item_list')
    else:
        form = ItemForm()
    return render(request, 'html/item_add.html', {'form': form})




@login_required
#@create_revision()
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()

            # 리비전에 사용자 정보 추가

            # set_user(request.user)
            # set_comment("Item 수정")
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
    total_quantity = sum(product_quantities.get(product.pk, 0) for product in products)
    return render(request, 'html/item_view.html', {
        'item': item,
        'products': products,
        'product_quantities': product_quantities,
        'total_quantity': total_quantity,
    })

@login_required
def item_delete1(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return redirect('item_edit', pk=pk)

@login_required
#@create_revision()
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()

        # set_user(request.user)
        # set_comment("Item 삭제")
        return redirect('item_list')
    return render(request, 'html/item_confirm_delete.html', {'item': item})


@login_required
@require_POST
#@create_revision()
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

    # 리비전에 사용자 정보 추가
    # set_user(request.user)
    # set_comment("Item 수정")
    return redirect('item_list')



@login_required
#@create_revision()
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

            # set_user(request.user)
            # set_comment("Product 생성")
            return redirect('product_list')
    else:
        form = ProductForm()

    items = Item.objects.all()
    return render(request, 'html/product_add.html', {
        'form': form,
        'materials': items,
    })

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'html/product_list.html', {'products': products})


@login_required
#@create_revision()
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

            # set_user(request.user)
            # set_comment("Product 수정")
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

