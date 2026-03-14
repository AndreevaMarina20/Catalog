from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import Product, Animal, Category

def index(request):
    # Получаем параметры фильтрации из GET-запроса
    animal_id = request.GET.get('animal')
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', 'default')
    
    # Базовый запрос всех товаров
    products = Product.objects.all().select_related('animal', 'category')
    
    # Применяем фильтры если они есть
    if animal_id and animal_id != 'all':
        products = products.filter(animal_id=animal_id)
    
    if category_id and category_id != 'all':
        products = products.filter(category_id=category_id)
    
    # Применяем сортировку
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    
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
            continue
    
    context = {
        'products': products,
        'animals': animals,
        'categories': categories,
        'cart': cart_items,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'selected_animal': animal_id,
        'selected_category': category_id,
        'sort_by': sort_by,
    }
    
    return render(request, 'catalog/index.html', context)


def product_detail(request, product_id):
    """Страница детального просмотра товара"""
    product = Product.objects.get(id=product_id)
    
    # Корзина
    cart_data = request.session.get('cart', [])
    cart_items = []
    cart_count = 0
    cart_total = 0
    
    for item in cart_data:
        try:
            p = Product.objects.get(id=item['id'])
            cart_items.append({
                'id': p.id,
                'product': p,
                'quantity': item['quantity']
            })
            cart_count += item['quantity']
            cart_total += p.price * item['quantity']
        except Product.DoesNotExist:
            continue
    
    context = {
        'product': product,
        'cart': cart_items,
        'cart_count': cart_count,
        'cart_total': cart_total,
    }
    
    return render(request, 'catalog/product_detail.html', context)


def add_to_cart(request, product_id):
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
    
    # Подсчитываем общее количество товаров
    cart_count = sum(item['quantity'] for item in cart)
    
    # Если это AJAX-запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart_count
        })
    
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


def get_cart_items(request):
    """Возвращает список ID товаров в корзине"""
    cart = request.session.get('cart', [])
    return JsonResponse({
        'items': [{'id': item['id'], 'quantity': item['quantity']} for item in cart]
    })


# ========== НОВЫЕ ФУНКЦИИ ==========

def checkout(request):
    """Страница оформления заказа"""
    # Корзина
    cart_data = request.session.get('cart', [])
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
            continue
    
    context = {
        'cart': cart_items,
        'cart_count': cart_count,
        'cart_total': cart_total,
    }
    
    return render(request, 'catalog/checkout.html', context)


def place_order(request):
    """Обработка отправки заказа"""
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        # Считаем сумму заказа ДО очистки корзины
        cart_data = request.session.get('cart', [])
        total = 0
        for item in cart_data:
            try:
                product = Product.objects.get(id=item['id'])
                total += product.price * item['quantity']
            except Product.DoesNotExist:
                continue
        
        # Очищаем корзину
        request.session['cart'] = []
        request.session.modified = True
        
        # Сохраняем данные о заказе
        request.session['order_placed'] = True
        request.session['order_details'] = {
            'name': name,
            'total': total,
        }
        
        return redirect('order_success')
    
    return redirect('index')


def order_success(request):
    """Страница успешного оформления заказа"""
    # Проверяем, был ли заказ оформлен
    if not request.session.get('order_placed'):
        return redirect('index')
    
    # Очищаем флаг
    order_details = request.session.get('order_details', {})
    request.session['order_placed'] = False
    request.session['order_details'] = {}
    
    context = {
        'name': order_details.get('name', 'Пользователь'),
        'total': order_details.get('total', 0),
    }
    
    return render(request, 'catalog/order_success.html', context)