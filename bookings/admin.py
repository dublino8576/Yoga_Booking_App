from django.contrib import admin
from .models import Booking
# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "yoga_class", "status", "created_at", "amount_paid", "currency")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("user__username", "user__email", "yoga_class__slug", "stripe_checkout_id")
    ordering = ("-created_at",)

    # Make object detail page read-only
    readonly_fields = (
        "user",
        "yoga_class",
        "status",
        "created_at",
        "cancelled_at",
        "stripe_payment_intent",
        "stripe_checkout_id",
        "amount_paid",
        "currency",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False