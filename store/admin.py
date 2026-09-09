from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Category, Product, Cart, CartItem, Order, OrderItem


# --- Users ---
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    date_hierarchy = 'date_joined'


# --- Categories ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


# --- Products ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_featured', 'is_in_stock', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity', 'is_featured', 'category')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20

    def is_in_stock(self, obj):
        return obj.is_in_stock
    is_in_stock.boolean = True
    is_in_stock.short_description = 'In Stock'


# --- Cart ---
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_item_count', 'total_price', 'created_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'

    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'


# --- Cart Items ---
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('product__name', 'cart__user__username')
    raw_id_fields = ('cart', 'product')


# --- Orders ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at', 'get_item_count')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'user', 'total_price',
                       'shipping_address', 'phone_number')
    list_editable = ('status',)
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'

    def has_add_permission(self, request):
        return False


# --- Order Items ---
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity', 'get_total_price')
    list_filter = ('order__created_at',)
    search_fields = ('order__id', 'product__name')
    raw_id_fields = ('order', 'product')

    def get_total_price(self, obj):
        return obj.get_total_price
    get_total_price.short_description = 'Total'
