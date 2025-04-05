from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('oldorders/', views.old_order_list, name='old_order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('home/', views.home, name='home'),
    
    # AJAX-URLs für Orderitems
    path('orderitem/<int:item_id>/update/', views.update_order_item, name='update_order_item'),
    path('orderitem/<int:item_id>/delete/', views.delete_order_item, name='delete_order_item'),
    path('orderitem/<int:item_id>/toggle/', views.toggle_order_item, name='toggle_order_item'),
    
    # Neue URLs für Order-Updates
    path('orders/<int:order_id>/update-delivery-date/', views.update_order_delivery_date, name='update_order_delivery_date'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
]