from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from .models import Category, Product


class CatalogueTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Testing')
        Product.objects.create(name='Alpha Mouse', category=category, description='wireless', price=Decimal('300.00'), stock=2)
        Product.objects.create(name='Bravo Keyboard', category=category, description='mechanical', price=Decimal('100.00'), stock=2)

    def test_search_category_and_sort(self):
        url = reverse('products:product_list')
        self.assertContains(self.client.get(url, {'q': 'wireless'}), 'Alpha Mouse')
        self.assertContains(self.client.get(reverse('products:product_list_by_category', args=['testing'])), 'Bravo Keyboard')
        response = self.client.get(url, {'sort': 'price_asc'})
        self.assertEqual(list(response.context['products'].object_list)[0].name, 'Bravo Keyboard')
