from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem
from django.utils import timezone
from datetime import datetime
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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
    open_orders_count = Order.objects.filter(status='pending').count()

    today = timezone.now().date()
    completed_today_count = Order.objects.filter(
        status='completed',
        order_date__date=today
    ).count()

    pending_orders = Order.objects.filter(status='pending')

    calendar_events = []
    for order in pending_orders:
        event_date = order.delivery_date if order.delivery_date else order.order_date
        
        calendar_events.append({
            'id': order.id,
            'title': order.customer_name,
            'start': event_date.strftime('%Y-%m-%d'),
            'backgroundColor': '#A8B400' if order.delivery_date else '#256238',
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

@require_POST
def update_order_item(request, item_id):
    """AJAX-View zum Aktualisieren eines OrderItems"""
    try:
        data = json.loads(request.body)
        order_item = get_object_or_404(OrderItem, pk=item_id)
        
        # Gewicht aktualisieren
        new_weight = Decimal(data.get('weight_kg'))
        order_item.weight_kg = new_weight
        order_item.save()
        
        # Aktualisierte Daten zurückgeben
        return JsonResponse({
            'success': True,
            'total_price': f"{order_item.order.total_price():.2f}"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def delete_order_item(request, item_id):
    """AJAX-View zum Löschen eines OrderItems"""
    try:
        order_item = get_object_or_404(OrderItem, pk=item_id)
        order = order_item.order
        order_item.delete()
        
        return JsonResponse({
            'success': True,
            'total_price': f"{order.total_price():.2f}"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def toggle_order_item(request, item_id):
    """AJAX-View zum Abhaken eines OrderItems"""
    try:
        data = json.loads(request.body)
        order_item = get_object_or_404(OrderItem, pk=item_id)
        
        # Status aktualisieren
        order_item.completed = data.get('completed', False)
        order_item.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def update_order_delivery_date(request, order_id):
    """AJAX-View zum Aktualisieren des Liefertermins einer Bestellung"""
    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, pk=order_id)
        
        delivery_date = data.get('delivery_date')
        
        # Wenn das Datum leer ist, auf None setzen
        if not delivery_date or delivery_date == '':
            order.delivery_date = None
            formatted_date = None
        else:
            # Datum parsen und speichern
            order.delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
            formatted_date = order.delivery_date.strftime('%d.%m.%Y')
            
        order.save()
        
        return JsonResponse({
            'success': True,
            'formatted_date': formatted_date
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def update_order_status(request, order_id):
    """AJAX-View zum Aktualisieren des Status einer Bestellung"""
    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, pk=order_id)
        
        # Status aktualisieren
        new_status = data.get('status')
        
        # Überprüfen, ob genügend Lagerbestand für den Status "completed" vorhanden ist
        if new_status == 'completed':
            for item in order.orderitem_set.all():
                if item.weight_kg > item.product_type.current_stock_kg:
                    return JsonResponse({
                        'success': False,
                        'error': f'Nicht genug Lagerbestand für {item.product_type}.'
                    })
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Status-Anzeigenamen bekommen
        status_display = dict(Order.STATUS_CHOICES)[new_status]
        
        return JsonResponse({
            'success': True,
            'status_display': status_display
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})