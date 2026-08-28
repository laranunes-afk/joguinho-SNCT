import pygame

from recursos import carregar_imagem


class Personagem:

    def __init__(self, x, y, largura=50, altura=80):
        """Cria a personagem, configura a física e carrega sua animação."""

        # ====================================================
        # RETÂNGULO DO PERSONAGEM
        # ====================================================

        self.largura_visual = largura
        self.altura_visual = altura
        largura_hitbox = max(1, int(largura * 0.68))
        altura_hitbox = max(1, int(altura * 0.85))
        self.margem_hitbox_x = (largura - largura_hitbox) // 2
        self.rect = pygame.Rect(
            x + self.margem_hitbox_x,
            y + altura - altura_hitbox,
            largura_hitbox,
            altura_hitbox
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

        # Fica ativo quando a personagem entra em um buraco, impedindo que
        # ela volte a pousar no chão do outro lado durante a mesma queda.
        self.caindo_no_buraco = False


        # ====================================================
        # IMAGEM TEMPORÁRIA
        # ====================================================

        sprites = carregar_imagem(
            "Personagem NÃO PRONTA.png",
            fundo_transparente=True
        )
        self.quadros_direita = []

        # A primeira linha da spritesheet contém oito quadros de caminhada.
        for indice in range(8):
            quadro = sprites.subsurface(
                pygame.Rect(25 + indice * 175, 85, 190, 245)
            )
            quadro_redimensionado = pygame.transform.scale(
                quadro,
                (largura, altura)
            )
            quadro_redimensionado.set_colorkey((0, 0, 0))
            self.quadros_direita.append(quadro_redimensionado)

        self.quadros_esquerda = [
            pygame.transform.flip(quadro, True, False)
            for quadro in self.quadros_direita
        ]
        self.indice_quadro = 0
        self.ultimo_quadro = pygame.time.get_ticks()
        self.em_movimento = False
        self.virado_para_esquerda = False


    # ========================================================
    # MOVIMENTO
    # ========================================================

    def mover(self):
        """Lê as teclas horizontais e desloca a personagem."""

        teclas = pygame.key.get_pressed()
        deslocamento_x = 0


        # ----------------------------------------------------
        # ESQUERDA
        # ----------------------------------------------------

        if (
            teclas[pygame.K_a]
            or teclas[pygame.K_LEFT]
        ):

            deslocamento_x -= self.velocidade


        # ----------------------------------------------------
        # DIREITA
        # ----------------------------------------------------

        if (
            teclas[pygame.K_d]
            or teclas[pygame.K_RIGHT]
        ):

            deslocamento_x += self.velocidade

        self.rect.x += deslocamento_x
        self.em_movimento = deslocamento_x != 0

        if deslocamento_x != 0:
            self.virado_para_esquerda = deslocamento_x < 0


    # ========================================================
    # PULO
    # ========================================================

    def pular(self):
        """Inicia um pulo quando a tecla é pressionada sobre o chão."""

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

    def aplicar_gravidade(self, y_chao, esta_sobre_buraco=False):
        """Aplica a queda vertical e resolve o contato com o chão."""

        self.velocidade_y += self.gravidade

        self.rect.y += int(
            self.velocidade_y
        )


        # ----------------------------------------------------
        # COLISÃO COM O CHÃO
        # ----------------------------------------------------

        if self.rect.bottom >= y_chao and not esta_sobre_buraco:

            self.rect.bottom = y_chao

            self.velocidade_y = 0

            self.no_chao = True


    # ========================================================
    # ATUALIZAR PERSONAGEM
    # ========================================================

    def atualizar(self, y_chao, verificar_buraco=None):
        """Atualiza movimento, pulo, gravidade e animação em um quadro."""

        self.mover()

        esta_sobre_buraco = (
            verificar_buraco(self)
            if verificar_buraco is not None
            else False
        )

        if esta_sobre_buraco:
            self.no_chao = False

            if self.rect.bottom >= y_chao:
                self.caindo_no_buraco = True

        self.pular()

        self.aplicar_gravidade(
            y_chao,
            esta_sobre_buraco or self.caindo_no_buraco
        )

        self.atualizar_animacao()


    def atualizar_animacao(self):
        """Avança os quadros enquanto a personagem estiver caminhando."""
        if not self.em_movimento:
            self.indice_quadro = 0
            return

        agora = pygame.time.get_ticks()
        if agora - self.ultimo_quadro >= 90:
            self.indice_quadro = (
                self.indice_quadro + 1
            ) % len(self.quadros_direita)
            self.ultimo_quadro = agora


    # ========================================================
    # DESENHAR PERSONAGEM
    # ========================================================

    def desenhar(self, tela, camera_x=0):
        """Desenha o quadro atual da personagem na posição da câmera."""
        quadros = (
            self.quadros_esquerda
            if self.virado_para_esquerda
            else self.quadros_direita
        )
        quadro = quadros[self.indice_quadro]
        personagem_na_tela = quadro.get_rect(
            midbottom=(
                self.rect.centerx - int(camera_x),
                self.rect.bottom
            )
        )
        tela.blit(quadro, personagem_na_tela)
