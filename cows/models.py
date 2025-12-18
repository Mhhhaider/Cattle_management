from django.db import models

class Batch(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Cattle(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='cattles')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    breed = models.CharField(max_length=50)
    purchase=models.DateTimeField(null=True, blank=True)
    purchase_amount=models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    milk=models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    convincing_date = models.DateField(null=True, blank=True)  # maybe pregnancy confirmation or vet check
    result = models.CharField(max_length=100, blank=True, null=True)
    milk_day_15 = models.DecimalField(max_digits=6, decimal_places=2,  null=True, blank=True)
    milk_day_30 = models.DecimalField(max_digits=6, decimal_places=2,  null=True, blank=True)
    milk_day_60 = models.DecimalField(max_digits=6, decimal_places=2,  null=True, blank=True)
    milk_day_75 = models.DecimalField(max_digits=6, decimal_places=2,  null=True, blank=True)
    outward_date = models.DateField(null=True, blank=True)
    sale_date = models.DateField(null=True, blank=True)
    sold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salvage_date = models.DateField(null=True, blank=True)
    salvage = models.CharField(max_length=50, blank=True, null=True)
    is_archive = models.BooleanField(default=False)
    reentered = models.BooleanField(default=False)

    HEALTH_CHOICES = [
        ('Healthy', 'Healthy'),
        ('Sick', 'Sick'),
        ('Critical', 'Critical'),
    ]
    health_status = models.CharField(max_length=20, choices=HEALTH_CHOICES, default='Healthy')
    BREEDING_CHOICES = [
        ('Fresh', 'Fresh'),
        ('Inseminated', 'Inseminated'),
        ('Pregnant', 'Pregnant'),
        ('Dry', 'Dry'),
    ]
    breeding = models.CharField(max_length=20, choices=BREEDING_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.breed})"

class Milking(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='milkings')
    date = models.DateField()
    milk_time=models.CharField(max_length=100, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)  # liters

    def __str__(self):
        return f"{self.cattle.name} - {self.amount}L on {self.date}"





class BatchInventory(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='inventory_records')
    batch_no = models.CharField(max_length=50)
    inward_date = models.DateField()
    purchase_date = models.DateField(null=True, blank=True)
    convincing_date = models.DateField(null=True, blank=True)  # maybe pregnancy confirmation or vet check
    result = models.CharField(max_length=100, blank=True, null=True)
    milk_day_0 = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True, blank=True)   # milk at inward
    milk_day_15 = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True, blank=True)
    milk_day_30 = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True, blank=True)
    milk_day_60 = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True, blank=True)
    milk_day_75 = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True, blank=True)
    outward_date = models.DateField(null=True, blank=True)
    sale_date = models.DateField(null=True, blank=True)
    sold = models.CharField(max_length=50, blank=True, null=True)
    salvage_date = models.DateField(null=True, blank=True)
    salvage = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.cattle.name} - Batch {self.batch_no}"
    


class Breeding(models.Model):
    male_cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='male_breedings')
    female_cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='female_breedings')
    breeding_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.male_cattle.name} x {self.female_cattle.name}"




class HealthStatus(models.Model):
    cattle = models.ForeignKey('Cattle', on_delete=models.CASCADE, related_name='health_records')
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='health_records')
    vaccination_date = models.DateField()
    
    STATUS_CHOICES = [
        ('Healthy', 'Healthy'),
        ('Sick', 'Sick'),
        ('Critical', 'Critical'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Healthy')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cattle.name} - {self.status} on {self.vaccination_date}"
    


class FeedStock(models.Model):
    cattle = models.ForeignKey('Cattle', on_delete=models.CASCADE, related_name='feed_records')
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='feed_records')
    
    feed_type = models.CharField(max_length=100)
    quantity = models.FloatField(help_text="Quantity in kg/litre")
    unit = models.CharField(max_length=10, default='kg')
    feed_date = models.DateField(auto_created=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cattle.name} - {self.feed_type} ({self.quantity}{self.unit})"
    


class Income(models.Model):
    amount = models.FloatField()
    source = models.CharField(max_length=100, help_text="e.g., Milk Sale, Animal Sale, Others")
    batch = models.ForeignKey('Batch', on_delete=models.SET_NULL, null=True, blank=True, related_name='income_records')
    cattle = models.ForeignKey('Cattle', on_delete=models.SET_NULL, null=True, blank=True, related_name='income_records')
    income_date = models.DateField(auto_created=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - {self.amount} on {self.income_date}"


