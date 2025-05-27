# inventory/models.py
from django.db import models
from django.conf import settings  # User 모델을 안전하게 참조


# ts_id = models.CharField(primary_key=True)
# name = models.CharField(max_length=50, blank=True)
# supply = models.CharField(max_length=50, blank=True)
# supply_id = models.CharField(max_length=50, blank=True)
# quantity = models.PositiveIntegerField(default=0)
# description = models.TextField(blank=True)


# ID(자재코드) 품명 품번 사양 제작사 공급처 단가(unit) 단가(moq) 재고수량 moq 납기(장,단)
class Item(models.Model):
    id = models.AutoField(primary_key=True)  # 대체키 추가
    ts_id = models.CharField(max_length=15, blank=True)
    name = models.CharField(max_length=30, blank=True)
    supply_id = models.CharField(max_length=50, blank=True)
    spec = models.CharField(max_length=70, blank=True)
    production_company = models.CharField(max_length=30, blank=True)
    supply_company = models.CharField(max_length=30, blank=True)
    unit_price = models.PositiveIntegerField(default=0, blank=True, null=True)
    moq_price = models.PositiveIntegerField(default=0, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    purchase_quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    moq = models.CharField(max_length=10, blank=True)
    stock_location = models.CharField(max_length=50, blank=True)
    delivery_date = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    # 각 재고 항목을 등록한 사용자와 연결 (필요시)

    def __str__(self):
        return str(self.ts_id)




class Product(models.Model):
    name = models.CharField(max_length=50, primary_key=True)  # 제품명
    materials = models.ManyToManyField(Item, related_name='products', blank= True)  # 제품에 연결된 자재(재고) 리스트
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name