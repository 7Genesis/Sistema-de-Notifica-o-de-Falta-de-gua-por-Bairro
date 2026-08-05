from rest_framework.routers import DefaultRouter
from .api import BairroViewSet, OcorrenciaViewSet

router = DefaultRouter()
router.register('bairros', BairroViewSet, basename='api-bairro')
router.register('ocorrencias', OcorrenciaViewSet, basename='api-ocorrencia')

urlpatterns = router.urls
