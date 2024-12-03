from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pos/', include('pos.urls', namespace='pos')),
    path('', include('users.urls')),
]
