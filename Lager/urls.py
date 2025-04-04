from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('oldorders/', views.old_order_list, name='old_order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]