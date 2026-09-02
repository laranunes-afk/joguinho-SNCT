import pygame

from recursos import (
    carregar_imagem,
    carregar_imagem_recortada,
    renderizar_texto_contornado,
)


ALTURA_PAINEL = 138
DURACAO_BONUS = 2400
SUBIDA_BONUS = 38
COR_DESTAQUE = (255, 215, 70)
COR_TEXTO = (255, 255, 255)


class InterfaceFaseFinal:
    """Desenha o cenário e as informações da fase final."""

    def __init__(self, largura, altura, y_chao):
        self.largura = largura
        self.y_chao = y_chao
        self.altura_chao = altura - y_chao
        self.fundo, self.chao = self._carregar_cenario()
        self._criar_fontes()
        self._criar_elementos_hud()
        self.texto_bonus = self._criar_texto_bonus()

    def _carregar_cenario(self):
        """Separa os pilares do piso contido na arte original."""
        cenario_original = carregar_imagem("cenário-4-pixilart.png")
        area_pilares = pygame.Rect(
            0,
            0,
            cenario_original.get_width(),
            int(cenario_original.get_height() * 0.72),
        )
        pilares = cenario_original.subsurface(area_pilares).copy()
        fundo = pygame.transform.scale(pilares, (self.largura, self.y_chao))
        chao = carregar_imagem_recortada(
            "Chão.png",
            (self.largura, self.altura_chao),
        )
        return fundo, chao

    def _criar_fontes(self):
        self.fonte_titulo = pygame.font.Font(None, 42)
        self.fonte_texto = pygame.font.Font(None, 29)
        self.fonte_contadores = pygame.font.Font(None, 40)
        self.fonte_cronometro = pygame.font.Font(None, 52)
        self.fonte_bonus = pygame.font.Font(None, 18)

    def _criar_elementos_hud(self):
        self.caixa_esquerda = pygame.Rect(22, 17, 250, 103)
        self.caixa_direita = pygame.Rect(self.largura - 282, 17, 260, 103)
        largura_centro = max(
            1,
            self.caixa_direita.left - self.caixa_esquerda.right - 36,
        )
        self.caixa_centro = pygame.Rect(
            self.caixa_esquerda.right + 18,
            17,
            largura_centro,
            103,
        )

        self.painel_hud = pygame.Surface(
            (self.largura, ALTURA_PAINEL),
            pygame.SRCALPHA,
        )
        self.painel_hud.fill((8, 13, 30, 220))
        pygame.draw.line(
            self.painel_hud,
            COR_DESTAQUE,
            (0, ALTURA_PAINEL - 1),
            (self.largura, ALTURA_PAINEL - 1),
            3,
        )
        for caixa in (
            self.caixa_esquerda,
            self.caixa_centro,
            self.caixa_direita,
        ):
            pygame.draw.rect(
                self.painel_hud,
                (25, 35, 55),
                caixa,
                border_radius=12,
            )
            pygame.draw.rect(
                self.painel_hud,
                (80, 105, 140),
                caixa,
                2,
                border_radius=12,
            )

        self.titulo = self.fonte_titulo.render(
            "DESAFIO FINAL",
            True,
            (255, 225, 90),
        )
        self.instrucoes = [
            self.fonte_texto.render(mensagem, True, COR_TEXTO)
            for mensagem in ("SIGA EM FRENTE", "FALE COM AS TRES PESSOAS")
        ]

    def _criar_texto_bonus(self):
        base = renderizar_texto_contornado(
            self.fonte_bonus,
            "+5 LUPAS",
            (255, 205, 45),
        )
        return pygame.transform.scale(
            base,
            (base.get_width() * 2, base.get_height() * 2),
        )

    def desenhar_cenario(self, tela, camera_x):
        inicio = int(camera_x // self.largura)
        for indice in range(inicio, inicio + 3):
            x = indice * self.largura - camera_x
            tela.blit(self.fundo, (x, 0))
            tela.blit(self.chao, (x, self.y_chao))

    @staticmethod
    def _segundos_decorridos(tempo_inicio):
        if tempo_inicio is None:
            return 0
        return (pygame.time.get_ticks() - tempo_inicio) // 1000

    def desenhar_hud(self, tela, lupas, tempo_inicio, total, respondidas):
        tela.blit(self.painel_hud, (0, 0))
        tela.blit(
            self.titulo,
            self.titulo.get_rect(center=(self.caixa_esquerda.centerx, 47)),
        )

        progresso = self.fonte_texto.render(
            f"PERGUNTAS: {respondidas}/{total}",
            True,
            COR_TEXTO,
        )
        tela.blit(
            progresso,
            progresso.get_rect(center=(self.caixa_esquerda.centerx, 88)),
        )

        for indice, texto in enumerate(self.instrucoes):
            tela.blit(
                texto,
                texto.get_rect(
                    center=(self.caixa_centro.centerx, 48 + indice * 31)
                ),
            )

        segundos = self._segundos_decorridos(tempo_inicio)
        cronometro = self.fonte_cronometro.render(
            f"{segundos // 60:02d}:{segundos % 60:02d}",
            True,
            COR_TEXTO,
        )
        tela.blit(
            cronometro,
            cronometro.get_rect(center=(self.caixa_direita.centerx, 46)),
        )
        texto_lupas = self.fonte_contadores.render(
            f"LUPAS: {lupas}",
            True,
            (255, 215, 55),
        )
        tela.blit(
            texto_lupas,
            texto_lupas.get_rect(center=(self.caixa_direita.centerx, 91)),
        )

    def desenhar_bonus_checkpoint(self, tela, personagem, camera_x, inicio):
        decorrido = pygame.time.get_ticks() - inicio
        if decorrido >= DURACAO_BONUS:
            return

        progresso = decorrido / DURACAO_BONUS
        texto = self.texto_bonus.copy()
        texto.set_alpha(int(255 * (1 - progresso)))
        x = int(personagem.rect.centerx - camera_x)
        y = int(personagem.rect.top - 12 - progresso * SUBIDA_BONUS)
        tela.blit(texto, texto.get_rect(midbottom=(x, y)))
