from django.shortcuts import render, get_object_or_404
from .models import Order
from django.utils import timezone
from datetime import datetime

def order_list(request):
    orders = Order.objects.filter(status='pending').order_by('-order_date')
    return render(request, 'order_list.html', {'orders': orders})

def old_order_list(request):
    orders = Order.objects.filter(status='completed').order_by('-order_date')
    return render(request, 'old_order_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order_detail.html', {'order': order})

def home(request):
    # Anzahl offener Bestellungen
    open_orders_count = Order.objects.filter(status='pending').count()
    
    # Anzahl heute abgeschlossener Bestellungen
    today = timezone.now().date()
    completed_today_count = Order.objects.filter(
        status='completed',
        order_date__date=today
    ).count()
    
    context = {
        'open_orders_count': open_orders_count,
        'completed_today_count': completed_today_count,
    }
    
    return render(request, 'home.html', context)