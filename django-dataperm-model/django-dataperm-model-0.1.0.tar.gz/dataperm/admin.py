from django.contrib import admin


class WithOwnerMixin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if not change and not obj.owner:
            obj.owner = request.user.username
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(owner=request.user.username)
