import pygame

from recursos import carregar_imagem_recortada


class PessoaFinal:
    """Apresentador que bloqueia o caminho ate sua pergunta ser respondida."""

    ALTURA_IMAGEM = 90

    def __init__(self, x, y_chao, cor, pergunta, nome_imagem=None):
        self.cor = cor
        self.pergunta = pergunta
        self.respondida = False
        self.imagem = self._carregar_imagem(nome_imagem)
        tamanho = self.imagem.get_size() if self.imagem else (100, 160)
        self.rect = pygame.Rect(x, 0, *tamanho)
        self.rect.bottom = y_chao

    def _carregar_imagem(self, nome_imagem):
        """Recorta margens transparentes e preserva a proporcao da arte."""
        if nome_imagem is None:
            return None
        recortada = carregar_imagem_recortada(nome_imagem)
        largura = max(
            1,
            round(
                recortada.get_width()
                * self.ALTURA_IMAGEM
                / recortada.get_height()
            ),
        )
        return pygame.transform.scale(recortada, (largura, self.ALTURA_IMAGEM))

    def bloquear_passagem(self, personagem, rect_anterior):
        """Impede que o apresentador seja atravessado antes da resposta."""
        if self.respondida:
            return
        x_barreira = self.rect.centerx
        if rect_anterior.right <= x_barreira < personagem.rect.right:
            personagem.rect.right = x_barreira
        elif rect_anterior.left >= x_barreira > personagem.rect.left:
            personagem.rect.left = x_barreira

    def desenhar(self, tela, camera_x):
        x = int(self.rect.centerx - camera_x)
        y = self.rect.top
        if self.imagem:
            tela.blit(self.imagem, (self.rect.x - int(camera_x), y))
        else:
            self._desenhar_modelo(tela, x, y)
        if not self.respondida:
            pygame.draw.circle(tela, (255, 255, 255), (x, y - 25), 25)
            fonte = pygame.font.Font(None, 42)
            texto = fonte.render("?", True, (30, 38, 58))
            tela.blit(texto, texto.get_rect(center=(x, y - 23)))

    def _desenhar_modelo(self, tela, x, y):
        """Desenha o apresentador provisorio quando nao ha imagem."""
        pygame.draw.circle(tela, (235, 190, 150), (x, y + 34), 32)
        pygame.draw.rect(tela, self.cor, (x - 38, y + 68, 76, 72), border_radius=14)
        pygame.draw.line(tela, (30, 38, 58), (x - 22, y + 140), (x - 28, y + 160), 10)
        pygame.draw.line(tela, (30, 38, 58), (x + 22, y + 140), (x + 28, y + 160), 10)
