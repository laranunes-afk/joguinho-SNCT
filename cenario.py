import pygame


class Cenario:
    """Cenário infinito com aparência própria para cada fase."""

    def __init__(self, largura, altura, fase=1):
        self.largura = largura
        self.altura = altura
        self.fase = fase
        self.inicio_mundo = 0
        self.camera_x = 0
        self.altura_chao = 100
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
        self.fundo.fill((238, 178, 92))

        pygame.draw.circle(
            self.fundo,
            (255, 225, 90),
            (self.largura - 160, 120),
            65
        )
        pygame.draw.ellipse(
            self.fundo,
            (215, 145, 65),
            (-180, self.y_chao - 170, self.largura // 2 + 300, 260)
        )
        pygame.draw.ellipse(
            self.fundo,
            (225, 158, 73),
            (self.largura // 3, self.y_chao - 140, self.largura, 230)
        )

        self.chao.fill((205, 135, 55))
        pygame.draw.rect(self.chao, (235, 180, 85), (0, 0, self.largura, 18))

        for x in range(30, self.largura, 70):
            pygame.draw.line(
                self.chao,
                (175, 110, 45),
                (x, 55),
                (x + 18, 55),
                3
            )

    def _criar_noite_gelada(self):
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

    def mover(self, velocidade):
        self.camera_x += velocidade

        if self.camera_x < self.inicio_mundo:
            self.camera_x = self.inicio_mundo

    def seguir_personagem(self, personagem):
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
        inicio = int(self.camera_x // self.largura)

        for indice in range(inicio, inicio + 3):
            x = indice * self.largura - self.camera_x
            tela.blit(self.fundo, (x, 0))

    def desenhar_chao(self, tela):
        inicio = int(self.camera_x // self.largura)

        for indice in range(inicio, inicio + 3):
            x = indice * self.largura - self.camera_x
            tela.blit(self.chao, (x, self.y_chao))

    def desenhar(self, tela):
        self.desenhar_fundo(tela)
        self.desenhar_chao(tela)
