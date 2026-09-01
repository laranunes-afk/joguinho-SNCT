import pygame

from recursos import renderizar_texto_contornado


class TesouroFinal:
    """Passagem secreta encontrada ao sair pelo lado esquerdo da fase."""

    DURACAO_CAMINHADA = 2000
    RECOMPENSA = 20

    def __init__(self):
        self.inicio_caminhada = None
        self.coletado = False
        self.aviso_ate = 0

    @property
    def em_andamento(self):
        return self.inicio_caminhada is not None

    def tentar_iniciar(self, personagem, agora):
        if not self.coletado and personagem.rect.right <= 0:
            self.inicio_caminhada = agora

    def atualizar(self, personagem, y_chao, agora):
        """Mantem a caminhada secreta e retorna as lupas conquistadas."""
        personagem.rect.x -= personagem.velocidade
        personagem.em_movimento = True
        personagem.virado_para_esquerda = True
        personagem.atualizar_animacao()
        if agora - self.inicio_caminhada < self.DURACAO_CAMINHADA:
            return 0

        self.coletado = True
        self.inicio_caminhada = None
        self.aviso_ate = agora + 2500
        personagem.rect.left = 40 + personagem.margem_hitbox_x
        personagem.rect.bottom = y_chao
        personagem.velocidade_y = 0
        personagem.no_chao = True
        return self.RECOMPENSA

    def limitar_saida_usada(self, personagem):
        if self.coletado:
            personagem.rect.left = max(0, personagem.rect.left)

    def desenhar_aviso(self, tela, largura):
        if pygame.time.get_ticks() >= self.aviso_ate:
            return
        fonte = pygame.font.Font(None, 48)
        mensagem = f"TESOURO ENCONTRADO: +{self.RECOMPENSA} LUPAS"
        texto = renderizar_texto_contornado(
            fonte,
            mensagem,
            (255, 215, 55),
            espessura=2,
            antialias=True,
        )
        rect = texto.get_rect(center=(largura // 2, 175))
        tela.blit(texto, rect)
