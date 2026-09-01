from pathlib import Path

import pygame


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTA_IMAGENS = RAIZ_PROJETO / "Imagens"


def carregar_imagem(nome, tamanho=None, fundo_transparente=False):
    """Carrega uma imagem do projeto e ajusta seu tamanho quando necessário."""
    imagem_original = pygame.image.load(PASTA_IMAGENS / nome)
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


def carregar_imagem_recortada(nome, tamanho=None):
    """Carrega somente a area visivel da arte e opcionalmente redimensiona."""
    imagem = carregar_imagem(nome, fundo_transparente=True)
    limites = pygame.mask.from_surface(imagem).get_bounding_rects()
    if limites:
        area_visivel = limites[0].unionall(limites)
        imagem = imagem.subsurface(area_visivel).copy()
    if tamanho is not None:
        imagem = pygame.transform.scale(imagem, tamanho)
    return imagem
