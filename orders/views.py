from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from cart.models import Cart, CartItem
from .models import Order, OrderItem, OrderTrackingEvent
from .forms import CheckoutForm


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.info(request, 'Your cart is empty')
        return redirect('cart:cart_detail')

    cart_items = cart.items.select_related('product').all()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                locked_items = list(
                    CartItem.objects.select_for_update().select_related('product')
                    .filter(cart=cart)
                )
                if not locked_items:
                    messages.info(request, 'Your cart is empty')
                    return redirect('cart:cart_detail')
                for item in locked_items:
                    if item.quantity > item.product.stock or not item.product.is_available:
                        messages.error(request, f'{item.product.name} is no longer available in the requested quantity.')
                        return redirect('orders:checkout')
                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data['full_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    postal_code=form.cleaned_data['postal_code'],
                    total_amount=sum(item.get_total_price for item in locked_items),
                    expected_delivery=timezone.localdate() + timedelta(days=5),
                )

                OrderTrackingEvent.objects.create(
                    order=order, status=Order.STATUS_PENDING,
                    message='Order placed successfully. We are confirming your items.',
                )

                for item in locked_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.price,
                        quantity=item.quantity
                    )
                    item.product.stock -= item.quantity
                    item.product.save()

                CartItem.objects.filter(pk__in=[item.pk for item in locked_items]).delete()

            messages.success(request, 'Order placed successfully!')
            return redirect('orders:order_success', order_id=order.id)
    else:
        # Pre-fill form with user profile data if available
        initial_data = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial_data = {
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': profile.phone,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'postal_code': profile.postal_code,
            }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'form': form,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = request.user.orders.all()
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_tracking.html', {'order': order})
