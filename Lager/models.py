from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ProductType(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    def update_stock(self, weight_change):
        """Atomare Lagerbestandsaktualisierung"""
        with transaction.atomic():
            self.refresh_from_db()
            self.current_stock_kg += weight_change
            if self.current_stock_kg < 0:
                raise ValidationError("Lagerbestand darf nicht negativ werden")
            self.save()

    def __str__(self):
        return f"{self.category} - {self.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ausstehend'),
        ('completed', 'Abgeschlossen'),
    ]
    customer_name = models.CharField(max_length=100)
    order_date = models.DateTimeField(auto_now_add=True)
    #delivery_date = models.DateTimeField(blank=True, null=True, verbose_name="Liefertermin")
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Liefertermin")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def clean(self):
        if self.status == 'completed':
            for item in self.orderitem_set.all():
                if item.weight_kg > item.product_type.current_stock_kg:
                    raise ValidationError(
                        f"Nicht genug Lagerbestand für {item.product_type} "
                        f"(Verfügbar: {item.product_type.current_stock_kg} kg)"
                    )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            items = list(self.orderitem_set.all())
            super().delete(*args, **kwargs)
            for item in items:
                if self.status != 'completed':
                    item.product_type.update_stock(item.weight_kg)

    def total_price(self):
        return sum(item.total_price() for item in self.orderitem_set.all())

    def __str__(self):
        return f"Bestellung #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_weight = self.weight_kg if self.pk else 0

    def clean(self):
        if self.weight_kg > self.product_type.current_stock_kg + (self.original_weight if self.pk else 0):
            raise ValidationError(
                f"Nicht genug Lagerbestand. Verfügbar: {self.product_type.current_stock_kg} kg"
            )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                weight_diff = self.original_weight - self.weight_kg
                self.product_type.update_stock(weight_diff)
            else:
                if self.order.status == 'pending':
                    self.product_type.update_stock(-self.weight_kg)
            super().save(*args, **kwargs)
            self.original_weight = self.weight_kg

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.order.status != 'completed':
                self.product_type.update_stock(self.weight_kg)
            super().delete(*args, **kwargs)

    def total_price(self):
        return self.weight_kg * self.product_type.price_per_kg

    def __str__(self):
        return f"{self.product_type} - {self.weight_kg} kg"