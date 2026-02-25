# catalog/views.py

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product, Animal, Category

def index(request):
    # Получаем параметры фильтрации из GET-запроса
    animal_id = request.GET.get('animal')
    category_id = request.GET.get('category')
    
    # Базовый запрос всех товаров
    products = Product.objects.all().select_related('animal', 'category')
    
    # Применяем фильтры если они есть
    if animal_id and animal_id != 'all':
        products = products.filter(animal_id=animal_id)
    
    if category_id and category_id != 'all':
        products = products.filter(category_id=category_id)
    
    # Получаем все категории и животных для фильтров
    animals = Animal.objects.all()
    categories = Category.objects.all()
    
    # Корзина хранится в сессии
    cart_data = request.session.get('cart', [])
    
    # Получаем полные объекты товаров для корзины
    cart_items = []
    cart_count = 0
    cart_total = 0
    
    for item in cart_data:
        try:
            product = Product.objects.get(id=item['id'])
            cart_items.append({
                'id': product.id,
                'product': product,
                'quantity': item['quantity']
            })
            cart_count += item['quantity']
            cart_total += product.price * item['quantity']
        except Product.DoesNotExist:
            continue  # Если товар удален из базы, пропускаем
    
    context = {
        'products': products,
        'animals': animals,
        'categories': categories,
        'cart': cart_items,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'selected_animal': animal_id,
        'selected_category': category_id,
    }
    
    return render(request, 'catalog/index.html', context)

def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    cart = request.session.get('cart', [])
    
    # Проверяем, есть ли уже такой товар
    found = False
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            found = True
            break
    
    if not found:
        cart.append({
            'id': product_id,
            'quantity': 1
        })
    
    request.session['cart'] = cart
    request.session.modified = True
    
    # Возвращаемся туда, откуда пришли
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def remove_from_cart(request, product_id):
    """Удаление товара из корзины"""
    cart = request.session.get('cart', [])
    
    # Удаляем товар
    cart = [item for item in cart if item['id'] != product_id]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def clear_cart(request):
    """Очистка корзины"""
    request.session['cart'] = []
    request.session.modified = True
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))