from django.shortcuts import render, get_object_or_404
from .models import Order
from django.utils import timezone
from datetime import datetime
import json

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
    
    # Kalenderdaten vorbereiten
    # Alle offenen Bestellungen für den Kalender holen
    pending_orders = Order.objects.filter(status='pending')
    
    # Kalenderdaten im FullCalendar-Format erstellen
    calendar_events = []
    for order in pending_orders:
        # Wenn ein Liefertermin festgelegt ist, verwende diesen, sonst das Bestelldatum
        event_date = order.delivery_date if order.delivery_date else order.order_date
        
        calendar_events.append({
            'id': order.id,
            'title': order.customer_name,  # Nur den Kundennamen anzeigen
            'start': event_date.strftime('%Y-%m-%d'),  # Nur das Datum verwenden
            'backgroundColor': '#A8B400' if order.delivery_date else '#256238',  # Farbunterscheidung
            'borderColor': '#A8B400' if order.delivery_date else '#256238',
            'extendedProps': {
                'hasDeliveryDate': bool(order.delivery_date)
            }
        })
    
    context = {
        'open_orders_count': open_orders_count,
        'completed_today_count': completed_today_count,
        'calendar_events': json.dumps(calendar_events)
    }
    
    return render(request, 'home.html', context)