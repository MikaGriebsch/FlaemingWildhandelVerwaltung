from django.shortcuts import render, get_object_or_404
from .models import Order

def order_list(request):
    orders = Order.objects.filter(status='pending').order_by('-order_date')
    return render(request, 'order_list.html', {'orders': orders})

def old_order_list(request):
    orders = Order.objects.filter(status='completed').order_by('-order_date')
    return render(request, 'old_order_list.html', {'orders': orders})
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order_detail.html', {'order': order})