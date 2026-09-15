"""Temas e fundos por cenário; eventos e alternativas ficam na tela base.

As artes são carregadas da pasta Imagens pelo módulo recursos.
Imagens/layout_perguntas_preview.png é apenas uma prévia dos quatro temas.
"""

from copy import copy

import pygame

from cenario import ARQUIVOS_DE_FUNDO
from recursos import carregar_imagem
from tela_multipla_escolha import TelaMultiplaEscolha, TemaMultiplaEscolha


# Fundo do painel, alternativa, alternativa selecionada e detalhes.
PALETAS_POR_FASE = {
    1: ((31, 43, 53), (83, 62, 34), (123, 88, 38), (255, 214, 131)),
    2: ((53, 30, 24), (100, 49, 27), (147, 72, 31), (255, 205, 108)),
    3: ((12, 23, 49), (28, 48, 82), (45, 75, 118), (166, 210, 255)),
    4: ((44, 29, 19), (91, 58, 29), (133, 87, 35), (255, 215, 112)),
}
FUNDOS_POR_FASE = {**ARQUIVOS_DE_FUNDO, 4: "cenário-4-pixilart.png"}
MARGEM_PAINEL = 16
PREENCHIMENTO_PAINEL = 32
MARGEM_VERTICAL_PAINEL = 20
ALPHA_SOMBRA = 95
ALPHA_PAINEL = 235


TEMA_PERGUNTAS = TemaMultiplaEscolha(
    cor_fundo=(20, 30, 50),
    cor_botao=(50, 85, 125),
    cor_botao_hover=(75, 135, 185),
    cor_resposta=(255, 255, 255),
    cor_letra=(255, 255, 255),
    largura_maxima_botao=900,
    margem_horizontal=60,
    altura_botao=70,
    espacamento_botoes=18,
    inicio_botoes_minimo=220,
    y_pergunta=140,
    tamanho_fonte_pergunta=44,
    tamanho_fonte_resposta=36,
    tamanho_fonte_letra=36,
    tamanho_fonte_rodape=28,
    cor_rodape=(190, 200, 215),
    margem_rodape=35,
    raio_borda=12,
)


TEMA_PERGUNTA_FINAL = TemaMultiplaEscolha(
    cor_fundo=(18, 24, 45),
    cor_botao=(48, 75, 112),
    cor_botao_hover=(80, 135, 180),
    cor_resposta=(255, 255, 255),
    cor_letra=(255, 215, 70),
    largura_maxima_botao=820,
    margem_horizontal=50,
    altura_botao=58,
    espacamento_botoes=18,
    inicio_botoes_minimo=225,
    y_pergunta=155,
    tamanho_fonte_pergunta=44,
    tamanho_fonte_resposta=38,
    tamanho_fonte_letra=50,
    tamanho_fonte_rodape=30,
    cor_rodape=(225, 230, 245),
    margem_rodape=28,
    cor_borda=(140, 195, 235),
    espessura_borda=2,
    raio_borda=9,
)


class LayoutPerguntas(TelaMultiplaEscolha):
    """Aplica a arte da fase e compartilha os controles de alternativas."""

    def __init__(self, fase):
        super().__init__(TEMA_PERGUNTAS)
        self.fase = None
        self._fundo = None
        self._tamanho_fundo = None
        self.definir_fase(fase)

    def definir_fase(self, fase):
        """Troca o tema e invalida o fundo somente quando a fase muda."""
        if fase not in PALETAS_POR_FASE:
            raise ValueError(f"Não existe layout de perguntas para a fase {fase}")
        if fase == self.fase:
            return
        painel, botao, hover, destaque = PALETAS_POR_FASE[fase]
        self.tema = copy(TEMA_PERGUNTA_FINAL if fase == 4 else TEMA_PERGUNTAS)
        self.tema.cor_fundo = painel
        self.tema.cor_botao = botao
        self.tema.cor_botao_hover = hover
        self.tema.cor_letra = destaque
        self.tema.cor_borda = destaque
        self.tema.espessura_borda = 2
        self.tema.raio_borda = 3
        self.fase = fase
        self._fundo = None
        self._tamanho_fundo = None

    def _desenhar_fundo(self, tela):
        tamanho = tela.get_size()
        if self._fundo is None or self._tamanho_fundo != tamanho:
            self._fundo = self._criar_fundo(tamanho)
            self._tamanho_fundo = tamanho
        tela.blit(self._fundo, (0, 0))

    def _criar_fundo(self, tamanho):
        """Prepara a arte e o painel uma vez por fase e tamanho de tela."""
        # Escala sem suavizar para preservar o pixel art dos cenarios.
        fundo = carregar_imagem(FUNDOS_POR_FASE[self.fase], tamanho)
        sombra = pygame.Surface(tamanho, pygame.SRCALPHA)
        sombra.fill((0, 0, 0, ALPHA_SOMBRA))
        fundo.blit(sombra, (0, 0))
        largura_painel = min(
            max(1, tamanho[0] - MARGEM_PAINEL * 2),
            self._largura_conteudo(tamanho[0]) + PREENCHIMENTO_PAINEL * 2,
        )
        painel = pygame.Rect(
            0, MARGEM_VERTICAL_PAINEL, largura_painel,
            max(1, tamanho[1] - MARGEM_VERTICAL_PAINEL * 2),
        )
        painel.centerx = tamanho[0] // 2
        camada = pygame.Surface(painel.size, pygame.SRCALPHA)
        camada.fill((*self.tema.cor_fundo, ALPHA_PAINEL))
        fundo.blit(camada, painel)
        pygame.draw.rect(fundo, self.tema.cor_borda, painel, 2)
        # Cantos em degraus acompanham as formas geometricas das piramides.
        for x, sentido in ((painel.left, 1), (painel.right, -1)):
            for y, vertical in ((painel.top, 1), (painel.bottom, -1)):
                pygame.draw.lines(
                    fundo, self.tema.cor_borda, False,
                    [(x, y + vertical * 16), (x, y),
                     (x + sentido * 16, y)],
                    4,
                )
        return fundo
