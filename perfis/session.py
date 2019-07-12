def adicionar_dado(request, chave, valor):
    request.session[chave] = valor


def recuperar_dado(request, chave):
    return request.session.get(chave, '')


def eliminar_dado(request, chave):
    del request.session[chave]