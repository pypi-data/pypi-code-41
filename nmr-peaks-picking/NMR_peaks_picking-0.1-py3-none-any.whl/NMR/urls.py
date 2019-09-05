from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.conf.urls import url



urlpatterns = [
    path('', views.index, name='index'),
    path('spectra/', views.SpectrumListView.as_view(), name='spectra'),
    path('<int:spectrum_id>/', views.detail, name='detail'),
    path('<int:spectrum_id>/csv', views.csv_file, name='csv_file'),
    path('<int:spectrum_id>/process/', views.process, name='process'),
    path('<int:spectrum_id>/pick/', views.pick, name='pick'),
    path('<int:spectrum_id>/predict/', views.predict, name='predict'),
    path('<int:spectrum_id>/save/', views.save, name='save'),
    path('<int:spectrum_id>/peak/', views.peak, name='peak'),
    path('svm/', views.svm, name='svm'),
    path('change/', views.change, name='change'),
    # ex: /polls/5/results/
    path('results/', views.results, name='results'),
]

urlpatterns += [
    path('spectrum/create/', views.SpectrumCreate.as_view(), name='spectrum_create'),
    path('spectrum/<int:pk>/update/', views.SpectrumUpdate.as_view(), name='spectrum_update'),
    path('spectrum/<int:pk>/delete/', views.SpectrumDelete.as_view(), name='spectrum_delete'),
]


