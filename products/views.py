from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Product


def home(request):
    available_products = Product.objects.filter(is_available=True, stock__gt=0)
    return render(request, 'home.html', {
        'featured_products': available_products[:8],
        'latest_products': available_products.order_by('-created_at')[:8],
        'popular_products': available_products.order_by('-stock')[:8],
        'categories': Category.objects.all(),
    })


def product_list(request, slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    selected_category = None
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'latest')

    if slug:
        selected_category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    sort_options = {
        'latest': '-created_at', 'price_asc': 'price', 'price_desc': '-price', 'name': 'name',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'categories': categories,
        'products': page_obj,
        'selected_category': selected_category,
        'query': query,
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


def error_404(request, exception):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)
