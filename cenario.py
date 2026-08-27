import pygame

from recursos import carregar_imagem


class Cenario:
    """Cenário infinito com aparência própria para cada fase."""

    def __init__(self, largura, altura, fase=1):
        """Prepara as superfícies e medidas do cenário da fase."""
        self.largura = largura
        self.altura = altura
        self.fase = fase
        self.inicio_mundo = 0
        self.camera_x = 0
        # Mantém o chão na mesma altura visual em todas as fases.
        self.altura_chao = int(altura * 0.35)
        self.y_chao = self.altura - self.altura_chao

        self.fundo = pygame.Surface((self.largura, self.altura))
        self.chao = pygame.Surface((self.largura, self.altura_chao))

        if fase == 1:
            self._criar_floresta()
        elif fase == 2:
            self._criar_deserto()
        else:
            self._criar_noite_gelada()

        self._criar_chao_comum()

    def _criar_floresta(self):
        """Desenha o fundo e o chão usados na primeira fase."""
        fundo_floresta = carregar_imagem(
            "pixilart-drawing (1).png",
            (self.largura, self.altura)
        )
        self.fundo.blit(fundo_floresta, (0, 0))

    def _criar_deserto(self):
        """Monta o cenário da segunda fase usando as imagens do deserto."""
        fundo_deserto = carregar_imagem(
            "cenário2.png",
            (self.largura, self.altura)
        )
        self.fundo.blit(fundo_deserto, (0, 0))

    def _criar_chao_comum(self):
        """Aplica a mesma imagem de chão em todas as fases."""
        imagem_original = carregar_imagem(
            "Chão.png",
            fundo_transparente=True
        )
        limites = pygame.mask.from_surface(
            imagem_original
        ).get_bounding_rects()
        area_chao = limites[0].unionall(limites)
        imagem_chao = imagem_original.subsurface(area_chao).copy()
        imagem_chao = pygame.transform.scale(
            imagem_chao,
            (self.largura, self.altura_chao)
        )
        self.chao.fill((0, 0, 0, 0))
        self.chao.blit(imagem_chao, (0, 0))

    def _criar_noite_gelada(self):
        """Carrega o fundo estrelado usado na terceira fase."""
        fundo_noturno = carregar_imagem(
            "cenário-3.png",
            (self.largura, self.altura)
        )
        self.fundo.blit(fundo_noturno, (0, 0))

    def desenhar_fundo(self, tela):
        """Repete o fundo para cobrir a região visível da câmera."""
        inicio = int(self.camera_x // self.largura)

        for indice in range(inicio, inicio + 3):
            x = indice * self.largura - self.camera_x
            tela.blit(self.fundo, (x, 0))

    def desenhar_chao(self, tela):
        """Repete a superfície do chão ao longo do cenário."""
        inicio = int(self.camera_x // self.largura)

        for indice in range(inicio, inicio + 3):
            x = indice * self.largura - self.camera_x
            tela.blit(self.chao, (x, self.y_chao))

    def desenhar(self, tela):
        """Desenha o fundo e o chão da fase."""
        self.desenhar_fundo(tela)
        self.desenhar_chao(tela)
