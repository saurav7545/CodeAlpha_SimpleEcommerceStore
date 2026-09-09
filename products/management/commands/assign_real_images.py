from django.core.management.base import BaseCommand

from products.models import Product


IMAGE_MAP = {
    'Noise-Cancelling Wireless Headphones': 'headphones.jpg',
    'Smart Fitness Band': 'smartwatch.jpg',
    'Mechanical Keyboard': 'keyboard.jpg',
    'Bluetooth Speaker': 'speaker.jpg',
    'Classic Cotton T-Shirt': 'tshirt.jpg',
    'Urban Backpack': 'backpack.jpg',
    'LED Table Lamp': 'lamp.jpg',
    'Python Programming Book': 'book.jpg',
    'Insulated Stainless Steel Bottle': 'bottle.jpg',
    'Sports Water Bottle': 'bottle.jpg',
    'Wireless Mouse': 'mouse.jpg',
    'Fast Charging Power Bank 20000mAh': 'mouse.jpg',
    'Non-Stick Fry Pan': 'lamp.jpg',
    'Coffee Maker': 'lamp.jpg',
}


class Command(BaseCommand):
    help = 'Assign locally stored real catalogue photos to seeded ShopSphere products.'

    def handle(self, *args, **options):
        updated = 0
        for product_name, image_name in IMAGE_MAP.items():
            product = Product.objects.filter(name=product_name).first()
            if product:
                product.image.name = f'products/real/{image_name}'
                product.save(update_fields=['image'])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Assigned real local photos to {updated} products.'))
