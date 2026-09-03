import pygame

from recursos import renderizar_texto_contornado


class TesouroFinal:
    """Controla a passagem secreta encontrada à esquerda da fase."""

    DURACAO_CAMINHADA = 2000
    DURACAO_AVISO = 2500
    RECOMPENSA = 20
    X_RETORNO = 40
    Y_AVISO = 175

    def __init__(self):
        self.inicio_caminhada = None
        self.coletado = False
        self.aviso_ate = 0
        self.texto_aviso = None

    def _obter_texto_aviso(self):
        """Cria o texto na primeira exibição e o reutiliza nas seguintes."""
        if self.texto_aviso is not None:
            return self.texto_aviso

        fonte = pygame.font.Font(None, 48)
        self.texto_aviso = renderizar_texto_contornado(
            fonte,
            f"TESOURO ENCONTRADO: +{self.RECOMPENSA} LUPAS",
            (255, 215, 55),
            espessura=2,
            antialias=True,
        )
        return self.texto_aviso

    @property
    def em_andamento(self):
        return self.inicio_caminhada is not None

    def tentar_iniciar(self, personagem, agora):
        if not self.coletado and personagem.rect.right <= 0:
            self.inicio_caminhada = agora

    def atualizar(self, personagem, y_chao, agora):
        """Mantém a caminhada secreta e retorna a recompensa ao concluí-la."""
        personagem.caminhar_automaticamente(-1)
        if agora - self.inicio_caminhada < self.DURACAO_CAMINHADA:
            return 0

        self.coletado = True
        self.inicio_caminhada = None
        self.aviso_ate = agora + self.DURACAO_AVISO
        personagem.posicionar_no_chao(self.X_RETORNO, y_chao)
        return self.RECOMPENSA

    def limitar_saida_usada(self, personagem):
        if self.coletado:
            personagem.rect.left = max(0, personagem.rect.left)

    def desenhar_aviso(self, tela, largura):
        if pygame.time.get_ticks() >= self.aviso_ate:
            return
        texto = self._obter_texto_aviso()
        rect = texto.get_rect(
            center=(largura // 2, self.Y_AVISO),
        )
        tela.blit(texto, rect)
