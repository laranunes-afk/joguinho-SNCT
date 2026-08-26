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

    def _criar_floresta(self):
        """Desenha o fundo e o chão usados na primeira fase."""
        self.fundo.fill((120, 180, 230))

        pygame.draw.circle(self.fundo, (245, 245, 245), (150, 100), 35)
        pygame.draw.circle(self.fundo, (245, 245, 245), (190, 100), 45)
        pygame.draw.circle(self.fundo, (245, 245, 245), (230, 100), 30)

        pygame.draw.polygon(
            self.fundo,
            (80, 120, 100),
            [(0, self.y_chao), (180, 250), (360, self.y_chao)]
        )
        pygame.draw.polygon(
            self.fundo,
            (70, 110, 90),
            [(280, self.y_chao), (520, 220), (780, self.y_chao)]
        )
        pygame.draw.polygon(
            self.fundo,
            (90, 130, 100),
            [(650, self.y_chao), (850, 280), (self.largura, self.y_chao)]
        )

        self.chao.fill((100, 65, 35))
        pygame.draw.rect(self.chao, (60, 150, 60), (0, 0, self.largura, 20))

        for x in range(20, self.largura, 40):
            pygame.draw.circle(self.chao, (75, 45, 25), (x, 55), 5)

    def _criar_deserto(self):
        """Monta o cenário da segunda fase usando as imagens do deserto."""
        fundo_deserto = carregar_imagem(
            "pixilart-drawing (1).png",
            (self.largura, self.altura)
        )
        self.fundo.blit(fundo_deserto, (0, 0))

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
        self.chao.blit(imagem_chao, (0, 0))

    def _criar_noite_gelada(self):
        """Desenha o fundo e o chão usados na terceira fase."""
        self.fundo.fill((24, 38, 78))

        pygame.draw.circle(self.fundo, (238, 240, 220), (150, 110), 55)
        pygame.draw.circle(self.fundo, (24, 38, 78), (175, 90), 50)

        for indice in range(28):
            x = (indice * 137 + 45) % self.largura
            y = 35 + (indice * 83) % max(100, self.altura // 2)
            pygame.draw.circle(self.fundo, (235, 240, 255), (x, y), 2)

        pygame.draw.polygon(
            self.fundo,
            (55, 72, 105),
            [(0, self.y_chao), (220, 230), (440, self.y_chao)]
        )
        pygame.draw.polygon(
            self.fundo,
            (65, 82, 115),
            [(360, self.y_chao), (650, 190), (950, self.y_chao)]
        )
        pygame.draw.polygon(
            self.fundo,
            (225, 235, 245),
            [(155, 320), (220, 230), (285, 320)]
        )
        pygame.draw.polygon(
            self.fundo,
            (225, 235, 245),
            [(575, 280), (650, 190), (730, 280)]
        )

        self.chao.fill((55, 68, 90))
        pygame.draw.rect(self.chao, (225, 235, 245), (0, 0, self.largura, 22))

        for x in range(25, self.largura, 60):
            pygame.draw.circle(self.chao, (90, 110, 135), (x, 60), 4)

    def seguir_personagem(self, personagem):
        """Move a câmera horizontal quando a personagem avança ou retorna."""
        margem = self.largura * 0.35

        if personagem.rect.right - self.camera_x > self.largura - margem:
            nova_camera = personagem.rect.right - (self.largura - margem)

            if nova_camera > self.camera_x:
                self.camera_x = nova_camera

        elif personagem.rect.left - self.camera_x < margem:
            nova_camera = personagem.rect.left - margem

            if nova_camera < self.camera_x:
                self.camera_x = max(self.inicio_mundo, nova_camera)

        if self.camera_x < self.inicio_mundo:
            self.camera_x = self.inicio_mundo

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
