from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from courses.views import logout_view
from memberships.views import billing_address

urlpatterns = [
    path('admin/', admin.site.urls),
    path('memberships/', include('memberships.urls', namespace='memberships')),
    path('', include('courses.urls', namespace='courses')),
    path('accounts/', include('allauth.urls')),
    path('billing-address/', billing_address, name='billing'),
    path('logout/', logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
