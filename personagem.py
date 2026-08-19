import pygame


class Personagem:

    def __init__(self, x, y, largura=50, altura=80):

        # ====================================================
        # RETÂNGULO DO PERSONAGEM
        # ====================================================

        self.rect = pygame.Rect(
            x,
            y,
            largura,
            altura
        )


        # ====================================================
        # MOVIMENTO
        # ====================================================

        self.velocidade = 5

        self.velocidade_y = 0


        # ====================================================
        # PULO
        # ====================================================

        self.forca_pulo = -14

        self.gravidade = 0.6

        self.no_chao = False


        # ====================================================
        # IMAGEM TEMPORÁRIA
        # ====================================================

        self.cor = (200, 50, 50)


    # ========================================================
    # MOVIMENTO
    # ========================================================

    def mover(self):

        teclas = pygame.key.get_pressed()


        # ----------------------------------------------------
        # ESQUERDA
        # ----------------------------------------------------

        if (
            teclas[pygame.K_a]
            or teclas[pygame.K_LEFT]
        ):

            self.rect.x -= self.velocidade


        # ----------------------------------------------------
        # DIREITA
        # ----------------------------------------------------

        if (
            teclas[pygame.K_d]
            or teclas[pygame.K_RIGHT]
        ):

            self.rect.x += self.velocidade


    # ========================================================
    # PULO
    # ========================================================

    def pular(self):

        teclas = pygame.key.get_pressed()


        if (
            teclas[pygame.K_w]
            or teclas[pygame.K_UP]
        ):

            if self.no_chao:

                self.velocidade_y = self.forca_pulo

                self.no_chao = False


    # ========================================================
    # GRAVIDADE
    # ========================================================

    def aplicar_gravidade(self, y_chao):

        self.velocidade_y += self.gravidade

        self.rect.y += int(
            self.velocidade_y
        )


        # ----------------------------------------------------
        # COLISÃO COM O CHÃO
        # ----------------------------------------------------

        if self.rect.bottom >= y_chao:

            self.rect.bottom = y_chao

            self.velocidade_y = 0

            self.no_chao = True


    # ========================================================
    # ATUALIZAR PERSONAGEM
    # ========================================================

    def atualizar(self, y_chao):

        self.mover()

        self.pular()

        self.aplicar_gravidade(
            y_chao
        )


    # ========================================================
    # DESENHAR PERSONAGEM
    # ========================================================

    def desenhar(self, tela):

        pygame.draw.rect(
            tela,
            self.cor,
            self.rect
        )
