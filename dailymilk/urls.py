from django.urls import path
from . import views

urlpatterns = [
    path('', views.collection_list, name='collection_list'),
    path('add/', views.collection_add, name='collection_add'),
    path('edit/<int:pk>/', views.collection_edit, name='collection_edit'),
    path('delete/<int:pk>/', views.collection_delete, name='collection_delete'),
    path('collections/pdf/', views.collection_pdf, name='collection_pdf'),
    path('customers_list/', views.customers_list, name='customer-list'),
    path('customers_delete/<int:id>', views.customers_delete, name='customer-delete'),
    path('customers/', views.customers_add, name='customer-add'),
    
]
