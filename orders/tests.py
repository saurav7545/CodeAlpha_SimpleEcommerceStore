from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cart.models import Cart, CartItem
from products.models import Category, Product
from .models import Order, OrderTrackingEvent


class StoreFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='shopper', password='safe-pass-123')
        self.other_user = User.objects.create_user(username='other', password='safe-pass-123')
        category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Wireless Mouse', category=category, description='A useful mouse.',
            price=Decimal('24.99'), stock=4,
        )

    def test_add_to_cart_enforces_stock(self):
        self.client.login(username='shopper', password='safe-pass-123')
        add_url = reverse('cart:add_to_cart', args=[self.product.slug])
        self.client.post(add_url, {'quantity': 2})
        self.client.post(add_url, {'quantity': 3})
        item = CartItem.objects.get(cart__user=self.user, product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_checkout_creates_order_reduces_stock_and_clears_cart(self):
        self.client.login(username='shopper', password='safe-pass-123')
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        response = self.client.post(reverse('orders:checkout'), {
            'full_name': 'Test Shopper', 'email': 'shopper@example.com', 'phone': '1234567890',
            'address': '1 Test Street', 'city': 'Testville', 'state': 'Test State', 'postal_code': '12345',
        })
        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse('orders:order_success', args=[order.id]))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)
        self.assertFalse(cart.items.exists())
        self.assertEqual(order.total_amount, Decimal('49.98'))

    def test_order_detail_is_private(self):
        order = Order.objects.create(
            user=self.user, full_name='Test Shopper', email='shopper@example.com', phone='1',
            address='Address', city='City', state='State', postal_code='12345', total_amount=Decimal('1.00'),
        )
        self.client.login(username='other', password='safe-pass-123')
        self.assertEqual(self.client.get(reverse('orders:order_detail', args=[order.id])).status_code, 404)

    def test_checkout_creates_initial_tracking_event(self):
        self.client.login(username='shopper', password='safe-pass-123')
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        self.client.post(reverse('orders:checkout'), {
            'full_name': 'Test Shopper', 'email': 'shopper@example.com', 'phone': '1234567890',
            'address': '1 Test Street', 'city': 'Testville', 'state': 'Test State', 'postal_code': '12345',
        })
        order = Order.objects.get(user=self.user)
        self.assertTrue(OrderTrackingEvent.objects.filter(order=order, status=Order.STATUS_PENDING).exists())
        self.assertEqual(self.client.get(reverse('orders:track_order', args=[order.id])).status_code, 200)
