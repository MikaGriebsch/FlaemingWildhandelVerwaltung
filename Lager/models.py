from django.db import models
from django.core.exceptions import ValidationError


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

    def __str__(self):
        return f"{self.category} - {self.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ausstehend'),
        ('completed', 'Abgeschlossen'),
    ]
    customer_name = models.CharField(max_length=100)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def clean(self):
        if self.status == 'completed':
            for item in self.orderitem_set.all():
                if item.weight_kg > item.product_type.current_stock_kg:
                    raise ValidationError(
                        f"Nicht genug Lagerbestand für {item.product_type} "
                        f"(Verfügbar: {item.product_type.current_stock_kg} kg)"
                    )

    def save(self, *args, **kwargs):
        if self.status == 'completed':
            # Lagerbestand aktualisieren
            for item in self.orderitem_set.all():
                item.product_type.current_stock_kg -= item.weight_kg
                item.product_type.save()
        super().save(*args, **kwargs)

    def total_price(self):
        return sum(item.total_price() for item in self.orderitem_set.all())

    def __str__(self):
        return f"Bestellung #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.weight_kg > self.product_type.current_stock_kg:
            raise ValidationError(
                f"Nicht genug Lagerbestand. Verfügbar: {self.product_type.current_stock_kg} kg"
            )

    def total_price(self):
        return self.weight_kg * self.product_type.price_per_kg

    def __str__(self):
        return f"{self.product_type} - {self.weight_kg} kg"