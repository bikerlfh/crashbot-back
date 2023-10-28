from cacheops.invalidation import invalidate_model
from django.contrib import admin


class ModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        invalidate_model(self.model)
        return super().save_model(request, obj, form, change)
