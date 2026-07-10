from django.contrib import admin

from mainapp.models import Order, PricingSettings, Product


@admin.register(PricingSettings)
class PricingSettingsAdmin(admin.ModelAdmin):
    list_display = ("base_box_price", "private_college_extra", "lab_coat_price", "updated_at")

    def has_add_permission(self, request):
        return not PricingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock")
    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "customer_mobile",
        "college_type",
        "includes_lab_coat",
        "total_amount",
        "status",
        "bill_reference",
        "paymob_order_id",
        "created_at",
    )
    list_filter = ("status", "college_type", "includes_lab_coat", "created_at")
    search_fields = ("customer_name", "customer_mobile", "customer_email", "bill_reference", "paymob_order_id")
    readonly_fields = ("paymob_order_id", "bill_reference", "paid_at")
