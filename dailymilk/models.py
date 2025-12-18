from django.db import models
from django.utils import timezone

class Farmer(models.Model):
    cardno = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MilkCollection(models.Model):
    SHIFT_CHOICES = (
        ('M', 'Morning'),
        ('E', 'Evening'),
    )
    
    farmer = models.CharField(max_length=100)
    date = models.DateField(default=timezone.localdate)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    quantity_ltr = models.DecimalField(max_digits=6, decimal_places=2)
    # fat = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rate_per_ltr = models.DecimalField(max_digits=6, decimal_places=2)
    cardno = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=120, blank=True)
    payment = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.amount = self.quantity_ltr * self.rate_per_ltr
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.farmer} - {self.get_shift_display()} ({self.date})"
