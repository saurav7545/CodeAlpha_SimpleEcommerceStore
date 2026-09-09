from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand

from products.models import Category, Product


PRODUCTS = {
    'Electronics': [
        ('Noise-Cancelling Wireless Headphones', 'Comfortable wireless headphones with rich sound and long battery life.', '2999.00', 25),
        ('Smart Fitness Band', 'Track daily activity, sleep, heart rate, and notifications.', '1499.00', 40),
        ('Fast Charging Power Bank 20000mAh', 'High-capacity dual-port power bank for phones and tablets.', '2199.00', 30),
        ('Mechanical Keyboard', 'Compact mechanical keyboard with comfortable tactile keys.', '3499.00', 16),
        ('Bluetooth Speaker', 'Portable speaker with deep bass and all-day battery.', '1899.00', 28),
    ],
    'Home & Kitchen': [
        ('Insulated Stainless Steel Bottle', '750 ml leak-proof bottle that keeps drinks hot or cold.', '699.00', 50),
        ('Non-Stick Fry Pan', 'Durable 24 cm non-stick pan for everyday Indian cooking.', '1199.00', 18),
        ('LED Table Lamp', 'Dimmable study lamp with a modern compact design.', '899.00', 22),
        ('Coffee Maker', 'Easy-to-use coffee maker for a fresh morning brew.', '2799.00', 12),
    ],
    'Fashion': [
        ('Classic Cotton T-Shirt', 'Soft regular-fit cotton t-shirt for everyday wear.', '599.00', 60),
        ('Urban Backpack', 'Water-resistant backpack with padded laptop compartment.', '1799.00', 20),
    ],
    'Books': [
        ('Python Programming Book', 'A practical beginner-friendly guide to Python programming.', '799.00', 35),
    ],
    'Sports': [
        ('Sports Water Bottle', 'Lightweight 1 litre bottle for workouts and travel.', '499.00', 45),
    ],
    'Accessories': [
        ('Wireless Mouse', 'Reliable ergonomic wireless mouse for work and study.', '999.00', 38),
    ],
}


class Command(BaseCommand):
    help = 'Create starter ShopSphere products priced in Indian rupees.'

    def handle(self, *args, **options):
        created_count = 0
        for category_name, products in PRODUCTS.items():
            category, _ = Category.objects.get_or_create(name=category_name)
            for name, description, price, stock in products:
                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'description': description,
                        'price': Decimal(price),
                        'stock': stock,
                        'is_available': True,
                    },
                )
                if created:
                    created_count += 1
                elif product.category_id != category.id:
                    product.category = category
                    product.save(update_fields=['category'])
        self.stdout.write(self.style.SUCCESS(f'Store seed complete: {created_count} products created.'))
        call_command('create_catalogue_images')
        call_command('assign_real_images')
