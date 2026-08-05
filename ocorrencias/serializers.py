from rest_framework import serializers
from .models import Bairro, Ocorrencia

class BairroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bairro
        fields = ['id', 'nome', 'criado_em']

class OcorrenciaSerializer(serializers.ModelSerializer):
    bairro_nome = serializers.CharField(source='bairro.nome', read_only=True)
    responsavel_username = serializers.CharField(source='responsavel.username', read_only=True)

    class Meta:
        model = Ocorrencia
        fields = [
            'id', 'bairro', 'bairro_nome', 'data_hora',
            'descricao', 'status', 'responsavel', 'responsavel_username',
        ]
        read_only_fields = ['responsavel']
