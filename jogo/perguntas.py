import random

import pygame

from dados_perguntas import PERGUNTAS_POR_FASE, TIPOS_DE_PERGUNTA


class Perguntas:
    """Exibe perguntas de múltipla escolha específicas de cada fase."""

    def __init__(self):
        """Cria e embaralha os bancos de perguntas das três fases."""
        self.tipos = TIPOS_DE_PERGUNTA
        self.listas = {
            fase: list(perguntas)
            for fase, perguntas in PERGUNTAS_POR_FASE.items()
        }

        self.indices = {1: 0, 2: 0, 3: 0}

        for lista in self.listas.values():
            random.shuffle(lista)

    def _proxima_pergunta(self, fase):
        """Seleciona a próxima pergunta da fase sem esgotar a lista."""
        lista = self.listas[fase]
        indice = self.indices[fase]

        if indice > 0 and indice % len(lista) == 0:
            random.shuffle(lista)

        self.indices[fase] += 1
        return lista[indice % len(lista)]

    def fazer(self, tela, fase):
        """Retorna True para acerto, False para erro e None ao sair."""

        largura, altura = tela.get_size()
        pergunta, respostas, correta = self._proxima_pergunta(fase)

        fonte_titulo = pygame.font.Font(None, 58)
        fonte_pergunta = pygame.font.Font(None, 44)
        fonte_resposta = pygame.font.Font(None, 36)
        fonte_instrucao = pygame.font.Font(None, 28)
        clock = pygame.time.Clock()

        largura_botao = min(900, largura - 120)
        altura_botao = 70
        espacamento = 18
        inicio_y = max(220, altura // 3)

        botoes = []

        for indice in range(4):
            botao = pygame.Rect(
                0,
                inicio_y + indice * (altura_botao + espacamento),
                largura_botao,
                altura_botao
            )
            botao.centerx = largura // 2
            botoes.append(botao)

        teclas = {
            pygame.K_a: 0,
            pygame.K_b: 1,
            pygame.K_c: 2,
            pygame.K_d: 3,
        }

        while True:
            pos_mouse = pygame.mouse.get_pos()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return None

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return None
                    if evento.key == pygame.K_TAB:
                        return "reiniciar"

                    if evento.key in teclas:
                        return teclas[evento.key] == correta

                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for indice, botao in enumerate(botoes):
                        if botao.collidepoint(evento.pos):
                            return indice == correta

            tela.fill((20, 30, 50))

            titulo = fonte_titulo.render(
                f"FASE {fase} - {self.tipos[fase]}",
                True,
                (245, 190, 45)
            )
            tela.blit(titulo, titulo.get_rect(center=(largura // 2, 65)))

            texto_pergunta = fonte_pergunta.render(
                pergunta,
                True,
                (255, 255, 255)
            )
            tela.blit(
                texto_pergunta,
                texto_pergunta.get_rect(center=(largura // 2, 140))
            )

            for indice, botao in enumerate(botoes):
                cor_botao = (
                    (75, 135, 185)
                    if botao.collidepoint(pos_mouse)
                    else (50, 85, 125)
                )

                pygame.draw.rect(tela, cor_botao, botao, border_radius=12)

                texto = fonte_resposta.render(
                    f"{'ABCD'[indice]}) {respostas[indice]}",
                    True,
                    (255, 255, 255)
                )
                tela.blit(texto, texto.get_rect(center=botao.center))

            instrucao = fonte_instrucao.render(
                "Responda com A, B, C ou D  |  TAB reinicia o jogo",
                True,
                (190, 200, 215)
            )
            tela.blit(
                instrucao,
                instrucao.get_rect(center=(largura // 2, altura - 35))
            )

            pygame.display.flip()
            clock.tick(60)

