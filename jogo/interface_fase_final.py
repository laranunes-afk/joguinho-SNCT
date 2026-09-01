import pygame

from recursos import carregar_imagem, carregar_imagem_recortada


class InterfaceFaseFinal:
    """Desenha o cenario, o HUD e os avisos da fase final."""

    def __init__(self, largura, altura, y_chao):
        self.largura = largura
        self.altura = altura
        self.y_chao = y_chao
        self.altura_chao = altura - y_chao
        # A arte original tambem possui uma faixa de piso. Usa somente a
        # parte superior com os pilares, pois o chao do jogo e desenhado
        # separadamente logo abaixo.
        cenario_original = carregar_imagem("cenário 4.png")
        area_pilares = pygame.Rect(
            0,
            0,
            cenario_original.get_width(),
            int(cenario_original.get_height() * 0.72),
        )
        pilares = cenario_original.subsurface(area_pilares).copy()
        self.fundo = pygame.transform.scale(pilares, (largura, y_chao))
        self.chao = carregar_imagem_recortada(
            "Chão.png", (largura, self.altura_chao)
        )

    def desenhar_cenario(self, tela, camera_x):
        inicio = int(camera_x // self.largura)
        for indice in range(inicio, inicio + 3):
            x = indice * self.largura - camera_x
            tela.blit(self.fundo, (x, 0))

        for indice in range(inicio, inicio + 3):
            x = indice * self.largura - camera_x
            tela.blit(self.chao, (x, self.y_chao))

    def desenhar_hud(self, tela, lupas, tempo_inicio, total, respondidas):
        fonte_titulo = pygame.font.Font(None, 42)
        fonte_texto = pygame.font.Font(None, 29)
        fonte_contadores = pygame.font.Font(None, 40)
        fonte_cronometro = pygame.font.Font(None, 52)
        painel = pygame.Surface((self.largura, 138), pygame.SRCALPHA)
        painel.fill((8, 13, 30, 220))
        tela.blit(painel, (0, 0))
        pygame.draw.line(tela, (255, 215, 70), (0, 137), (self.largura, 137), 3)

        caixa_esquerda = pygame.Rect(22, 17, 250, 103)
        caixa_direita = pygame.Rect(self.largura - 282, 17, 260, 103)
        caixa_centro = pygame.Rect(
            caixa_esquerda.right + 18,
            17,
            caixa_direita.left - caixa_esquerda.right - 36,
            103,
        )
        for caixa in (caixa_esquerda, caixa_centro, caixa_direita):
            pygame.draw.rect(tela, (25, 35, 55), caixa, border_radius=12)
            pygame.draw.rect(tela, (80, 105, 140), caixa, 2, border_radius=12)

        titulo = fonte_titulo.render("DESAFIO FINAL", True, (255, 225, 90))
        tela.blit(titulo, titulo.get_rect(center=(caixa_esquerda.centerx, 47)))
        progresso = fonte_texto.render(
            f"PERGUNTAS: {respondidas}/{total}", True, (255, 255, 255)
        )
        tela.blit(progresso, progresso.get_rect(center=(caixa_esquerda.centerx, 88)))
        segundos = (
            (pygame.time.get_ticks() - tempo_inicio) // 1000
            if tempo_inicio is not None
            else 0
        )
        cronometro = fonte_cronometro.render(
            f"{segundos // 60:02d}:{segundos % 60:02d}", True, (255, 255, 255)
        )
        tela.blit(cronometro, cronometro.get_rect(center=(caixa_direita.centerx, 46)))
        texto_lupas = fonte_contadores.render(
            f"LUPAS: {lupas}", True, (255, 215, 55)
        )
        tela.blit(texto_lupas, texto_lupas.get_rect(center=(caixa_direita.centerx, 91)))

        instrucoes = ("SIGA EM FRENTE", "FALE COM AS TRES PESSOAS")
        for indice, mensagem in enumerate(instrucoes):
            texto = fonte_texto.render(mensagem, True, (255, 255, 255))
            rect = texto.get_rect(center=(caixa_centro.centerx, 48 + indice * 31))
            tela.blit(texto, rect)

    def desenhar_bonus_checkpoint(self, tela, personagem, camera_x, inicio):
        duracao = 2400
        decorrido = pygame.time.get_ticks() - inicio
        if decorrido >= duracao:
            return
        progresso = decorrido / duracao
        fonte = pygame.font.Font(None, 18)
        base = fonte.render("+5 LUPAS", False, (255, 205, 45))
        texto = pygame.transform.scale(base, (base.get_width() * 2, base.get_height() * 2))
        texto.set_alpha(int(255 * (1 - progresso)))
        x = int(personagem.rect.centerx - camera_x)
        y = int(personagem.rect.top - 12 - progresso * 38)
        tela.blit(texto, texto.get_rect(midbottom=(x, y)))
