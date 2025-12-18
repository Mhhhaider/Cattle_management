# billing/models.py
from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name

class Item(models.Model):

    UNIT_CHOICES = [
        ("kg", "Kilogram"),
        ("liter", "Liter"),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="liter")

    def __str__(self):
        return f"{self.name} - {self.unit} ({self.stock} available)"



class Bill(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def total_amount(self):
        return sum(item.total_price() for item in self.billitem_set.all())

    def __str__(self):
        return f"Bill #{self.id} - {self.customer.name}"

# models.py
class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.CharField(max_length=15, blank=True, null=True)
    cardno = models.CharField(max_length=15, blank=True, null=True)
    

    def total_price(self):
        return self.item.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.pk:  # only reduce stock when creating a new BillItem
            self.item.stock -= self.quantity
            self.item.save()
        super().save(*args, **kwargs)

