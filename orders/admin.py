from django.contrib import admin
from .models import Order, OrderItem, OrderTrackingEvent


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity', 'get_total_price')
    can_delete = False


class OrderTrackingEventInline(admin.TabularInline):
    model = OrderTrackingEvent
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('id', 'user__username', 'email', 'full_name')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    list_select_related = ('user',)
    inlines = (OrderItemInline, OrderTrackingEventInline)

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = Order.objects.get(pk=obj.pk).status
        super().save_model(request, obj, form, change)
        if change and previous_status != obj.status:
            OrderTrackingEvent.objects.create(
                order=obj, status=obj.status,
                message=f'Order status updated to {obj.get_status_display()}.',
            )


@admin.register(OrderTrackingEvent)
class OrderTrackingEventAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'message', 'location', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'message', 'location')
