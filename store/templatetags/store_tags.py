from django import template

register = template.Library()

@register.filter(name='cart_item_count')
def cart_item_count(user):
    if user.is_authenticated:
        return user.cart_items.count()
    return 0

@register.filter(name='cart_total_quantity')
def cart_total_quantity(user):
    if user.is_authenticated:
        total = sum(item.quantity for item in user.cart_items.all())
        return total
    return 0
