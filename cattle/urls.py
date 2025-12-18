from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.login, name="log-in"),
    path('logout/', views.Logout_user, name='logout'),
    path('register/',views.registration, name="register"),
    path('home/',views.home, name="home"),
    path('admin_home/',views.admin_home, name="admin-home"),
    
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
