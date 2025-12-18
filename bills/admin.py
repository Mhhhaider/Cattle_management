from django.contrib import admin
from .models import Customer, Item, Bill, BillItem

admin.site.register(Customer)
admin.site.register(Item)
admin.site.register(Bill)
admin.site.register(BillItem)