from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import BairroForm, OcorrenciaForm
from .models import Bairro, Ocorrencia


class BairroModelTests(TestCase):
    def test_str_retorna_o_nome(self):
        bairro = Bairro.objects.create(nome='Centro')
        self.assertEqual(str(bairro), 'Centro')

    def test_nome_e_unico(self):
        Bairro.objects.create(nome='Centro')
        with self.assertRaises(Exception):
            Bairro.objects.create(nome='Centro')


class OcorrenciaModelTests(TestCase):
    def setUp(self):
        self.bairro = Bairro.objects.create(nome='Centro')

    def test_str_combina_bairro_e_status(self):
        ocorrencia = Ocorrencia.objects.create(
            bairro=self.bairro, descricao='Sem água desde ontem', status='pendente',
        )
        self.assertEqual(str(ocorrencia), 'Centro - Em andamento')

    def test_status_padrao_e_pendente(self):
        ocorrencia = Ocorrencia.objects.create(bairro=self.bairro, descricao='Vazamento na rua')
        self.assertEqual(ocorrencia.status, 'pendente')


class BairroFormTests(TestCase):
    def test_form_valido_com_nome_preenchido(self):
        form = BairroForm(data={'nome': 'Centro'})
        self.assertTrue(form.is_valid())

    def test_form_invalido_sem_nome(self):
        form = BairroForm(data={'nome': ''})
        self.assertFalse(form.is_valid())


class OcorrenciaFormTests(TestCase):
    def setUp(self):
        self.bairro = Bairro.objects.create(nome='Centro')

    def test_form_valido_com_campos_obrigatorios(self):
        form = OcorrenciaForm(data={
            'bairro': self.bairro.id, 'descricao': 'Falta de água', 'status': 'pendente',
        })
        self.assertTrue(form.is_valid())

    def test_form_invalido_sem_descricao(self):
        form = OcorrenciaForm(data={'bairro': self.bairro.id, 'descricao': '', 'status': 'pendente'})
        self.assertFalse(form.is_valid())


class LoginObrigatorioTests(TestCase):
    """
    Confere que as páginas do sistema exigem login antes de qualquer coisa.
    """
    def test_dashboard_redireciona_para_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_lista_de_ocorrencias_redireciona_para_login(self):
        response = self.client.get(reverse('ocorrencias_list'))
        self.assertEqual(response.status_code, 302)

    def test_lista_de_bairros_redireciona_para_login(self):
        response = self.client.get(reverse('bairro_list'))
        self.assertEqual(response.status_code, 302)


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('usuario', password='senha12345')
        self.bairro = Bairro.objects.create(nome='Centro')
        self.client.login(username='usuario', password='senha12345')

    def test_totais_batem_com_o_banco(self):
        Ocorrencia.objects.create(bairro=self.bairro, descricao='A', status='pendente')
        Ocorrencia.objects.create(bairro=self.bairro, descricao='B', status='pendente')
        Ocorrencia.objects.create(bairro=self.bairro, descricao='C', status='resolvido')

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['total'], 3)
        self.assertEqual(response.context['pendentes'], 2)
        self.assertEqual(response.context['resolvidas'], 1)


class OcorrenciaViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('usuario', password='senha12345')
        self.bairro_centro = Bairro.objects.create(nome='Centro')
        self.bairro_massaroca = Bairro.objects.create(nome='Massaroca')
        self.client.login(username='usuario', password='senha12345')

    def test_criar_ocorrencia_define_responsavel_como_usuario_logado(self):
        self.client.post(reverse('ocorrencia_create'), {
            'bairro': self.bairro_centro.id, 'descricao': 'Cano estourado', 'status': 'pendente',
        })
        ocorrencia = Ocorrencia.objects.get(descricao='Cano estourado')
        self.assertEqual(ocorrencia.responsavel, self.user)

    def test_filtro_por_bairro(self):
        Ocorrencia.objects.create(bairro=self.bairro_centro, descricao='A', status='pendente')
        Ocorrencia.objects.create(bairro=self.bairro_massaroca, descricao='B', status='pendente')

        response = self.client.get(reverse('ocorrencias_list'), {'bairro': self.bairro_centro.id})

        self.assertEqual(list(response.context['ocorrencias']), [Ocorrencia.objects.get(descricao='A')])

    def test_filtro_por_status(self):
        Ocorrencia.objects.create(bairro=self.bairro_centro, descricao='A', status='pendente')
        Ocorrencia.objects.create(bairro=self.bairro_centro, descricao='B', status='resolvido')

        response = self.client.get(reverse('ocorrencias_list'), {'status': 'resolvido'})

        self.assertEqual(list(response.context['ocorrencias']), [Ocorrencia.objects.get(descricao='B')])

    def test_marcar_ocorrencia_como_resolvida(self):
        ocorrencia = Ocorrencia.objects.create(bairro=self.bairro_centro, descricao='A', status='pendente')

        self.client.post(reverse('ocorrencia_update', args=[ocorrencia.pk]), {
            'bairro': self.bairro_centro.id, 'descricao': 'A', 'status': 'resolvido',
        })

        ocorrencia.refresh_from_db()
        self.assertEqual(ocorrencia.status, 'resolvido')


class BairroViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('usuario', password='senha12345')
        self.client.login(username='usuario', password='senha12345')

    def test_criar_bairro(self):
        self.client.post(reverse('bairro_create'), {'nome': 'Centro'})
        self.assertTrue(Bairro.objects.filter(nome='Centro').exists())

    def test_editar_bairro(self):
        bairro = Bairro.objects.create(nome='Centro')
        self.client.post(reverse('bairro_update', args=[bairro.pk]), {'nome': 'Centro Histórico'})
        bairro.refresh_from_db()
        self.assertEqual(bairro.nome, 'Centro Histórico')

    def test_excluir_bairro(self):
        bairro = Bairro.objects.create(nome='Centro')
        self.client.post(reverse('bairro_delete', args=[bairro.pk]))
        self.assertFalse(Bairro.objects.filter(pk=bairro.pk).exists())

    def test_nao_exclui_bairro_com_ocorrencias_vinculadas(self):
        bairro = Bairro.objects.create(nome='Centro')
        Ocorrencia.objects.create(bairro=bairro, descricao='A', status='pendente')

        with self.assertRaises(Exception):
            self.client.post(reverse('bairro_delete', args=[bairro.pk]))


class ApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('usuario', password='senha12345')
        self.bairro = Bairro.objects.create(nome='Centro')

    def test_api_exige_autenticacao(self):
        response = self.client.get('/api/bairros/')
        self.assertEqual(response.status_code, 403)

    def test_api_lista_bairros_autenticado(self):
        self.client.login(username='usuario', password='senha12345')
        response = self.client.get('/api/bairros/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_api_cria_ocorrencia_com_responsavel_automatico(self):
        self.client.login(username='usuario', password='senha12345')
        response = self.client.post('/api/ocorrencias/', {
            'bairro': self.bairro.id, 'descricao': 'Falta de água', 'status': 'pendente',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['responsavel'], self.user.id)

    def test_api_filtra_por_status(self):
        self.client.login(username='usuario', password='senha12345')
        Ocorrencia.objects.create(bairro=self.bairro, descricao='A', status='pendente')
        Ocorrencia.objects.create(bairro=self.bairro, descricao='B', status='resolvido')

        response = self.client.get('/api/ocorrencias/', {'status': 'resolvido'})

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['descricao'], 'B')
