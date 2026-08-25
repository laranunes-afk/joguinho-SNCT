import pygame

from recursos import carregar_imagem


class Checkpoint:
    """Marca um novo ponto de retorno para o personagem."""

    def __init__(self, x, y_chao):
        self.x = x
        self.y_chao = y_chao
        self.ativado = False

        # A área alta garante a ativação mesmo se o jogador estiver pulando.
        self.rect = pygame.Rect(
            x,
            0,
            50,
            y_chao
        )

        self.area_livre = pygame.Rect(
            x - 150,
            0,
            350,
            y_chao
        )

        self.posicao_retorno = x + 80
        imagem_original = carregar_imagem(
            "Checkpoint.png",
            fundo_transparente=True
        )
        limites = pygame.mask.from_surface(
            imagem_original
        ).get_bounding_rects()
        area_bandeira = limites[0].unionall(limites)
        imagem_recortada = imagem_original.subsurface(area_bandeira).copy()
        self.imagem = pygame.transform.scale(imagem_recortada, (75, 115))

    def foi_alcancado(self, personagem):
        return (
            not self.ativado
            and self.rect.colliderect(personagem.rect)
        )

    def ativar(self):
        self.ativado = True

    def desenhar(self, tela, camera_x, largura_tela):
        x_na_tela = int(self.x - camera_x)

        if x_na_tela < -80 or x_na_tela > largura_tela + 80:
            return

        rect_imagem = self.imagem.get_rect(
            midbottom=(x_na_tela + 25, self.y_chao)
        )
        tela.blit(self.imagem, rect_imagem)

        if self.ativado:
            pygame.draw.circle(
                tela,
                (50, 200, 90),
                (rect_imagem.centerx, rect_imagem.top + 12),
                10
            )
