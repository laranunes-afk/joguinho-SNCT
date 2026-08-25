from pathlib import Path

import pygame


PASTA_IMAGENS = Path(__file__).with_name("Imagens")


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
