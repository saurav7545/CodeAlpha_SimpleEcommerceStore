from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q

from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import RegistrationForm, CheckoutForm


def home(request):
    featured_products = Product.objects.filter(is_featured=True, stock_quantity__gt=0)
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    selected_category = None
    query = ""

    category_slug = request.GET.get('category')
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


def _get_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = _get_cart(request.user)
    return render(request, 'cart.html', {'cart': cart})


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart = _get_cart(request.user)

    requested_qty = int(request.POST.get('quantity', 1))
    total_qty = requested_qty

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 0}
    )

    if cart_item.quantity + total_qty > product.stock_quantity:
        error_msg = f'Sorry, only {product.stock_quantity} item(s) of {product.name} in stock'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        messages.error(request, error_msg)
    else:
        cart_item.quantity += total_qty
        cart_item.save()
        success_msg = f'{product.name} added to cart'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'cart_count': cart.items.count(),
            })
        messages.success(request, success_msg)

    return redirect('cart_detail')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('cart_detail')


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product = cart_item.product

    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock_quantity:
        error_msg = f'Sorry, only {product.stock_quantity} item(s) in stock'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': error_msg,
                'item_total': cart_item.get_total_price,
                'cart_total': cart_item.cart.total_price,
            })
        messages.error(request, error_msg)
    elif quantity < 1:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Quantity must be at least 1',
                'item_total': cart_item.get_total_price,
                'cart_total': cart_item.cart.total_price,
            })
        messages.error(request, 'Quantity must be at least 1')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cart updated',
                'item_id': cart_item.id,
                'item_total': float(cart_item.get_total_price),
                'cart_total': float(cart_item.cart.total_price),
            })
        messages.success(request, 'Cart updated')

    return redirect('cart_detail')


@login_required
def checkout(request):
    cart = _get_cart(request.user)
    cart_items = cart.items.select_related('product').all()

    if not cart_items:
        messages.info(request, 'Your cart is empty')
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            insufficient_stock = False
            for item in cart_items:
                if item.quantity > item.product.stock_quantity:
                    messages.error(
                        request,
                        f'Sorry, only {item.product.stock_quantity} '
                        f'item(s) of {item.product.name} in stock'
                    )
                    insufficient_stock = True
                    break

            if insufficient_stock:
                return redirect('checkout')

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    total_price=cart.total_price,
                    shipping_address=form.cleaned_data['shipping_address'],
                    phone_number=form.cleaned_data['phone_number'],
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.price,
                        quantity=item.quantity
                    )
                    item.product.stock_quantity -= item.quantity
                    item.product.save()

                cart.items.all().delete()

            messages.success(request, 'Order placed successfully!')
            return redirect('order_success', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'form': form,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = request.user.orders.all()
    return render(request, 'orders.html', {'orders': orders})


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back!')

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('home')
