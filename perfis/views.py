from django.shortcuts import render, redirect
from perfis.models import Perfil, Convite, Post
from perfis import session, constants
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage


# # 
# # Páginas
# # 
@login_required(login_url='login')
def index(request):
    dados = {}
    dados['perfis'] = Perfil.objects.all()
    dados['perfil_logado'] = request.user.perfil
    dados['timeline'] = selecionar_posts_de_amigos(request)

    return render(request, 'index.html', dados)

@login_required(login_url='login')
def exibir_perfil(request, perfil_id):
    dados = {}
    dados['perfil'] = Perfil.objects.get(id=perfil_id)
    dados['perfil_logado'] = perfil_logado = request.user.perfil
    dados['ja_eh_contato'] = dados['perfil_logado'].contatos.filter(id=dados['perfil'].id)
    dados['timeline'] = dados['perfil'].posts.all() 

    return render(request, 'perfil.html', dados)

@login_required(login_url='login')
def esqueci_a_minha_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        query = Perfil.objects.filter(email=email)
        if len(query) == 0:
            messages.add_message(request, messages.INFO, 'Email não cadastrado')
            return redirect('esqueci_senha')
        else:
            # Deve criar um token
            # Deve enviar uma mensagem para o email do solicitante
            messages.add_message(request, messages.INFO, 'Ainda não feito, Um email foi enviado para você contendo o link de alteração de senha')
            return redirect('login')
    return render(request, 'esqueci_senha.html')

@login_required(login_url='login')
def postagem(request):
    if request.method == 'POST':
        try:
            titulo = request.POST.get('titulo')
            texto = request.POST.get('texto')
            imagem = request.FILES['imagem']
            perfil = request.user.perfil
            # Formatação da imagem
            file_system = FileSystemStorage()
            file_name = file_system.save(imagem.name, imagem)
            # Salvando no banco de dados
            Post.objects.create(titulo=titulo, text=texto, perfil=perfil, imagem=file_name)
            messages.add_message(request, messages.INFO, 'Postagem publicada.')

        except Exception:
            titulo = request.POST.get('titulo')
            texto = request.POST.get('texto')
            perfil = request.user.perfil
            Post.objects.create(titulo=titulo, text=texto, perfil=perfil)
            messages.add_message(request, messages.INFO, 'Postagem publicada.')

    return redirect('minhas_postagens')

@login_required(login_url='login')
def delete_postagem(request, id_postagem):
    post = Post.objects.get(id=id_postagem)

    if post.perfil == request.user.perfil or request.user.is_superuser:
        post.delete()
        messages.add_message(request, messages.INFO, 'Post deletado com sucesso!')

    return redirect('index')
    

@login_required(login_url='login')
def convidar(request, perfil_id):
    perfil_a_convidar = Perfil.objects.get(id=perfil_id)
    perfil_logado = request.user.perfil
    perfil_logado.convidar(perfil_a_convidar)

    messages.add_message(request, messages.INFO, 'Solicitação de amizade enviada para {}.'.format(perfil_a_convidar.nome))

    return redirect('index')

@login_required(login_url='login')
def aceitar(request, convite_id):
    convite = Convite.objects.get(id=convite_id)
    messages.add_message(request, messages.INFO, 'Convite aceito para {}.'.format(convite.solicitante))
    convite.aceitar()
    return redirect('index')

@login_required(login_url='login')
def rejeitar(request, convite_id):
    convite = Convite.objects.get(id=convite_id)
    convite.rejeitar()
    messages.add_message(request, messages.INFO, 'Solicitação cancelada.')
    return redirect('index')

@login_required(login_url='login')
def desfazer_amizade(request, perfil_id):
    amizade = Perfil.objects.get(id=perfil_id)
    perfil_logado = request.user.perfil
    perfil_logado.desfazer_amizade(amizade)
    messages.add_message(request, messages.INFO, 'Você e {} não estão mais conectados.'.format(amizade.nome))
    return redirect('index')

@login_required(login_url='login')
def buscar_usuario(request):
    encontrados = Perfil.objects.all()

    if request.method == 'POST':
        query = request.POST.get('busca')
        encontrados = list(Perfil.objects.filter(nome__contains=query))
        encontrados.remove(request.user.perfil)

    dados = {}
    dados['encontrados'] = encontrados
    dados['perfil_logado'] = request.user.perfil
    
    word = 'perfil'
    if len(dados['encontrados']) > 1: 
        word = 'perfis'
    messages.add_message(request, messages.INFO, 'Foram encontrados {} {}'.format(len(dados['encontrados']), word))
    
    return render(request, 'buscarusuario.html', dados)

@login_required(login_url='login')
def conexoes(request):
    dados = {}
    dados['perfil_logado'] = request.user.perfil
    dados['encontrados'] = dados['perfil_logado'].contatos.all()
    return render(request, 'buscarusuario.html', dados)

@login_required(login_url='login')
def excluir_postagem(request, id_postagem):
    postagem = Post.objects.get(id=id_postagem)
    postagem.delete()
    messages.add_message(request, messages.INFO, 'Postagem deletada')
    return redirect('index')

@login_required(login_url='login')
def alterar_perfil(request):
    try:
        if request.method == 'POST':
            imagem = request.FILES['imagemperfil']
            file_system = FileSystemStorage()
            file_name = file_system.save(imagem.name, imagem)

            perfil_logado = request.user.perfil
            perfil_logado.imagem_perfil = file_name
            perfil_logado.save()
            
            return redirect('index')
    except:
        return redirect('index')

@login_required(login_url='login')
def alterar_capa(request):
    try:
        if request.method == 'POST':
            imagem = request.FILES['imagemcapa']
            file_system = FileSystemStorage()
            file_name = file_system.save(imagem.name, imagem)

            perfil_logado = request.user.perfil
            perfil_logado.imagem_capa = file_name
            perfil_logado.save()
            
            return redirect('index')
    except:
        return redirect('index')

@login_required(login_url='login')
def minhas_postagens(request):
    dados = {}
    dados['perfis'] = Perfil.objects.all()
    dados['perfil_logado'] = request.user.perfil
    dados['timeline'] = selecionar_minhas_postagens(request) 

    return render(request, 'index.html', dados)

# #
# # Métodos auxiliares
# #
def selecionar_posts_de_amigos(request):
    perfil_logado = request.user.perfil
    amigos = perfil_logado.contatos.all()
    posts = []
    for amigo in amigos:
        posts.extend(list(amigo.posts.all()))
    posts.sort(key=lambda x: x.data_postagem, reverse=True)
    return posts

def selecionar_minhas_postagens(request):
    posts = list(request.user.perfil.posts.all())
    posts.sort(key=lambda x: x.data_postagem, reverse=True)
    return posts
