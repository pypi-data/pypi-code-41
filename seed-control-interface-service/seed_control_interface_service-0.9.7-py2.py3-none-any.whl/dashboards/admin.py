from django.contrib import admin
from .models import Dashboard, Widget, WidgetData, UserDashboard, Definition


admin.site.register(Dashboard)
admin.site.register(Widget)
admin.site.register(WidgetData)
admin.site.register(UserDashboard)
admin.site.register(Definition)
