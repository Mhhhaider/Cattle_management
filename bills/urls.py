# billing/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('add-item/', views.add_item, name='add_item'),
    path('items/', views.item_list, name='item_list'),
    path('item/delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('create/', views.create_bill, name='create_bill'),
    path('view/<int:bill_id>/', views.view_bill, name='view_bill'),
    path('billitems/', views.billitem_list, name='billitem_list'),
    path('bill/<int:bill_id>/pdf/', views.download_bill_pdf, name='download_bill_pdf'),

    path('customer/add/', views.add_customer, name='add_customer'),
    path('customers/', views.list_customers, name='list_customers'),

]
