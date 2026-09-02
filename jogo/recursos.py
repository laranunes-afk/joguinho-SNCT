from functools import lru_cache
from pathlib import Path

import pygame


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTA_IMAGENS = RAIZ_PROJETO / "Imagens"


def _normalizar_tamanho(tamanho):
    """Converte tamanhos mutáveis em uma chave segura para o cache."""
    if tamanho is None:
        return None
    return tuple(map(int, tamanho))


@lru_cache(maxsize=128)
def _carregar_imagem_em_cache(nome, tamanho, fundo_transparente):
    """Carrega e prepara a superfície mestre compartilhada apenas internamente."""
    imagem_original = pygame.image.load(str(PASTA_IMAGENS / nome))
    tem_transparencia = imagem_original.get_masks()[3] != 0
    imagem = (
        imagem_original.convert_alpha()
        if tem_transparencia
        else imagem_original.convert()
    )

    # Algumas artes antigas usam preto como fundo; as novas preservam alfa.
    if fundo_transparente and not tem_transparencia:
        imagem.set_colorkey((0, 0, 0))

    if tamanho is not None:
        imagem = pygame.transform.scale(imagem, tamanho)

    return imagem


def carregar_imagem(nome, tamanho=None, fundo_transparente=False):
    """Carrega uma imagem e devolve uma cópia independente para o chamador."""
    tamanho = _normalizar_tamanho(tamanho)
    imagem = _carregar_imagem_em_cache(
        str(nome),
        tamanho,
        bool(fundo_transparente),
    )
    # A cópia impede que set_alpha, fill ou blit alterem a versão em cache.
    return imagem.copy()


@lru_cache(maxsize=128)
def _carregar_imagem_recortada_em_cache(nome, tamanho):
    """Mantém em cache o recorte pronto, inclusive suas transformações."""
    imagem = _carregar_imagem_em_cache(nome, None, True)
    # O limite 128 equivale ao limiar padrão usado pela máscara anterior.
    area_visivel = imagem.get_bounding_rect(128)
    if area_visivel.width and area_visivel.height:
        imagem = imagem.subsurface(area_visivel).copy()
    else:
        imagem = imagem.copy()

    if tamanho is not None:
        imagem = pygame.transform.scale(imagem, tamanho)
    return imagem


def carregar_imagem_recortada(nome, tamanho=None):
    """Carrega somente a área visível e devolve uma superfície independente."""
    tamanho = _normalizar_tamanho(tamanho)
    imagem = _carregar_imagem_recortada_em_cache(str(nome), tamanho)
    return imagem.copy()


def renderizar_texto_contornado(
    fonte,
    texto,
    cor_contorno,
    cor_texto=(0, 0, 0),
    espessura=1,
    antialias=False,
):
    """Cria texto legivel com preenchimento e contorno independentes."""
    preenchimento = fonte.render(texto, antialias, cor_texto)
    contorno = fonte.render(texto, antialias, cor_contorno)
    margem = espessura
    superficie = pygame.Surface(
        (
            preenchimento.get_width() + margem * 2,
            preenchimento.get_height() + margem * 2,
        ),
        pygame.SRCALPHA,
    )

    for deslocamento_x in range(-espessura, espessura + 1):
        for deslocamento_y in range(-espessura, espessura + 1):
            if deslocamento_x == 0 and deslocamento_y == 0:
                continue
            superficie.blit(
                contorno,
                (margem + deslocamento_x, margem + deslocamento_y),
            )

    superficie.blit(preenchimento, (margem, margem))
    return superficie
