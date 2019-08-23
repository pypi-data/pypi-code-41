"""
from finance import views
try:
    # django 2.0
    from django.urls import path
except:
    # django 1.6
    from django.conf.urls import url as path


urlpatterns = [
    path('finance/finance/budgetslist/', views.budgetslist, name='budgetslist'),
    path('finance/budgetslist/finance/importbudgets/<str:docname>/', views.budgetslist, name='budgetslist'),
    path('finance/importbudgets/<int:docname>/', views.importbudgets,                    name='importbudgets'),
    path('finance/importbudgets/<str:docname>/', views.importbudgets,                    name='importbudgets'),
    path('export/orders_from_project/<int:project_id>/', views.orders_from_project),
]
"""