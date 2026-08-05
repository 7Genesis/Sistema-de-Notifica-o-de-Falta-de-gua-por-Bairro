from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ocorrencias/', views.OcorrenciaListView.as_view(), name='ocorrencias_list'),
    path('ocorrencias/create/', views.OcorrenciaCreateView.as_view(), name='ocorrencia_create'),
    path('ocorrencias/<int:pk>/editar/', views.OcorrenciaUpdateView.as_view(), name='ocorrencia_update'),

    # Bairros (CRUD)
    path('bairros/', views.BairroListView.as_view(), name='bairro_list'),
    path('bairros/novo/', views.BairroCreateView.as_view(), name='bairro_create'),
    path('bairros/<int:pk>/editar/', views.BairroUpdateView.as_view(), name='bairro_update'),
    path('bairros/<int:pk>/excluir/', views.BairroDeleteView.as_view(), name='bairro_delete'),

    path('mapa/', views.mapa, name='mapa'),

    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='ocorrencias/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]