import pygame
from personagem import Personagem

pygame.init()


# ============================================================
# CONFIGURAÇÕES
# ============================================================

LARGURA = 1000
ALTURA = 600

TELA = pygame.display.set_mode(
    (LARGURA, ALTURA)
)

pygame.display.set_caption(
    "Cenário Infinito"
)

FPS = 60
clock = pygame.time.Clock()


# ============================================================
# CLASSE CENARIO
# ============================================================

class Cenario:

    def __init__(self):

        # ====================================================
        # TAMANHO DO CENÁRIO
        # ====================================================

        self.largura = LARGURA
        self.altura = ALTURA


        # ====================================================
        # LIMITE INICIAL DO MUNDO
        # ====================================================

        # O mundo começa aqui.
        #
        # Não existe cenário antes dessa posição.

        self.inicio_mundo = 0


        # ====================================================
        # FUNDO
        # ====================================================

        self.fundo = pygame.Surface(
            (
                self.largura,
                self.altura
            )
        )

        self.fundo.fill(
            (120, 180, 230)
        )


        # ====================================================
        # NUVENS
        # ====================================================

        pygame.draw.circle(
            self.fundo,
            (245, 245, 245),
            (150, 100),
            35
        )

        pygame.draw.circle(
            self.fundo,
            (245, 245, 245),
            (190, 100),
            45
        )

        pygame.draw.circle(
            self.fundo,
            (245, 245, 245),
            (230, 100),
            30
        )


        # ====================================================
        # MONTANHAS
        # ====================================================

        pygame.draw.polygon(
            self.fundo,
            (80, 120, 100),
            [
                (0, 450),
                (180, 250),
                (350, 450)
            ]
        )

        pygame.draw.polygon(
            self.fundo,
            (70, 110, 90),
            [
                (250, 450),
                (500, 220),
                (750, 450)
            ]
        )

        pygame.draw.polygon(
            self.fundo,
            (90, 130, 100),
            [
                (600, 450),
                (820, 280),
                (1000, 450)
            ]
        )


        # ====================================================
        # CHÃO
        # ====================================================

        self.altura_chao = 100

        self.y_chao = (
            ALTURA - self.altura_chao
        )


        self.chao = pygame.Surface(
            (
                self.largura,
                self.altura_chao
            )
        )

        self.chao.fill(
            (100, 65, 35)
        )


        # ====================================================
        # GRAMA
        # ====================================================

        pygame.draw.rect(
            self.chao,
            (60, 150, 60),
            (
                0,
                0,
                self.largura,
                20
            )
        )


        # ====================================================
        # DETALHES DO CHÃO
        # ====================================================

        for x in range(
            20,
            self.largura,
            40
        ):

            pygame.draw.circle(
                self.chao,
                (75, 45, 25),
                (x, 55),
                5
            )


        # ====================================================
        # POSIÇÃO DA CÂMERA
        # ====================================================

        self.camera_x = 0


    # ========================================================
    # MOVER CÂMERA
    # ========================================================

    def mover(self, velocidade):

        self.camera_x += velocidade


        # ----------------------------------------------------
        # LIMITE DO INÍCIO DO MUNDO
        # ----------------------------------------------------

        if self.camera_x < self.inicio_mundo:

            self.camera_x = self.inicio_mundo


    # ========================================================
    # DESENHAR FUNDO
    # ========================================================

    def desenhar_fundo(self, tela):

        inicio = int(
            self.camera_x
            // self.largura
        )


        # ----------------------------------------------------
        # REPETIR O FUNDO
        # ----------------------------------------------------

        for i in range(
            inicio,
            inicio + 3
        ):

            x = (
                i * self.largura
                - self.camera_x
            )

            tela.blit(
                self.fundo,
                (x, 0)
            )


    # ========================================================
    # DESENHAR CHÃO
    # ========================================================

    def desenhar_chao(self, tela):

        inicio = int(
            self.camera_x
            // self.largura
        )


        # ----------------------------------------------------
        # REPETIR O CHÃO
        # ----------------------------------------------------

        for i in range(
            inicio,
            inicio + 3
        ):

            x = (
                i * self.largura
                - self.camera_x
            )

            tela.blit(
                self.chao,
                (
                    x,
                    self.y_chao
                )
            )


    # ========================================================
    # DESENHAR CENÁRIO
    # ========================================================

    def desenhar(self, tela):

        self.desenhar_fundo(tela)

        self.desenhar_chao(tela)


# ============================================================
# CRIAR CENÁRIO
# ============================================================

cenario = Cenario()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

rodando = True

while rodando:

    # ========================================================
    # EVENTOS
    # ========================================================

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:

            rodando = False


    # ========================================================
    # MOVIMENTO DO CENÁRIO
    # ========================================================

    teclas = pygame.key.get_pressed()


    if teclas[pygame.K_RIGHT]:

        cenario.mover(5)


    if teclas[pygame.K_LEFT]:

        cenario.mover(-5)


    # ========================================================
    # DESENHAR
    # ========================================================

    cenario.desenhar(TELA)


    # ========================================================
    # ATUALIZAR
    # ========================================================

    pygame.display.flip()

    clock.tick(FPS)


# ============================================================
# FINALIZAR
# ============================================================

pygame.quit()
