from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem


def _get_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = _get_cart(request.user)
    return render(request, 'cart/cart.html', {'cart': cart})


@login_required
@require_POST
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    cart = _get_cart(request.user)

    try:
        requested_qty = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        requested_qty = 0

    if requested_qty < 1:
        messages.error(request, 'Quantity must be at least 1')
        return redirect('products:product_detail', slug=slug)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 0}
    )

    if cart_item.quantity + requested_qty > product.stock:
        error_msg = f'Sorry, only {product.stock} item(s) of {product.name} in stock'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        messages.error(request, error_msg)
    else:
        cart_item.quantity += requested_qty
        cart_item.save()
        success_msg = f'{product.name} added to cart'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'cart_count': cart.total_items,
            })
        messages.success(request, success_msg)

    return redirect('cart:cart_detail')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('cart:cart_detail')


@login_required
@require_POST
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product = cart_item.product

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 0

    if quantity > product.stock:
        error_msg = f'Sorry, only {product.stock} item(s) in stock'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': error_msg,
                'item_total': str(cart_item.get_total_price),
                'cart_total': str(cart_item.cart.total_price),
            })
        messages.error(request, error_msg)
    elif quantity < 1:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Quantity must be at least 1',
                'item_total': str(cart_item.get_total_price),
                'cart_total': str(cart_item.cart.total_price),
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
                'item_total': str(cart_item.get_total_price),
                'cart_total': str(cart_item.cart.total_price),
            })
        messages.success(request, 'Cart updated')

    return redirect('cart:cart_detail')


@login_required
@require_POST
def clear_cart(request):
    cart = _get_cart(request.user)
    cart.items.all().delete()
    messages.success(request, 'Your cart has been cleared')
    return redirect('cart:cart_detail')
