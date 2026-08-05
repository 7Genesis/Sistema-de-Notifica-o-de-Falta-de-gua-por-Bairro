from django.contrib import admin
from .models import Bairro, Ocorrencia

# Configuração opcional para melhorar a visualização na listagem do admin

class OcorrenciasAdmin(admin.ModelAdmin):
    list_display = ('bairro', 'status', 'data_hora', 'responsavel')
    list_filter = ('bairro', 'status')
    search_fields = ('bairro__nome', 'descricao')
    
admin.site.register(Bairro)
admin.site.register(Ocorrencia, OcorrenciasAdmin)