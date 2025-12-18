from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.cow_home, name="cow-home"),
    path('add/', views.add_cattle, name='add_cattle'),
    path('list/', views.cattle_list, name='cattle_list'),
    # path('cattle/<int:id>/', views.cattle_delete, name='cattle_list'),
    path('milking/add/', views.add_milking, name='add_milking'),
    path('milking/list/', views.milking_list, name='milking_list'),
    path('cattle/milk_report/', views.cattle_milk_report, name='cattle_milk_report'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('inventory/list/', views.inventory_list, name='inventory_list'),
    path('breeding/add/',add_breeding, name='add_breeding'),
    path('breeding/list/',breeding_list, name='breeding-list'),

    path('health/add/', add_health_status, name='add_health_status'),
    path('health/list/', health_status_list, name='health_status_list'),

    path('feed/add/', add_feed, name='add_feed'),
    path('feed/list/', feed_list, name='feed_list'),

    path('income/add/', add_income, name='add_income'),
    path('income/list/', income_list, name='income_list'),


    path('report/',report, name='full_report'),


    path("sell-cattle/<int:id>/", views.sell_cattle, name="sell_cattle"),
    path("cattle-archive/", views.cattle_archive, name="cattle_archive"),


    path('cattle/reentry/<int:cattle_id>/', views.reentry_cattle, name='reentry_cattle'),

    path("alert/", views.alert, name="alert_status"),
    path('update-cattle/<int:id>/', views.update_cattle, name='update_cattle'),


    



    
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
