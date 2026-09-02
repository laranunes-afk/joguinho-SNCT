from functools import lru_cache

import pygame

from configuracoes_tela import FPS, criar_tela


COR_FUNDO = (0, 0, 0)
COR_BOTAO = (70, 130, 180)
COR_BOTAO_HOVER = (100, 160, 210)
COR_TEXTO = (255, 255, 255)

CONTROLES = (
    ("W /", "cima", "Pular"),
    ("A /", "esquerda", "Andar para esquerda"),
    ("D /", "direita", "Andar para direita"),
    ("TAB", None, "Reiniciar jogo"),
    ("ESC", None, "Sair do jogo"),
)

# Cada string representa uma linha de uma seta pixelada de 5 x 5 pontos.
SETAS_PIXEL = {
    "cima": ("00100", "01110", "11111", "00100", "00100"),
    "esquerda": ("00100", "01100", "11111", "01100", "00100"),
    "direita": ("00100", "00110", "11111", "00110", "00100"),
}


@lru_cache(maxsize=None)
def _fonte(tamanho):
    """Reutiliza fontes criadas para elementos desenhados a cada quadro."""
    return pygame.font.Font(None, tamanho)


def _desenhar_seta(tela, direcao, x, y, escala=3):
    """Converte a matriz 5 x 5 em pequenos quadrados brancos."""
    for linha, pixels in enumerate(SETAS_PIXEL[direcao]):
        for coluna, pixel in enumerate(pixels):
            if pixel == "1":
                pygame.draw.rect(
                    tela,
                    COR_TEXTO,
                    (
                        x + coluna * escala,
                        y + linha * escala,
                        escala,
                        escala,
                    ),
                )


def _desenhar_tecla(tela, caixa, tecla, direcao, fonte):
    pygame.draw.rect(tela, (48, 75, 112), caixa, border_radius=8)
    pygame.draw.rect(tela, (150, 205, 240), caixa, 2, border_radius=8)
    texto = fonte.render(tecla, True, COR_TEXTO)

    if direcao is None:
        tela.blit(texto, texto.get_rect(center=caixa.center))
        return

    largura_seta = 15
    largura_total = texto.get_width() + 6 + largura_seta
    inicio_x = caixa.centerx - largura_total // 2
    tela.blit(texto, texto.get_rect(midleft=(inicio_x, caixa.centery)))
    _desenhar_seta(
        tela,
        direcao,
        inicio_x + texto.get_width() + 6,
        caixa.centery - largura_seta // 2,
    )


def desenhar_lista_controles(tela, largura, altura):
    """Exibe os controles em um painel lateral."""
    largura_painel = min(310, max(270, largura // 5))
    painel = pygame.Rect(
        largura - largura_painel - 30,
        max(35, (altura - 350) // 2),
        largura_painel,
        350,
    )
    pygame.draw.rect(tela, (17, 25, 43), painel, border_radius=18)
    pygame.draw.rect(tela, (95, 155, 205), painel, 3, border_radius=18)

    fonte_titulo = _fonte(36)
    fonte_tecla = _fonte(26)
    fonte_descricao = _fonte(24)
    titulo = fonte_titulo.render("CONTROLES", True, (255, 215, 70))
    tela.blit(titulo, titulo.get_rect(center=(painel.centerx, painel.top + 34)))

    for indice, (tecla, direcao, descricao) in enumerate(CONTROLES):
        caixa = pygame.Rect(painel.left + 16, painel.top + 69 + indice * 52, 82, 38)
        _desenhar_tecla(tela, caixa, tecla, direcao, fonte_tecla)
        texto = fonte_descricao.render(descricao, True, (225, 235, 245))
        tela.blit(
            texto,
            texto.get_rect(midleft=(caixa.right + 10, caixa.centery)),
        )


def tela_inicial(tela=None, clock=None):
    """Exibe o menu e informa se o jogador escolheu iniciar."""
    if not pygame.get_init():
        pygame.init()
    if tela is None:
        tela, _, _ = criar_tela()
    clock = clock or pygame.time.Clock()
    largura, altura = tela.get_size()

    fonte = _fonte(55)
    botao = pygame.Rect(0, 0, 300, 90)
    botao.center = (largura // 2, altura // 2)

    while True:
        mouse = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return False
            if (
                evento.type == pygame.MOUSEBUTTONDOWN
                and evento.button == 1
                and botao.collidepoint(evento.pos)
            ):
                return True

        tela.fill(COR_FUNDO)
        cor = COR_BOTAO_HOVER if botao.collidepoint(mouse) else COR_BOTAO
        pygame.draw.rect(tela, cor, botao, border_radius=20)
        texto = fonte.render("JOGAR", True, COR_TEXTO)
        tela.blit(texto, texto.get_rect(center=botao.center))

        pygame.display.flip()
        clock.tick(FPS)
