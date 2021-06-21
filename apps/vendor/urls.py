from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('vendor_admin/', views.vendor_admin, name='vendor_admin'),


    path('become-vendor/', views.become_vendor, name='become_vendor'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-vendor/', views.edit_vendor, name='edit_vendor'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),

    path('myaccount/', views.myaccount, name='myaccount'),
    path('become-customer/', views.become_customer, name='become_customer'),
    path('request_restore_password/', views.request_restore_password, name='request_restore_password'),
    path('restore_password/', views.restore_password, name='restore_password'),


    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('login/', auth_views.LoginView.as_view(template_name='vendor/login.html'), name='login'),

    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    # path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),

    path('', views.vendors, name='vendors'),
    path('<int:vendor_id>/', views.vendor, name='vendor'),
]
