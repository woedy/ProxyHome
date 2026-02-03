from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from . import views

router = DefaultRouter()
router.register(r'proxies', views.ProxyViewSet)
router.register(r'credentials', views.ProxyCredentialsViewSet)
router.register(r'sources', views.ProxySourceViewSet)
router.register(r'jobs', views.FetchJobViewSet)
router.register(r'tests', views.ProxyTestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', lambda request: JsonResponse({'status': 'ok'}), name='health'),
]