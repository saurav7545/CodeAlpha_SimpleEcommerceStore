from .models import Category


def navigation_categories(request):
    return {'nav_categories': Category.objects.all()}
