import pygame


class PerguntaFinal:
    """Tela reutilizavel para uma pergunta do desafio final."""

    def __init__(self, largura, altura, total_perguntas):
        self.largura = largura
        self.altura = altura
        self.total_perguntas = total_perguntas

    def fazer(self, tela, dados, numero):
        pergunta, respostas, correta = dados
        fontes = {
            "titulo": pygame.font.Font(None, 52),
            "pergunta": pygame.font.Font(None, 44),
            "resposta": pygame.font.Font(None, 38),
            "letra": pygame.font.Font(None, 50),
            "aviso": pygame.font.Font(None, 30),
        }
        largura_botao = min(820, self.largura - 100)
        inicio_y = max(225, self.altura // 3)
        botoes = [
            pygame.Rect(
                (self.largura - largura_botao) // 2,
                inicio_y + indice * 76,
                largura_botao,
                58,
            )
            for indice in range(4)
        ]
        teclas = {pygame.K_a: 0, pygame.K_b: 1, pygame.K_c: 2, pygame.K_d: 3}
        clock = pygame.time.Clock()

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

            self._desenhar(tela, pergunta, respostas, numero, botoes, pos_mouse, fontes)
            pygame.display.flip()
            clock.tick(60)

    def _desenhar(self, tela, pergunta, respostas, numero, botoes, mouse, fontes):
        tela.fill((18, 24, 45))
        titulo = fontes["titulo"].render(
            f"PERGUNTA DIFICIL {numero}/{self.total_perguntas}", True, (255, 215, 70)
        )
        tela.blit(titulo, titulo.get_rect(center=(self.largura // 2, 62)))
        aviso = fontes["aviso"].render(
            "SE ERRAR, VOCE VOLTA AO INICIO DA FASE 1", True, (255, 145, 125)
        )
        tela.blit(aviso, aviso.get_rect(center=(self.largura // 2, 105)))
        texto = fontes["pergunta"].render(pergunta, True, (255, 255, 255))
        tela.blit(texto, texto.get_rect(center=(self.largura // 2, 155)))

        for indice, botao in enumerate(botoes):
            cor = (80, 135, 180) if botao.collidepoint(mouse) else (48, 75, 112)
            pygame.draw.rect(tela, cor, botao, border_radius=9)
            pygame.draw.rect(tela, (140, 195, 235), botao, width=2, border_radius=9)
            letra = fontes["letra"].render(f"{'ABCD'[indice]})", True, (255, 215, 70))
            resposta = fontes["resposta"].render(respostas[indice], True, (255, 255, 255))
            inicio_x = botao.centerx - (letra.get_width() + 12 + resposta.get_width()) // 2
            tela.blit(letra, letra.get_rect(midleft=(inicio_x, botao.centery)))
            tela.blit(
                resposta,
                resposta.get_rect(midleft=(inicio_x + letra.get_width() + 12, botao.centery)),
            )

        reinicio = fontes["aviso"].render(
            "TAB REINICIA TODA A JOGATINA", True, (225, 230, 245)
        )
        tela.blit(reinicio, reinicio.get_rect(center=(self.largura // 2, self.altura - 28)))
