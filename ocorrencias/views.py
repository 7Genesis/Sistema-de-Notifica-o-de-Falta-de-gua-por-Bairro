from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import OcorrenciaForm, BairroForm
from django.shortcuts import render
from .models import Bairro, Ocorrencia
from .dados_bairros_juazeiro import BAIRROS_JUAZEIRO

class BairroSugestoesMixin:
    """
    Envia a lista de bairros conhecidos de Juazeiro-BA pro template, usada
    como sugestão de nome e coordenadas no formulário de cadastro de bairro.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bairros_sugeridos'] = BAIRROS_JUAZEIRO
        return context

@login_required(login_url='login')
def dashboard(request):
    """
    Renderiza o Dashboard Inicial com métricas agregadas.
    """
    total = Ocorrencia.objects.count()
    pendentes = Ocorrencia.objects.filter(status='pendente').count()
    resolvidas = Ocorrencia.objects.filter(status='resolvido').count()
    
    context = {
        'total': total,
        'pendentes': pendentes,
        'resolvidas': resolvidas,
    }
    
    return render(request, 'ocorrencias/dashboard.html', context)

class OcorrenciaListView(LoginRequiredMixin, ListView):
    """
    View responsável por listar todas as ocorrências cadastradas.
    O LoginRequiredMixin garante a segurança da rota.
    """
    model = Ocorrencia
    template_name = 'ocorrencias/ocorrencia_list.html'
    context_object_name = 'ocorrencias'
    login_url = 'login'
    ordering = ['-data_hora'] # Ordena da mais recente para a mais antiga

    def get_queryset(self):
        # Pega a lista já ordenada e aplica os filtros que vierem na URL (?bairro=1&status=pendente)
        queryset = super().get_queryset()
        bairro_id = self.request.GET.get('bairro')
        status = self.request.GET.get('status')

        if bairro_id:
            queryset = queryset.filter(bairro_id=bairro_id)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        # Envia os bairros e os status disponíveis pro template, pra montar os <select> do filtro
        context = super().get_context_data(**kwargs)
        context['bairros'] = Bairro.objects.all()
        context['status_choices'] = Ocorrencia.STATUS_CHOICES
        return context

class OcorrenciaCreateView(LoginRequiredMixin, CreateView):
    """
    View responsável por renderizar e processar o formulário de criação.
    """
    model = Ocorrencia
    form_class = OcorrenciaForm
    template_name = 'ocorrencias/ocorrencia_form.html'
    success_url = reverse_lazy('ocorrencias_list')
    login_url = 'login'

    def form_valid(self, form):
        # O campo responsável não fica no formulário: quem registra a ocorrência
        # é automaticamente o usuário logado
        form.instance.responsavel = self.request.user
        return super().form_valid(form)

class OcorrenciaUpdateView(LoginRequiredMixin, UpdateView):
    """
    View responsável por renderizar e processar o formulário de edição de ocorrência
    (usada, por exemplo, pra marcar uma ocorrência como resolvida).
    """
    model = Ocorrencia
    form_class = OcorrenciaForm
    template_name = 'ocorrencias/ocorrencia_form.html'
    success_url = reverse_lazy('ocorrencias_list')
    login_url = 'login'

class BairroListView(LoginRequiredMixin, ListView):
    """
    View responsável por listar todos os bairros cadastrados.
    """
    model = Bairro
    template_name = 'ocorrencias/bairro_list.html'
    context_object_name = 'bairros'
    login_url = 'login'

class BairroCreateView(LoginRequiredMixin, BairroSugestoesMixin, CreateView):
    """
    View responsável por renderizar e processar o formulário de criação de bairro.
    """
    model = Bairro
    form_class = BairroForm
    template_name = 'ocorrencias/bairro_form.html'
    success_url = reverse_lazy('bairro_list')
    login_url = 'login'

class BairroUpdateView(LoginRequiredMixin, BairroSugestoesMixin, UpdateView):
    """
    View responsável por renderizar e processar o formulário de edição de bairro.
    """
    model = Bairro
    form_class = BairroForm
    template_name = 'ocorrencias/bairro_form.html'
    success_url = reverse_lazy('bairro_list')
    login_url = 'login'

class BairroDeleteView(LoginRequiredMixin, DeleteView):
    """
    View responsável por confirmar e processar a exclusão de um bairro.
    """
    model = Bairro
    template_name = 'ocorrencias/bairro_confirm_delete.html'
    success_url = reverse_lazy('bairro_list')
    login_url = 'login'

@login_required(login_url='login')
def mapa(request):
    """
    Renderiza o mapa com a localização de cada bairro e sua quantidade de ocorrências pendentes e resolvidas.
    """
    bairros = Bairro.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    dados = [
        {
            'nome': bairro.nome,
            'latitude': float(bairro.latitude),
            'longitude': float(bairro.longitude),
            'pendentes': bairro.ocorrencias.filter(status='pendente').count(),
            'resolvidas': bairro.ocorrencias.filter(status='resolvido').count(),
        }
        for bairro in bairros
    ]
    return render(request, 'ocorrencias/mapa.html', {'bairros_data': dados})
