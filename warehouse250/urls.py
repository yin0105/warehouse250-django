"""warehouse250 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from apps.newsletter.api import api_add_subscriber

from django.contrib.sitemaps.views import sitemap

from .sitemaps import StaticViewSitemap, CategorySitemap, ProductSitemap, PostSitemap

from apps.vendor import views as vendor_views

sitemaps = {'static': StaticViewSitemap,
            'product': ProductSitemap, 'category': CategorySitemap, 'post': PostSitemap}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('vendor/', include('apps.vendor.urls')),
    path('cart/', include('apps.cart.urls')),
    path('blog/', include('apps.blog.urls')),
    path('api/add_subscriber/', api_add_subscriber, name='api_add_subscriber'),
    path("dashboard/", include("apps.dashboard.urls")),
    path('', include('apps.core.urls')),
    path('', include('apps.product.urls')),
    

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.view.sitemap'),



    path('activate/<slug:uidb64>/<slug:token>/',
         vendor_views.activate, name='activate'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

print(urlpatterns)
