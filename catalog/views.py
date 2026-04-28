from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import Product, Animal, Category

def index(request):
    animal_id = request.GET.get('animal')
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', 'default')
    search_query = request.GET.get('search', '')
    
    products = list(Product.objects.all().select_related('animal', 'category'))
    
    if search_query:
        products = [p for p in products if search_query.lower() in p.name.lower()]
    
    if animal_id and animal_id != 'all':
        products = [p for p in products if str(p.animal.id) == animal_id]
    
    if category_id and category_id != 'all':
        products = [p for p in products if str(p.category.id) == category_id]
    
    if sort_by == 'price_asc':
        products.sort(key=lambda x: x.price)
    elif sort_by == 'price_desc':
        products.sort(key=lambda x: x.price, reverse=True)
    elif sort_by == 'name_asc':
        products.sort(key=lambda x: x.name)
    elif sort_by == 'name_desc':
        products.sort(key=lambda x: x.name, reverse=True)
    
    animals = Animal.objects.all()
    categories = Category.objects.all()
    
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
        'products': products,
        'animals': animals,
        'categories': categories,
        'cart': cart_items,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'selected_animal': animal_id,
        'selected_category': category_id,
        'sort_by': sort_by,
        'search_query': search_query,
    }
    
    return render(request, 'catalog/index.html', context)


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    
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
    
    cart_count = sum(item['quantity'] for item in cart)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart_count
        })
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', [])
    
    cart = [item for item in cart if item['id'] != product_id]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def clear_cart(request):
    request.session['cart'] = []
    request.session.modified = True
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def get_cart_items(request):
    cart = request.session.get('cart', [])
    return JsonResponse({
        'items': [{'id': item['id'], 'quantity': item['quantity']} for item in cart]
    })


def checkout(request):
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
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        cart_data = request.session.get('cart', [])
        total = 0
        for item in cart_data:
            try:
                product = Product.objects.get(id=item['id'])
                total += product.price * item['quantity']
            except Product.DoesNotExist:
                continue
        
        request.session['cart'] = []
        request.session.modified = True
        
        request.session['order_placed'] = True
        request.session['order_details'] = {
            'name': name,
            'total': total,
        }
        
        return redirect('order_success')
    
    return redirect('index')


def order_success(request):
    if not request.session.get('order_placed'):
        return redirect('index')
    
    order_details = request.session.get('order_details', {})
    request.session['order_placed'] = False
    request.session['order_details'] = {}
    
    context = {
        'name': order_details.get('name', 'Пользователь'),
        'total': order_details.get('total', 0),
    }
    
    return render(request, 'catalog/order_success.html', context)