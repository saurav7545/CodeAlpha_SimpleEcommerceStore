from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import UserProfile
from orders.models import Order, OrderItem, OrderTrackingEvent
from products.models import Product


class Command(BaseCommand):
    help = 'Create a safe local ShopSphere demo customer, orders, and tracking history.'

    def handle(self, *args, **options):
        call_command('seed_store')
        user, created = User.objects.get_or_create(
            username='demo_customer',
            defaults={
                'first_name': 'Demo', 'last_name': 'Customer', 'email': 'demo@shopsphere.local',
            },
        )
        if created:
            user.set_password('DemoPass123!')
            user.save()
        UserProfile.objects.get_or_create(
            user=user,
            defaults={'phone': '9876543210', 'address': '21 Demo Street', 'city': 'Mumbai', 'state': 'Maharashtra', 'postal_code': '400001'},
        )
        products = list(Product.objects.filter(is_available=True, stock__gt=0)[:3])
        if len(products) < 3:
            self.stdout.write(self.style.ERROR('At least three products are required for the demo.'))
            return
        if not Order.objects.filter(user=user).exists():
            delivered = self.create_order(user, products[:2], Order.STATUS_DELIVERED, -6)
            self.create_event(delivered, Order.STATUS_PENDING, 'Order placed successfully.')
            self.create_event(delivered, Order.STATUS_PROCESSING, 'Items packed and ready for dispatch.')
            self.create_event(delivered, Order.STATUS_SHIPPED, 'Package shipped from Mumbai fulfilment centre.', 'Mumbai')
            self.create_event(delivered, Order.STATUS_DELIVERED, 'Package delivered successfully.', 'Mumbai')
            shipped = self.create_order(user, [products[2]], Order.STATUS_SHIPPED, -1)
            self.create_event(shipped, Order.STATUS_PENDING, 'Order placed successfully.')
            self.create_event(shipped, Order.STATUS_PROCESSING, 'Items packed and ready for dispatch.')
            self.create_event(shipped, Order.STATUS_SHIPPED, 'Package is on the way.', 'Mumbai')
        self.stdout.write(self.style.SUCCESS('Demo ready. Login: demo_customer / DemoPass123!'))

    def create_order(self, user, products, status, days_offset):
        total = sum((product.price for product in products), Decimal('0'))
        order = Order.objects.create(
            user=user, full_name='Demo Customer', email=user.email, phone='9876543210',
            address='21 Demo Street', city='Mumbai', state='Maharashtra', postal_code='400001',
            total_amount=total, status=status,
            expected_delivery=timezone.localdate() + timedelta(days=3),
        )
        for product in products:
            OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)
        return order

    @staticmethod
    def create_event(order, status, message, location=''):
        OrderTrackingEvent.objects.create(order=order, status=status, message=message, location=location)
