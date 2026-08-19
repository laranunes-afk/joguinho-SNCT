import pygame

pygame.init()


# ============================================================
# CONFIGURAÇÕES
# ============================================================

LARGURA = 1000
ALTURA = 600

TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cenário Infinito")

FPS = 60
clock = pygame.time.Clock()


# ============================================================
# CLASSE CENARIO
# ============================================================

class Cenario:

    def __init__(self):

        # ----------------------------------------------------
        # TAMANHO DE CADA CENÁRIO
        # ----------------------------------------------------

        self.largura = LARGURA
        self.altura = ALTURA


        # ----------------------------------------------------
        # CHÃO
        # ----------------------------------------------------

        self.altura_chao = 100

        self.y_chao = (
            ALTURA - self.altura_chao
        )


        # ====================================================
        # CRIAR FUNDO
        # ====================================================

        self.fundo = pygame.Surface(
            (self.largura, self.altura)
        )

        self.fundo.fill(
            (120, 180, 230)
        )


        # ----------------------------------------------------
        # NUVENS
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # MONTANHAS
        # ----------------------------------------------------

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
        # CRIAR CHÃO
        # ====================================================

        self.chao = pygame.Surface(
            (self.largura, self.altura_chao)
        )

        self.chao.fill(
            (100, 65, 35)
        )


        # ----------------------------------------------------
        # GRAMA
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # DETALHES DO CHÃO
        # ----------------------------------------------------

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


    # ========================================================
    # DESENHAR
    # ========================================================

    def desenhar(self, tela, camera_x):

        # ----------------------------------------------------
        # DESENHAR FUNDO
        # ----------------------------------------------------

        inicio = int(
            camera_x // self.largura
        )

        for i in range(
            inicio,
            inicio + 3
        ):

            x = (
                i * self.largura
                - camera_x
            )

            tela.blit(
                self.fundo,
                (x, 0)
            )


        # ----------------------------------------------------
        # DESENHAR CHÃO
        # ----------------------------------------------------

        for i in range(
            inicio,
            inicio + 3
        ):

            x = (
                i * self.largura
                - camera_x
            )

            tela.blit(
                self.chao,
                (
                    x,
                    self.y_chao
                )
            )


# ============================================================
# CRIAR CENÁRIO
# ============================================================

cenario = Cenario()


# ============================================================
# PERSONAGEM
# ============================================================

personagem = pygame.Rect(
    150,
    cenario.y_chao - 80,
    50,
    80
)

velocidade = 5


# ============================================================
# POSIÇÃO DO PERSONAGEM NO MUNDO
# ============================================================

# Esta é a posição real do personagem no mapa.

player_world_x = 150


# ============================================================
# CÂMERA
# ============================================================

camera_x = 0


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
    # TECLAS
    # ========================================================

    teclas = pygame.key.get_pressed()


    # ========================================================
    # MOVIMENTO PARA DIREITA
    # ========================================================

    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:

        player_world_x += velocidade


    # ========================================================
    # MOVIMENTO PARA ESQUERDA
    # ========================================================

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:

        player_world_x -= velocidade


    # ========================================================
    # LIMITE ABSOLUTO DO MAPA
    # ========================================================

    # O mundo começa em X = 150.
    #
    # Portanto, nunca podemos voltar para antes desse ponto.

    if player_world_x < 150:

        player_world_x = 150


    # ========================================================
    # CÂMERA
    # ========================================================

    # A câmera acompanha o personagem.

    camera_x = (
        player_world_x - 300
    )


    # --------------------------------------------------------
    # A câmera nunca mostra uma área antes do começo do mapa.
    # --------------------------------------------------------

    if camera_x < 0:

        camera_x = 0


    # ========================================================
    # POSIÇÃO DO PERSONAGEM NA TELA
    # ========================================================

    personagem.x = int(
        player_world_x - camera_x
    )


    # ========================================================
    # LIMITES VISUAIS DO PERSONAGEM
    # ========================================================

    if personagem.left < 0:

        personagem.left = 0


    if personagem.right > LARGURA:

        personagem.right = LARGURA


    # ========================================================
    # DESENHAR
    # ========================================================

    cenario.desenhar(
        TELA,
        camera_x
    )


    # ========================================================
    # PERSONAGEM
    # ========================================================

    pygame.draw.rect(
        TELA,
        (200, 50, 50),
        personagem
    )


    # ========================================================
    # ATUALIZAR
    # ========================================================

    pygame.display.flip()

    clock.tick(FPS)


# ============================================================
# FINALIZAR
# ============================================================

pygame.quit()