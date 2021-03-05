from django.contrib import admin

from .models import Item

class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "upc", "quantity", "weight", "date")

admin.site.register(Item, ItemAdmin)
