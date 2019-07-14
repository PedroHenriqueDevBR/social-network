from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from usuarios.forms import RegistrarUsuarioForm
from perfis.models import Perfil
from django.contrib import messages

# Create your views here.
class RegistrarUsuarioView(View):
    template_name = 'usuarios/registrar.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = RegistrarUsuarioForm(request.POST)
        if form.is_valid():
            dados_form = form.cleaned_data
            usuario = User.objects.create_user(username=dados_form['email'],
                                                email=dados_form['email'],
                                                password=dados_form['senha'])

            perfil = Perfil(nome=dados_form['nome'],
                            telefone=dados_form['telefone'],
                            nome_empresa=dados_form['nome_empresa'],
                            usuario=usuario)
            perfil.save()
            messages.add_message(request, messages.INFO, 'Usuário cadastrado com sucesso')
            return redirect('login')
        return render(request, self.template_name, {'form': form})


class LoginUsuarioView(View):
    template_name = 'usuarios/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('user')
        password = request.POST.get('pass')

        user = authenticate(request, username=username, password=password)

        if user is None:
            if User.objects.filter(email=username):
                messages.add_message(request, messages.INFO, 'Usuário bloqueado.')
            else:
                messages.add_message(request, messages.INFO, 'Usuário não cadastrado.')
        else:
            login(request, user)
            return redirect('index')

        return redirect('login')


class AlterarSenhaView(View):
    template_name = 'usuarios/alterarsenha.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        senha_antiga = request.POST.get('senha_antiga')
        nova_senha = request.POST.get('nova_senha')
        repete_senha = request.POST.get('repete_senha')

        if self.dados_validos_para_alterar_senha(request, senha_antiga, nova_senha, repete_senha):
            user = request.user
            user.set_password(nova_senha)
            user.save()
            return redirect('deslogar')

        return redirect('alterar_senha')


    def dados_validos_para_alterar_senha(self, request, senha_antiga, nova_senha, repete_senha):
        valido = True
        username = request.user.username
        user = authenticate(request, username=username, password=senha_antiga)

        if user is None:
            messages.add_message(request, messages.INFO, 'senha não confere com a cadastrada')
            valido = False
        if nova_senha != repete_senha:
            messages.add_message(request, messages.INFO, 'senha repetida não confere')
            valido = False
        return valido


# Funções soltas
def logout_view(request):
    logout(request)
    return redirect('login')


def tornar_superuser(request, id_perfil):
    if request.user.is_superuser:
        user = Perfil.objects.get(id=id_perfil).usuario
        user.is_superuser = True
        user.save()
    return redirect('/perfil/{}/'.format(id_perfil))


def retirar_superuser(request, id_perfil):
    if request.user.is_superuser:
        user = Perfil.objects.get(id=id_perfil).usuario
        user.is_superuser = False
        user.save()
    return redirect('/perfil/{}/'.format(id_perfil))


def bloquear_usuario(request, id_perfil):
    if request.user.is_superuser:
        user = Perfil.objects.get(id=id_perfil).usuario
        user.is_active = False
        user.save()
    return redirect('/perfil/{}/'.format(id_perfil))


def bloquear_meu_usuario(request):
    user = request.user
    user.is_active = False
    user.save()
    return redirect('deslogar')


def desbloquear_usuario(request, id_perfil):
    if request.user.is_superuser:
        user = Perfil.objects.get(id=id_perfil).usuario
        user.is_active = True
        user.save()
    return redirect('/perfil/{}/'.format(id_perfil))
