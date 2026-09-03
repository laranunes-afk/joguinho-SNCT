import pygame

from cenario import esta_visivel
from recursos import carregar_imagem_recortada


LARGURA_ATIVACAO = 50
MARGEM_AREA_ESQUERDA = 150
LARGURA_AREA_PROTEGIDA = 350
DESLOCAMENTO_RETORNO = 80
MARGEM_VISIBILIDADE = 80
TAMANHO_BANDEIRA = (75, 115)


class Checkpoint:
    """Marca um novo ponto de retorno para o personagem."""

    _imagens = {}

    def __init__(self, x, y_chao):
        """Cria um checkpoint inativo na posição informada."""
        self.x = x
        self.y_chao = y_chao
        self.ativado = False

        # A área alta permite ativar a bandeira mesmo durante um pulo.
        self.rect = pygame.Rect(x, 0, LARGURA_ATIVACAO, y_chao)
        self.area_livre = pygame.Rect(
            x - MARGEM_AREA_ESQUERDA,
            0,
            LARGURA_AREA_PROTEGIDA,
            y_chao,
        )
        self.posicao_retorno = x + DESLOCAMENTO_RETORNO
        self.imagem_inativa = self._carregar_bandeira("Checkpoint.png")
        self.imagem_ativa = self._carregar_bandeira("CheckPoint-Verde.png")

    @classmethod
    def _carregar_bandeira(cls, nome_arquivo):
        """Carrega cada estado da bandeira somente uma vez."""
        if nome_arquivo not in cls._imagens:
            cls._imagens[nome_arquivo] = carregar_imagem_recortada(
                nome_arquivo,
                TAMANHO_BANDEIRA,
            )
        return cls._imagens[nome_arquivo]

    def foi_alcancado(self, personagem):
        """Informa se a personagem alcançou este checkpoint pela primeira vez."""
        return not self.ativado and self.rect.colliderect(personagem.rect)

    def ativar(self):
        """Marca o checkpoint como respondido e ativo."""
        self.ativado = True

    def desenhar(self, tela, camera_x, largura_tela):
        """Desenha a bandeira quando ela estiver dentro da área visível."""
        if not esta_visivel(
            self.rect,
            camera_x,
            largura_tela,
            MARGEM_VISIBILIDADE,
        ):
            return

        imagem = self.imagem_ativa if self.ativado else self.imagem_inativa
        rect_imagem = imagem.get_rect(
            midbottom=(
                self.rect.centerx - int(camera_x),
                self.rect.bottom,
            )
        )
        tela.blit(imagem, rect_imagem)
