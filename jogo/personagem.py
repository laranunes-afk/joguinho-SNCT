import pygame

from recursos import carregar_imagem


ARQUIVO_SPRITES = "personagem-transparente.png"
TOTAL_QUADROS_CORRIDA = 8
TOTAL_POSES = TOTAL_QUADROS_CORRIDA + 1
INTERVALO_ANIMACAO_MS = 90
TAMANHO_MINIMO_COMPONENTE = 100


class Personagem:
    """Personagem jogável com movimento, física e animação."""

    def __init__(self, x, y, largura=50, altura=80):
        self.largura_visual = largura
        self.altura_visual = altura

        # A hitbox ignora chapéu, cabelo e braços, mas termina nos pés.
        largura_hitbox = max(1, round(largura * 0.56))
        altura_hitbox = max(1, round(altura * 0.88))
        self.margem_hitbox_x = (largura - largura_hitbox) // 2
        self.rect = pygame.Rect(
            x + self.margem_hitbox_x,
            y + altura - altura_hitbox,
            largura_hitbox,
            altura_hitbox,
        )

        self.velocidade = 5
        self.velocidade_y = 0
        self.forca_pulo = -14
        self.gravidade = 0.6
        self.no_chao = False

        # Depois de entrar em um buraco, não pode pousar na outra borda
        # durante a mesma queda. O estado é limpo ao reposicionar.
        self.caindo_no_buraco = False

        poses = self._carregar_quadros(largura, altura)
        self.quadro_parado_direita = poses[0]
        self.quadro_parado_esquerda = pygame.transform.flip(
            poses[0], True, False
        )
        self.quadros_direita = poses[1:]
        self.quadros_esquerda = [
            pygame.transform.flip(quadro, True, False)
            for quadro in self.quadros_direita
        ]
        self.indice_quadro = 0
        self.ultimo_quadro = pygame.time.get_ticks()
        self.em_movimento = False
        self.virado_para_esquerda = False

    @staticmethod
    def _localizar_quadros(sprites):
        """Localiza cada pose pelos pixels conectados, sem recortes fixos."""
        mascara = pygame.mask.from_surface(sprites, threshold=1)
        limites = [
            componente.get_bounding_rects()[0]
            for componente in mascara.connected_components(
                TAMANHO_MINIMO_COMPONENTE
            )
        ]

        # A margem de 80 px exclui o começo da segunda linha da spritesheet.
        limite_primeira_linha = sprites.get_height() // 2 - 80
        primeira_linha = sorted(
            (area for area in limites if area.y < limite_primeira_linha),
            key=lambda area: area.x,
        )
        return primeira_linha

    @classmethod
    def _carregar_quadros(cls, largura, altura):
        sprites = carregar_imagem(ARQUIVO_SPRITES)
        limites = cls._localizar_quadros(sprites)
        if len(limites) != TOTAL_POSES:
            raise ValueError(
                f"Esperadas {TOTAL_POSES} poses da personagem; "
                f"encontrados {len(limites)}"
            )

        largura_base = max(area.width for area in limites)
        altura_base = max(area.height for area in limites)
        escala = min(largura / largura_base, altura / altura_base)
        return [
            cls._preparar_quadro(sprites, area, largura, altura, escala)
            for area in limites
        ]

    @staticmethod
    def _preparar_quadro(sprites, area, largura, altura, escala):
        """Recorta uma pose e alinha seus pés num canvas comum."""
        quadro = sprites.subsurface(area).copy()
        tamanho = (
            max(1, round(area.width * escala)),
            max(1, round(area.height * escala)),
        )
        quadro = pygame.transform.scale(quadro, tamanho)

        alinhado = pygame.Surface((largura, altura), pygame.SRCALPHA)
        alinhado.blit(
            quadro,
            ((largura - tamanho[0]) // 2, altura - tamanho[1]),
        )
        return alinhado

    @staticmethod
    def _direcao_horizontal(teclas):
        esquerda = teclas[pygame.K_a] or teclas[pygame.K_LEFT]
        direita = teclas[pygame.K_d] or teclas[pygame.K_RIGHT]
        return int(direita) - int(esquerda)

    def mover(self):
        """Lê as teclas horizontais e desloca a hitbox."""
        direcao = self._direcao_horizontal(pygame.key.get_pressed())
        self.rect.x += direcao * self.velocidade
        self.em_movimento = direcao != 0
        if self.em_movimento:
            self.virado_para_esquerda = direcao < 0

    def pular(self):
        """Inicia o pulo somente quando a personagem está apoiada."""
        teclas = pygame.key.get_pressed()
        pediu_pulo = teclas[pygame.K_w] or teclas[pygame.K_UP]
        if pediu_pulo and self.no_chao:
            self.velocidade_y = self.forca_pulo
            self.no_chao = False

    def posicionar_no_chao(self, x_visual, y_chao):
        """Restaura posição e estado físico em um ponto seguro."""
        self.rect.left = x_visual + self.margem_hitbox_x
        self.rect.bottom = y_chao
        self.velocidade_y = 0
        self.no_chao = True
        self.caindo_no_buraco = False

    def rebater(self, intensidade=0.55):
        """Impulsiona a personagem após cair sobre um inimigo."""
        self.velocidade_y = self.forca_pulo * intensidade
        self.no_chao = False

    def caminhar_automaticamente(self, direcao):
        """Move sem ler o teclado, usado em sequências controladas."""
        self.rect.x += direcao * self.velocidade
        self.em_movimento = True
        self.virado_para_esquerda = direcao < 0
        self.atualizar_animacao()

    def aplicar_gravidade(self, y_chao, ignorar_chao=False):
        """Aplica a queda e resolve o contato com o piso da fase."""
        self.velocidade_y += self.gravidade
        self.rect.y += int(self.velocidade_y)

        if self.rect.bottom >= y_chao and not ignorar_chao:
            self.rect.bottom = y_chao
            self.velocidade_y = 0
            self.no_chao = True

    def atualizar(self, y_chao, verificar_buraco=None):
        """Atualiza entrada, física e animação por um quadro."""
        self.mover()
        sobre_buraco = bool(verificar_buraco and verificar_buraco(self))

        if sobre_buraco:
            self.no_chao = False
            if self.rect.bottom >= y_chao:
                self.caindo_no_buraco = True

        self.pular()
        self.aplicar_gravidade(
            y_chao,
            ignorar_chao=sobre_buraco or self.caindo_no_buraco,
        )
        self.atualizar_animacao()

    def atualizar_animacao(self):
        """Avança a caminhada em intervalos constantes."""
        if not self.em_movimento:
            self.indice_quadro = 0
            self.ultimo_quadro = pygame.time.get_ticks()
            return

        agora = pygame.time.get_ticks()
        if agora - self.ultimo_quadro >= INTERVALO_ANIMACAO_MS:
            self.indice_quadro = (
                self.indice_quadro + 1
            ) % len(self.quadros_direita)
            self.ultimo_quadro = agora

    def desenhar(self, tela, camera_x=0):
        """Desenha a pose atual alinhada aos pés da hitbox."""
        if not self.em_movimento:
            quadro = (
                self.quadro_parado_esquerda
                if self.virado_para_esquerda
                else self.quadro_parado_direita
            )
        else:
            quadros = (
                self.quadros_esquerda
                if self.virado_para_esquerda
                else self.quadros_direita
            )
            quadro = quadros[self.indice_quadro]
        destino = quadro.get_rect(
            midbottom=(self.rect.centerx - int(camera_x), self.rect.bottom)
        )
        tela.blit(quadro, destino)
