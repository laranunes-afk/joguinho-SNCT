import random

import pygame


class Perguntas:
    """Exibe perguntas de múltipla escolha específicas de cada fase."""

    def __init__(self):
        self.tipos = {
            1: "CONHECIMENTOS GERAIS",
            2: "MATEMÁTICA",
            3: "CIÊNCIAS",
        }

        self.listas = {
            1: [
                ("Qual é a capital do Brasil?",
                 ["Brasília", "Salvador", "São Paulo", "Recife"], 0),
                ("Em qual continente fica o Brasil?",
                 ["Europa", "Ásia", "América do Sul", "África"], 2),
                ("Quantos dias possui uma semana?",
                 ["Cinco", "Seis", "Sete", "Oito"], 2),
                ("Qual idioma é falado oficialmente no Brasil?",
                 ["Espanhol", "Português", "Inglês", "Francês"], 1),
            ],
            2: [
                ("Quanto é 7 x 8?", ["48", "54", "56", "64"], 2),
                ("Quanto é 100 dividido por 4?", ["20", "25", "30", "40"], 1),
                ("Quanto é 35 + 27?", ["52", "60", "62", "72"], 2),
                ("Quantos lados possui um hexágono?",
                 ["Cinco", "Seis", "Sete", "Oito"], 1),
            ],
            3: [
                ("Qual é o maior planeta do Sistema Solar?",
                 ["Terra", "Marte", "Saturno", "Júpiter"], 3),
                ("Qual destes animais é um mamífero?",
                 ["Tubarão", "Golfinho", "Polvo", "Pinguim"], 1),
                ("Qual gás é essencial para a respiração humana?",
                 ["Oxigênio", "Hélio", "Hidrogênio", "Neônio"], 0),
                ("A água congela normalmente a quantos graus Celsius?",
                 ["0", "10", "50", "100"], 0),
            ],
        }

        self.indices = {1: 0, 2: 0, 3: 0}

        for lista in self.listas.values():
            random.shuffle(lista)

    def _proxima_pergunta(self, fase):
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
                "Clique em uma resposta ou pressione A, B, C ou D",
                True,
                (190, 200, 215)
            )
            tela.blit(
                instrucao,
                instrucao.get_rect(center=(largura // 2, altura - 35))
            )

            pygame.display.flip()
            clock.tick(60)

    def mostrar_vitoria(self, tela, segundos_decorridos):
        largura, altura = tela.get_size()
        fonte_titulo = pygame.font.Font(None, 90)
        fonte_texto = pygame.font.Font(None, 42)
        clock = pygame.time.Clock()

        minutos = segundos_decorridos // 60
        segundos = segundos_decorridos % 60

        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return

                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        return

                if evento.type == pygame.MOUSEBUTTONDOWN:
                    return

            tela.fill((18, 35, 45))

            titulo = fonte_titulo.render(
                "VOCÊ COMPLETOU AS 3 FASES!",
                True,
                (80, 220, 120)
            )
            tela.blit(
                titulo,
                titulo.get_rect(center=(largura // 2, altura // 2 - 70))
            )

            tempo = fonte_texto.render(
                f"Tempo final: {minutos:02d}:{segundos:02d}",
                True,
                (255, 255, 255)
            )
            tela.blit(
                tempo,
                tempo.get_rect(center=(largura // 2, altura // 2 + 25))
            )

            sair = fonte_texto.render(
                "Pressione Enter ou clique para sair",
                True,
                (190, 200, 210)
            )
            tela.blit(
                sair,
                sair.get_rect(center=(largura // 2, altura // 2 + 95))
            )

            pygame.display.flip()
            clock.tick(60)
