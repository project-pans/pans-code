from django.contrib import admin

from .models import Item

class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "upc", "quantity", "percent", "date", "weight_num")

admin.site.register(Item, ItemAdmin)
