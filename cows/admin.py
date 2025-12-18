from django.contrib import admin
from .models import Batch, Cattle, Milking, BatchInventory,Income

admin.site.register(Batch)
admin.site.register(Cattle)
admin.site.register(Milking)
admin.site.register(BatchInventory)
admin.site.register(Income)