from rest_framework import viewsets
from .models import Bairro, Ocorrencia
from .serializers import BairroSerializer, OcorrenciaSerializer

class BairroViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API pra listar, criar, editar e excluir bairros.
    """
    queryset = Bairro.objects.all()
    serializer_class = BairroSerializer

class OcorrenciaViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API pra listar, criar, editar e excluir ocorrências.
    Aceita os parâmetros ?bairro=<id> e ?status=<status> pra filtrar a listagem.
    """
    serializer_class = OcorrenciaSerializer

    def get_queryset(self):
        queryset = Ocorrencia.objects.all().order_by('-data_hora')
        bairro_id = self.request.query_params.get('bairro')
        status_param = self.request.query_params.get('status')

        if bairro_id:
            queryset = queryset.filter(bairro_id=bairro_id)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    def perform_create(self, serializer):
        # O responsável pela ocorrência é sempre o usuário autenticado na requisição
        serializer.save(responsavel=self.request.user)
