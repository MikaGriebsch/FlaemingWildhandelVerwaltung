from django.contrib import admin
from .models import *

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ['product_type']
    min_num = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_kg', 'current_stock_kg')
    list_editable = ('current_stock_kg',)
    list_filter = ('category',)
    search_fields = ['name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'order_date', 'status', 'stock_status')
    inlines = [OrderItemInline]
    actions = ['complete_orders', 'delete_selected']

    def delete_model(self, request, obj):
        obj.delete()

    def delete_queryset(self, request, queryset):
        for order in queryset:
            order.delete()

    def stock_status(self, obj):
        for item in obj.orderitem_set.all():
            if item.weight_kg > item.product_type.current_stock_kg:
                return "⚠️ Nicht genug Lagerbestand"
        return "✔️ Verfügbar"
    stock_status.short_description = 'Lagerstatus'

    def complete_orders(self, request, queryset):
        for order in queryset:
            order.status = 'completed'
            order.save()
    complete_orders.short_description = "Markierte Bestellungen abschließen"