from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('api/cart/items/', views.get_cart_items, name='get_cart_items'),
]