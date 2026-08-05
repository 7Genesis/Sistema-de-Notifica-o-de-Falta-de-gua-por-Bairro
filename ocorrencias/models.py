from django.db import models
from django.contrib.auth.models import User

class Bairro(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Bairro")
    criado_em = models.DateTimeField(auto_now_add=True)

    # Coordenadas usadas pra posicionar o bairro no mapa; ficam em branco se não informadas
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        ordering = ['nome']
        verbose_name = "Bairro"
        verbose_name_plural = "Bairros"
        
class Ocorrencia(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Em andamento'),
        ('resolvido', 'Resolvido'),
    ]
    
    bairro = models.ForeignKey(Bairro, on_delete=models.PROTECT, related_name='ocorrencias')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora")
    descricao = models.TextField(verbose_name="Descrição")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    
    #Vincula o sistema de login no nativo Django
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsável")
    
    def __str__(self):
        return f"{self.bairro.nome} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Ocorrência'
        verbose_name_plural = 'Ocorrências'
        
