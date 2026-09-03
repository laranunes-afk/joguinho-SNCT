import pygame

from configuracoes_tela import FPS, criar_tela
from recursos import carregar_imagem, renderizar_texto_contornado


COR_BOTAO = (92, 42, 20)
COR_BOTAO_HOVER = (142, 70, 26)
COR_BORDA_BOTAO = (236, 158, 52)
COR_BORDA_INTERNA = (255, 211, 111)
COR_SOMBRA_BOTAO = (45, 20, 11)
COR_TEXTO_BOTAO = (255, 235, 178)
COR_TEXTO = (255, 255, 255)
ARQUIVO_FUNDO = "cenario_menu.png"

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
_FONTES = {}
_FUNDOS_MENU = {}


def _fonte(tamanho):
    """Reutiliza fontes criadas para elementos desenhados a cada quadro."""
    if tamanho not in _FONTES:
        _FONTES[tamanho] = pygame.font.Font(None, tamanho)
    return _FONTES[tamanho]


def _fundo_menu(largura, altura):
    """Ajusta a arte do menu à tela sem deformar nem deixar bordas."""
    chave = (largura, altura)
    if chave in _FUNDOS_MENU:
        return _FUNDOS_MENU[chave]

    original = carregar_imagem(ARQUIVO_FUNDO)
    escala = max(
        largura / original.get_width(),
        altura / original.get_height(),
    )
    tamanho = (
        max(largura, round(original.get_width() * escala)),
        max(altura, round(original.get_height() * escala)),
    )
    redimensionado = pygame.transform.scale(original, tamanho)
    area = pygame.Rect(0, 0, largura, altura)
    area.center = redimensionado.get_rect().center
    fundo = redimensionado.subsurface(area).copy()
    if len(_FUNDOS_MENU) >= 4:
        primeira_chave = next(iter(_FUNDOS_MENU))
        del _FUNDOS_MENU[primeira_chave]
    _FUNDOS_MENU[chave] = fundo
    return fundo


def _forma_pixelada(rect, corte=10):
    """Cria uma placa retangular com cantos em degraus."""
    return (
        (rect.left + corte, rect.top),
        (rect.right - corte, rect.top),
        (rect.right - corte, rect.top + 4),
        (rect.right - 4, rect.top + 4),
        (rect.right - 4, rect.top + corte),
        (rect.right, rect.top + corte),
        (rect.right, rect.bottom - corte),
        (rect.right - 4, rect.bottom - corte),
        (rect.right - 4, rect.bottom - 4),
        (rect.right - corte, rect.bottom - 4),
        (rect.right - corte, rect.bottom),
        (rect.left + corte, rect.bottom),
        (rect.left + corte, rect.bottom - 4),
        (rect.left + 4, rect.bottom - 4),
        (rect.left + 4, rect.bottom - corte),
        (rect.left, rect.bottom - corte),
        (rect.left, rect.top + corte),
        (rect.left + 4, rect.top + corte),
        (rect.left + 4, rect.top + 4),
        (rect.left + corte, rect.top + 4),
    )


def _desenhar_botao_menu(tela, botao, mouse, fonte):
    """Desenha uma placa pixelada inspirada nas cores do cenário."""
    destacado = botao.collidepoint(mouse)
    cor_fundo = COR_BOTAO_HOVER if destacado else COR_BOTAO
    deslocamento_texto = -2 if destacado else 0

    sombra = botao.move(0, 7)
    pygame.draw.polygon(tela, COR_SOMBRA_BOTAO, _forma_pixelada(sombra))
    if destacado:
        pygame.draw.polygon(
            tela,
            (255, 189, 65),
            _forma_pixelada(botao.inflate(12, 12), corte=14),
            width=3,
        )

    pygame.draw.polygon(tela, cor_fundo, _forma_pixelada(botao))
    pygame.draw.polygon(
        tela,
        COR_BORDA_BOTAO,
        _forma_pixelada(botao),
        width=4,
    )
    pygame.draw.polygon(
        tela,
        COR_BORDA_INTERNA,
        _forma_pixelada(botao.inflate(-14, -14), corte=6),
        width=2,
    )
    pygame.draw.line(
        tela,
        (181, 91, 34),
        (botao.left + 24, botao.top + 12),
        (botao.right - 24, botao.top + 12),
        2,
    )

    for x in (botao.left + 17, botao.right - 17):
        pygame.draw.rect(
            tela,
            COR_BORDA_INTERNA,
            (x - 4, botao.centery - 4, 8, 8),
        )
        pygame.draw.rect(
            tela,
            (112, 51, 20),
            (x - 2, botao.centery - 2, 4, 4),
        )

    texto_base = renderizar_texto_contornado(
        fonte,
        "JOGAR",
        (48, 20, 10),
        cor_texto=COR_TEXTO_BOTAO,
        espessura=1,
        antialias=False,
    )
    texto = pygame.transform.scale(
        texto_base,
        (texto_base.get_width() * 2, texto_base.get_height() * 2),
    )
    tela.blit(
        texto,
        texto.get_rect(
            center=(botao.centerx, botao.centery + deslocamento_texto),
        ),
    )


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

    fonte = _fonte(27)
    botao = pygame.Rect(0, 0, 336, 88)
    botao.center = (largura // 2, int(altura * 0.78))
    fundo = _fundo_menu(largura, altura)

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

        tela.blit(fundo, (0, 0))
        _desenhar_botao_menu(tela, botao, mouse, fonte)

        pygame.display.flip()
        clock.tick(FPS)
