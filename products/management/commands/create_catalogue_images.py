from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from products.models import Product


PALETTES = [
    ('#181B2F', '#7367F0'), ('#073B4C', '#06D6A0'), ('#4A1942', '#E76F51'),
    ('#244B36', '#A7C957'), ('#3D405B', '#F2CC8F'), ('#264653', '#E9C46A'),
    ('#6D2E46', '#F4A261'), ('#1D3557', '#A8DADC'),
]


class Command(BaseCommand):
    help = 'Create and attach polished local PNG catalogue images for products without images.'

    def handle(self, *args, **options):
        font = ImageFont.load_default()
        created = 0
        for index, product in enumerate(Product.objects.filter(image='').order_by('id')):
            background, accent = PALETTES[index % len(PALETTES)]
            canvas = Image.new('RGB', (900, 900), background)
            draw = ImageDraw.Draw(canvas)
            # Soft concentric backdrop and a simple product-style silhouette.
            draw.ellipse((110, 90, 790, 770), fill=accent)
            draw.ellipse((165, 145, 735, 715), fill=background)
            self.draw_silhouette(draw, product.name, accent)
            draw.rounded_rectangle((55, 700, 845, 845), radius=24, fill='#FFFFFF')
            draw.text((88, 735), product.name[:44], fill=background, font=font)
            draw.text((88, 785), product.category.name.upper(), fill='#555555', font=font)
            image_bytes = BytesIO()
            canvas.save(image_bytes, format='PNG', optimize=True)
            filename = f'products/{product.slug}-catalogue.png'
            product.image.save(filename, ContentFile(image_bytes.getvalue()), save=True)
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Created and attached {created} local catalogue images.'))

    @staticmethod
    def draw_silhouette(draw, name, accent):
        name = name.lower()
        if 'headphone' in name:
            draw.arc((260, 205, 640, 585), 185, 355, fill=accent, width=44)
            draw.rounded_rectangle((225, 485, 330, 650), radius=42, fill=accent)
            draw.rounded_rectangle((570, 485, 675, 650), radius=42, fill=accent)
        elif 'band' in name:
            draw.rounded_rectangle((375, 220, 525, 675), radius=70, outline=accent, width=48)
            draw.rounded_rectangle((350, 360, 550, 535), radius=36, fill=accent)
        elif 'bottle' in name:
            draw.rounded_rectangle((350, 230, 550, 660), radius=80, fill=accent)
            draw.rounded_rectangle((395, 180, 505, 270), radius=18, fill=accent)
        elif 'backpack' in name:
            draw.rounded_rectangle((280, 280, 620, 665), radius=70, fill=accent)
            draw.arc((340, 195, 560, 395), 180, 355, fill=accent, width=38)
            draw.rounded_rectangle((335, 465, 565, 550), radius=22, outline='#FFFFFF', width=12)
        elif 't-shirt' in name:
            draw.polygon([(300, 290), (405, 215), (495, 215), (600, 290), (545, 390), (525, 665), (375, 665), (355, 390)], fill=accent)
        elif 'lamp' in name:
            draw.polygon([(280, 350), (620, 350), (545, 210), (355, 210)], fill=accent)
            draw.line((450, 350, 450, 635), fill=accent, width=36)
            draw.ellipse((330, 610, 570, 680), fill=accent)
        else:
            draw.rounded_rectangle((270, 300, 630, 630), radius=55, fill=accent)
