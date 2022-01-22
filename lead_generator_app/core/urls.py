from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('/leads_table', views.result, name='leads_table')
]
    