from .models import Cart, CartItem


def cart_item_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            count = cart.items.count()
        except Cart.DoesNotExist:
            count = 0
    return {'cart_item_count': count}
